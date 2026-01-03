from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
import rasterio.coords
import trimesh
import trimesh.visual
from geopandas import GeoDataFrame
from PIL import Image
from rasterio.crs import CRS
from rasterio.transform import Affine
from scipy.interpolate import RegularGridInterpolator
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
import fast_simplification
import mapbox_earcut

from .colors import (
    DefaultHeightmapColorAlgorithm,
    HeightmapColorAlgorithm,
    TextureContext,
)
from .dem import DemData
from .utils import StopWatch

if TYPE_CHECKING:
    from .glb import GlbLayer


@dataclass
class HeightmapConfig:
    """Configuration for heightmap GLB generation."""

    texture_size: int | None = 256
    """Size of the texture (width and height). If None, uses mesh resolution."""

    mesh_size: int | None = 1024
    """Size of the mesh grid (width and height). If None, uses DEM resolution."""

    height_scale: float = 0.5
    """Scale factor for the height (Y axis). Default 0.5 for 2x2 meter base."""

    x_size: float = 2.0
    """Size of the mesh in the X (east-west) direction in meters."""

    z_size: float = 2.0
    """Size of the mesh in the Z (north-south) direction in meters."""

    simplify_ratio: float | None = None
    """Target ratio for mesh simplification (0.0-1.0). None disables simplification."""

    color_algorithm: HeightmapColorAlgorithm = field(
        default_factory=DefaultHeightmapColorAlgorithm
    )
    """Algorithm for generating texture colors. Defaults to elevation-based coloring."""


@dataclass
class DemCache:
    """Cached DEM data and computed values for layer generation.
    NOTE: This class shouldn't be used outside of this file, threat it as opaque.
    """

    # From DEM metadata
    bounds: rasterio.coords.BoundingBox
    crs: CRS | None
    transform: Affine | None

    # Elevation data
    elevation: np.ndarray
    rows: int
    cols: int
    min_elev: float
    max_elev: float
    elev_range: float
    valid_mask: np.ndarray

    # Scale factors
    x_size: float
    z_size: float
    height_scale: float
    geo_width: float
    geo_height: float
    x_scale: float
    z_scale: float
    mesh_height_scale: float
    pixel_size_x: float
    pixel_size_y: float

    # Interpolators
    elevation_interpolator: RegularGridInterpolator
    validity_interpolator: RegularGridInterpolator

    def geo_to_mesh_x(self, geo_x: np.ndarray | float) -> np.ndarray | float:
        """Convert geographic X to mesh X coordinate."""
        return (self.bounds.left - geo_x) * self.x_scale + self.x_size / 2

    def geo_to_mesh_z(self, geo_y: np.ndarray | float) -> np.ndarray | float:
        """Convert geographic Y to mesh Z coordinate."""
        return self.z_size / 2 - (self.bounds.top - geo_y) * self.z_scale

    def elevation_to_mesh_y(self, elevation: np.ndarray | float) -> np.ndarray | float:
        """Convert real-world elevation to mesh Y coordinate."""
        return (elevation - self.min_elev) * self.mesh_height_scale

    def sample_elevation(self, geo_points: np.ndarray) -> np.ndarray:
        """Sample elevation at geographic points (x, y)."""
        sample_points = np.column_stack([geo_points[:, 1], geo_points[:, 0]])
        return self.elevation_interpolator(sample_points)

    def sample_validity(self, geo_points: np.ndarray) -> np.ndarray:
        """Check if points are over valid elevation data."""
        sample_points = np.column_stack([geo_points[:, 1], geo_points[:, 0]])
        return self.validity_interpolator(sample_points) > 0.5


def prepare_dem(dem: DemData, config: HeightmapConfig) -> DemCache:
    """Prepare cached DEM data for layer generation.

    Args:
        dem: DEM elevation data
        config: Heightmap configuration with size and scale settings

    Returns:
        DemCache with precomputed values and interpolators
    """
    if dem.elevation is None or dem.metadata is None:
        raise ValueError("DemData has no elevation data or metadata")

    if dem.metadata.bounds is None:
        raise ValueError("DemData has no bounds")

    bounds = dem.metadata.bounds
    elevation = dem.elevation

    # Dimensions
    rows, cols = elevation.shape
    geo_width = bounds.right - bounds.left
    geo_height = bounds.top - bounds.bottom

    # Scale factors
    x_scale = config.x_size / geo_width
    z_scale = config.z_size / geo_height

    # Elevation stats
    min_elev = float(np.nanmin(elevation))
    max_elev = float(np.nanmax(elevation))
    elev_range = max_elev - min_elev if max_elev != min_elev else 1.0
    mesh_height_scale = config.height_scale / elev_range

    # Valid mask
    valid_mask = ~np.isnan(elevation)

    # Pixel sizes
    pixel_size_x = geo_width / cols
    pixel_size_y = geo_height / rows

    # Create interpolators
    row_coords = np.linspace(bounds.top, bounds.bottom, rows)
    col_coords = np.linspace(bounds.left, bounds.right, cols)
    elev_filled = np.where(valid_mask, elevation, min_elev)

    elevation_interpolator = RegularGridInterpolator(
        (row_coords, col_coords),
        elev_filled,
        method='linear',
        bounds_error=False,
        fill_value=min_elev,
    )

    validity_interpolator = RegularGridInterpolator(
        (row_coords, col_coords),
        valid_mask.astype(np.float32),
        method='nearest',
        bounds_error=False,
        fill_value=0.0,
    )

    return DemCache(
        bounds=bounds,
        crs=dem.metadata.crs,
        transform=dem.metadata.transform,
        elevation=elevation,
        rows=rows,
        cols=cols,
        min_elev=min_elev,
        max_elev=max_elev,
        elev_range=elev_range,
        valid_mask=valid_mask,
        x_size=config.x_size,
        z_size=config.z_size,
        height_scale=config.height_scale,
        geo_width=geo_width,
        geo_height=geo_height,
        x_scale=x_scale,
        z_scale=z_scale,
        mesh_height_scale=mesh_height_scale,
        pixel_size_x=pixel_size_x,
        pixel_size_y=pixel_size_y,
        elevation_interpolator=elevation_interpolator,
        validity_interpolator=validity_interpolator,
    )


def create_dem_heightmap_layer(
    cache: DemCache, config: HeightmapConfig | None = None
) -> GlbLayer:
    """Create a GlbLayer with a colored heightmap mesh from DEM data.

    The mesh is centered at origin (0, 0, 0).
    Height is indicated by a color texture using a terrain colormap.

    Args:
        cache: Prepared DEM cache from prepare_dem()
        config: Optional configuration for texture, mesh size, simplification, and colors
    """
    from .glb import GlbLayer

    if config is None:
        config = HeightmapConfig()

    sw_total = StopWatch()
    sw_setup = StopWatch()

    elevation = cache.elevation.copy()

    # Resample elevation to mesh_size if specified
    if config.mesh_size is not None:
        mesh_rows, mesh_cols = config.mesh_size, config.mesh_size
        elev_image = Image.fromarray(elevation, mode='F')
        elev_image = elev_image.resize((mesh_cols, mesh_rows), Image.Resampling.BILINEAR)
        elevation = np.array(elev_image)

    rows, cols = elevation.shape

    # Create grid coordinates centered at origin
    x = np.linspace(cache.x_size / 2, -cache.x_size / 2, cols)
    z = np.linspace(cache.z_size / 2, -cache.z_size / 2, rows)
    xx, zz = np.meshgrid(x, z)

    # Normalize heights for Y coordinate (up axis)
    valid_mask = ~np.isnan(elevation)
    normalized = (elevation - cache.min_elev) / cache.elev_range
    normalized = np.where(valid_mask, normalized, 0.0)

    # Scale Y to reasonable height
    yy = normalized * cache.height_scale

    # Create vertices array (rows * cols, 3)
    vertices = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], axis=1)

    print(f'sw_setup={sw_setup}')

    sw_faces = StopWatch()

    # Create faces (triangles) for the grid, skipping cells with nodata
    i_idx, j_idx = np.meshgrid(np.arange(rows - 1), np.arange(cols - 1), indexing='ij')
    i_flat = i_idx.ravel()
    j_flat = j_idx.ravel()

    cell_valid = (valid_mask[:-1, :-1] & valid_mask[:-1, 1:] &
                  valid_mask[1:, :-1] & valid_mask[1:, 1:]).ravel()

    v0 = i_flat * cols + j_flat
    v1 = i_flat * cols + (j_flat + 1)
    v2 = (i_flat + 1) * cols + j_flat
    v3 = (i_flat + 1) * cols + (j_flat + 1)

    v0_valid = v0[cell_valid]
    v1_valid = v1[cell_valid]
    v2_valid = v2[cell_valid]
    v3_valid = v3[cell_valid]

    tri1 = np.stack([v0_valid, v2_valid, v1_valid], axis=1)
    tri2 = np.stack([v1_valid, v2_valid, v3_valid], axis=1)
    faces = np.vstack([tri1, tri2]).astype(np.int32)

    print(f'sw_faces={sw_faces}')

    # Generate UV coordinates for texture mapping
    sw_uv = StopWatch()
    u = np.linspace(0, 1, cols)
    v = np.linspace(1, 0, rows)
    uu, vv = np.meshgrid(u, v)
    uv_coords = np.stack([uu.ravel(), vv.ravel()], axis=1)
    print(f'sw_uv={sw_uv}')

    # Create texture image based on height (terrain colormap)
    sw_texture = StopWatch()

    if config.texture_size is not None:
        tex_rows, tex_cols = config.texture_size, config.texture_size
        norm_image = Image.fromarray((normalized * 255).astype(np.uint8), mode='L')
        norm_image = norm_image.resize((tex_cols, tex_rows), Image.Resampling.BILINEAR)
        tex_normalized = np.array(norm_image).astype(np.float32) / 255.0
    else:
        tex_rows, tex_cols = rows, cols
        tex_normalized = normalized

    # Create texture context for the color algorithm
    context = TextureContext(
        tex_rows=tex_rows,
        tex_cols=tex_cols,
        min_elevation=cache.min_elev,
        max_elevation=cache.max_elev,
        bounds=cache.bounds,
        crs=cache.crs,
        transform=cache.transform,
    )

    # Generate texture using the color algorithm
    config.color_algorithm.prepare(context)
    texture_colors = config.color_algorithm.generate_texture(tex_normalized)
    texture_image = Image.fromarray(texture_colors, mode='RGB')
    print(f'sw_texture={sw_texture}')

    # Create mesh with texture
    sw_mesh = StopWatch()
    material = trimesh.visual.material.PBRMaterial(
        baseColorTexture=texture_image,
        baseColorFactor=[1.0, 1.0, 1.0, 1.0],
        metallicFactor=0.0,
        roughnessFactor=1.0,
    )
    visuals = trimesh.visual.TextureVisuals(uv=uv_coords, material=material)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, visual=visuals, process=False)
    print(f'sw_mesh={sw_mesh}')

    # Simplify mesh if requested
    if config.simplify_ratio is not None:
        sw_simplify = StopWatch()
        original_faces = len(mesh.faces)
        simplified_verts, simplified_faces = fast_simplification.simplify(
            mesh.vertices,
            mesh.faces,
            target_reduction=1.0 - config.simplify_ratio,
        )
        from scipy.spatial import cKDTree
        tree = cKDTree(vertices)
        _, indices = tree.query(simplified_verts)
        simplified_uv = uv_coords[indices]
        visuals = trimesh.visual.TextureVisuals(uv=simplified_uv, material=material)
        mesh = trimesh.Trimesh(vertices=simplified_verts, faces=simplified_faces, visual=visuals, process=False)
        print(f'sw_simplify={sw_simplify} ({original_faces} -> {len(mesh.faces)} faces)')

    print(f'sw_total={sw_total}')

    return GlbLayer(name="heightmap", mesh=mesh)


def create_solid_dem_layer(
    cache: DemCache, config: HeightmapConfig | None = None, base_height: float = 0.0
) -> GlbLayer:
    """Create a GlbLayer with a solid (watertight) mesh from DEM data.

    Creates a closed solid suitable for 3D printing with:
    - Top surface following the terrain
    - Flat bottom surface
    - Side walls connecting top to bottom

    The mesh is centered at origin (0, 0, 0).

    Args:
        cache: Prepared DEM cache from prepare_dem()
        config: Optional configuration for texture, mesh size, simplification, and colors
        base_height: Y coordinate for the bottom surface (default 0.0)

    Returns:
        GlbLayer named "solid" with watertight mesh
    """
    from .glb import GlbLayer

    if config is None:
        config = HeightmapConfig()

    elevation = cache.elevation.copy()

    # Resample elevation to mesh_size if specified
    if config.mesh_size is not None:
        mesh_rows, mesh_cols = config.mesh_size, config.mesh_size
        elev_image = Image.fromarray(elevation, mode='F')
        elev_image = elev_image.resize((mesh_cols, mesh_rows), Image.Resampling.BILINEAR)
        elevation = np.array(elev_image)

    rows, cols = elevation.shape

    # Create grid coordinates centered at origin
    x = np.linspace(cache.x_size / 2, -cache.x_size / 2, cols)
    z = np.linspace(cache.z_size / 2, -cache.z_size / 2, rows)
    xx, zz = np.meshgrid(x, z)

    # Normalize heights for Y coordinate (up axis)
    valid_mask = ~np.isnan(elevation)
    normalized = (elevation - cache.min_elev) / cache.elev_range
    normalized = np.where(valid_mask, normalized, 0.0)

    # Scale Y to reasonable height
    yy_top = normalized * cache.height_scale

    # Create top vertices (terrain surface)
    top_vertices = np.stack([xx.ravel(), yy_top.ravel(), zz.ravel()], axis=1)

    # Create bottom vertices (flat base)
    yy_bottom = np.full_like(yy_top, base_height)
    bottom_vertices = np.stack([xx.ravel(), yy_bottom.ravel(), zz.ravel()], axis=1)

    # Combine vertices: top surface, then bottom surface
    n_grid_verts = rows * cols
    vertices = np.vstack([top_vertices, bottom_vertices]).astype(np.float32)

    # Create top faces (same as heightmap)
    i_idx, j_idx = np.meshgrid(np.arange(rows - 1), np.arange(cols - 1), indexing='ij')
    i_flat = i_idx.ravel()
    j_flat = j_idx.ravel()

    cell_valid = (valid_mask[:-1, :-1] & valid_mask[:-1, 1:] &
                  valid_mask[1:, :-1] & valid_mask[1:, 1:]).ravel()

    v0 = i_flat * cols + j_flat
    v1 = i_flat * cols + (j_flat + 1)
    v2 = (i_flat + 1) * cols + j_flat
    v3 = (i_flat + 1) * cols + (j_flat + 1)

    v0_valid = v0[cell_valid]
    v1_valid = v1[cell_valid]
    v2_valid = v2[cell_valid]
    v3_valid = v3[cell_valid]

    # Top surface faces (terrain)
    top_tri1 = np.stack([v0_valid, v2_valid, v1_valid], axis=1)
    top_tri2 = np.stack([v1_valid, v2_valid, v3_valid], axis=1)
    top_faces = np.vstack([top_tri1, top_tri2])

    # Bottom surface faces (reversed winding for outward normals)
    bottom_offset = n_grid_verts
    bottom_tri1 = np.stack([v0_valid + bottom_offset, v1_valid + bottom_offset, v2_valid + bottom_offset], axis=1)
    bottom_tri2 = np.stack([v1_valid + bottom_offset, v3_valid + bottom_offset, v2_valid + bottom_offset], axis=1)
    bottom_faces = np.vstack([bottom_tri1, bottom_tri2])

    # Side wall faces - connect perimeter of top to bottom
    # Top edge (row 0): z = z_size/2
    top_edge_indices = np.arange(cols)
    # Bottom edge (row = rows-1): z = -z_size/2
    bottom_edge_indices = np.arange((rows - 1) * cols, rows * cols)
    # Left edge (col 0): x = x_size/2
    left_edge_indices = np.arange(0, rows * cols, cols)
    # Right edge (col = cols-1): x = -x_size/2
    right_edge_indices = np.arange(cols - 1, rows * cols, cols)

    side_faces = []

    # Top edge wall (row 0) - faces point outward (+Z)
    for i in range(cols - 1):
        t0, t1 = top_edge_indices[i], top_edge_indices[i + 1]
        b0, b1 = t0 + bottom_offset, t1 + bottom_offset
        side_faces.append([t0, t1, b0])
        side_faces.append([b0, t1, b1])

    # Bottom edge wall (row = rows-1) - faces point outward (-Z)
    for i in range(cols - 1):
        t0, t1 = bottom_edge_indices[i], bottom_edge_indices[i + 1]
        b0, b1 = t0 + bottom_offset, t1 + bottom_offset
        side_faces.append([t0, b0, t1])
        side_faces.append([b0, b1, t1])

    # Left edge wall (col 0) - faces point outward (+X)
    for i in range(rows - 1):
        t0, t1 = left_edge_indices[i], left_edge_indices[i + 1]
        b0, b1 = t0 + bottom_offset, t1 + bottom_offset
        side_faces.append([t0, b0, t1])
        side_faces.append([b0, b1, t1])

    # Right edge wall (col = cols-1) - faces point outward (-X)
    for i in range(rows - 1):
        t0, t1 = right_edge_indices[i], right_edge_indices[i + 1]
        b0, b1 = t0 + bottom_offset, t1 + bottom_offset
        side_faces.append([t0, t1, b0])
        side_faces.append([b0, t1, b1])

    side_faces = np.array(side_faces, dtype=np.int32)

    # Combine all faces
    faces = np.vstack([top_faces, bottom_faces, side_faces]).astype(np.int32)

    # Generate UV coordinates for texture mapping (top surface only, bottom gets same UVs)
    u = np.linspace(0, 1, cols)
    v = np.linspace(1, 0, rows)
    uu, vv = np.meshgrid(u, v)
    uv_top = np.stack([uu.ravel(), vv.ravel()], axis=1)
    uv_coords = np.vstack([uv_top, uv_top]).astype(np.float32)  # Same UVs for bottom

    # Create texture
    if config.texture_size is not None:
        tex_rows, tex_cols = config.texture_size, config.texture_size
        norm_image = Image.fromarray((normalized * 255).astype(np.uint8), mode='L')
        norm_image = norm_image.resize((tex_cols, tex_rows), Image.Resampling.BILINEAR)
        tex_normalized = np.array(norm_image).astype(np.float32) / 255.0
    else:
        tex_rows, tex_cols = rows, cols
        tex_normalized = normalized

    context = TextureContext(
        tex_rows=tex_rows,
        tex_cols=tex_cols,
        min_elevation=cache.min_elev,
        max_elevation=cache.max_elev,
        bounds=cache.bounds,
        crs=cache.crs,
        transform=cache.transform,
    )

    config.color_algorithm.prepare(context)
    texture_colors = config.color_algorithm.generate_texture(tex_normalized)
    texture_image = Image.fromarray(texture_colors, mode='RGB')

    material = trimesh.visual.material.PBRMaterial(
        baseColorTexture=texture_image,
        baseColorFactor=[1.0, 1.0, 1.0, 1.0],
        metallicFactor=0.0,
        roughnessFactor=1.0,
    )
    visuals = trimesh.visual.TextureVisuals(uv=uv_coords, material=material)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, visual=visuals, process=False)

    # Simplify mesh if requested
    if config.simplify_ratio is not None:
        original_faces = len(mesh.faces)
        simplified_verts, simplified_faces = fast_simplification.simplify(
            mesh.vertices,
            mesh.faces,
            target_reduction=1.0 - config.simplify_ratio,
        )
        from scipy.spatial import cKDTree
        tree = cKDTree(vertices)
        _, indices = tree.query(simplified_verts)
        simplified_uv = uv_coords[indices]
        visuals = trimesh.visual.TextureVisuals(uv=simplified_uv, material=material)
        mesh = trimesh.Trimesh(
            vertices=simplified_verts, faces=simplified_faces, visual=visuals, process=False
        )

    return GlbLayer(name="solid", mesh=mesh)


@dataclass
class RoadConfig:
    """Configuration for road appearance."""

    road_width: float = 5.0
    """Road width in real-world meters."""

    road_color: tuple[int, int, int] = (255, 0, 0)
    """RGB color of the road surface."""

    thickness: float | None = None
    """Road thickness in real-world meters. If None, roads are flat."""


def _default_road_id_config() -> dict[int, RoadConfig]:
    """Default road configurations by objekttypnr."""
    return {
        1803: RoadConfig(road_color=(255, 0, 0)),      # Red

        #1804: RoadConfig(road_color=(0, 255, 0)),      # Green
        1804: RoadConfig(road_color=(255, 255, 0)),

        1805: RoadConfig(road_color=(0, 0, 255)),      # Blue
        1806: RoadConfig(road_color=(255, 255, 0)),    # Yellow
        1807: RoadConfig(road_color=(255, 0, 255)),    # Magenta

        # 1808 Landsväg
        #1808: RoadConfig(road_color=(0, 255, 255)),    # Cyan
        1808: RoadConfig(road_width=20, road_color=(0, 255, 0)),

        1809: RoadConfig(road_color=(255, 128, 0)),    # Orange
        1810: RoadConfig(road_color=(128, 0, 255)),    # Purple
        1811: RoadConfig(road_color=(0, 128, 0)),      # Dark green
    }


@dataclass
class DrapedRoadConfig:
    """Configuration for draped road layer."""

    default_road: RoadConfig = field(default_factory=RoadConfig)
    """Default road appearance for unknown objekttypnr values."""

    road_id_config: dict[int, RoadConfig] = field(default_factory=_default_road_id_config)
    """Road configurations by objekttypnr value."""

    road_id_column: str = "objekttypnr"
    """Column name in GeoDataFrame containing road type identifiers."""

    height_delta: float = 2
    """Height offset above the terrain in real-world meters."""

    sample_distance: float | None = None
    """Distance between elevation samples along roads in real-world meters.
    If None, uses DEM pixel size. Smaller values = tighter terrain following."""


def create_dem_road_layer(
    cache: DemCache,
    roads: GeoDataFrame,
    road_config: DrapedRoadConfig,
) -> GlbLayer:
    """Create a GlbLayer with roads draped over the terrain.

    Roads follow the terrain elevation plus a height offset.
    Roads are grouped by road_id_column into child layers.

    Args:
        cache: Prepared DEM cache from prepare_dem()
        roads: GeoDataFrame containing road geometries
        road_config: Road layer configuration

    Returns:
        GlbLayer "roads" with child layers per road type plus a 'default' child
    """
    from .glb import GlbLayer

    # Scale the height_delta from real-world to mesh coordinates
    scaled_height_delta = road_config.height_delta * cache.mesh_height_scale

    # Calculate sample distance (default to DEM pixel size)
    sample_distance = road_config.sample_distance or min(cache.pixel_size_x, cache.pixel_size_y)

    def subdivide_line(coords: np.ndarray) -> np.ndarray:
        """Subdivide line segments to sample elevation more frequently."""
        if len(coords) < 2:
            return coords

        # Vectorized subdivision
        segments = coords[1:] - coords[:-1]
        lengths = np.linalg.norm(segments, axis=1)
        n_subdivs = np.maximum(1, np.ceil(lengths / sample_distance).astype(int))

        # Preallocate result array
        total_points = int(np.sum(n_subdivs)) + 1
        result = np.empty((total_points, 2), dtype=coords.dtype)

        idx = 0
        for i in range(len(coords) - 1):
            n = n_subdivs[i]
            if n == 1:
                result[idx] = coords[i]
                idx += 1
            else:
                t = np.linspace(0, 1, n, endpoint=False).reshape(-1, 1)
                result[idx:idx + n] = coords[i] + t * segments[i]
                idx += n
        result[idx] = coords[-1]
        return result[:idx + 1]

    def build_road_mesh(
        road_geometries: list,
        road_cfg: RoadConfig,
    ) -> trimesh.Trimesh | None:
        """Build a mesh for a set of road geometries."""
        scaled_road_width = road_cfg.road_width * cache.x_scale / 2

        all_vertices = []
        all_faces = []
        vertex_offset = 0

        for geom in road_geometries:
            if isinstance(geom, MultiLineString):
                lines = list(geom.geoms)
            elif isinstance(geom, LineString):
                lines = [geom]
            else:
                continue

            for line in lines:
                coords = np.array(line.coords)
                if len(coords) < 2:
                    continue

                coords = subdivide_line(coords)

                elevations = cache.sample_elevation(coords)
                point_valid = cache.sample_validity(coords)

                mesh_x = cache.geo_to_mesh_x(coords[:, 0])
                mesh_z = cache.geo_to_mesh_z(coords[:, 1])
                mesh_y = cache.elevation_to_mesh_y(elevations) + scaled_height_delta

                tangent = np.zeros_like(coords)
                tangent[:-1] = coords[1:] - coords[:-1]
                tangent[-1] = tangent[-2]

                tangent_mesh = np.column_stack([
                    -tangent[:, 0] * cache.x_scale,
                    -tangent[:, 1] * cache.z_scale,
                ])
                lengths = np.linalg.norm(tangent_mesh, axis=1, keepdims=True)
                lengths = np.where(lengths == 0, 1, lengths)
                tangent_mesh = tangent_mesh / lengths

                perp_x = -tangent_mesh[:, 1]
                perp_z = tangent_mesh[:, 0]

                left_x = mesh_x + perp_x * scaled_road_width
                left_z = mesh_z + perp_z * scaled_road_width
                right_x = mesh_x - perp_x * scaled_road_width
                right_z = mesh_z - perp_z * scaled_road_width

                n_points = len(coords)
                segment_valid = point_valid[:-1] & point_valid[1:]
                valid_indices = np.where(segment_valid)[0]

                if road_cfg.thickness is not None:
                    # 3D road with thickness: 4 vertices per point
                    scaled_thickness = road_cfg.thickness * cache.mesh_height_scale
                    mesh_y_bottom = mesh_y - scaled_thickness

                    vertices = np.zeros((n_points * 4, 3), dtype=np.float32)
                    # Top left (index 0, 4, 8, ...)
                    vertices[0::4, 0] = left_x
                    vertices[0::4, 1] = mesh_y
                    vertices[0::4, 2] = left_z
                    # Top right (index 1, 5, 9, ...)
                    vertices[1::4, 0] = right_x
                    vertices[1::4, 1] = mesh_y
                    vertices[1::4, 2] = right_z
                    # Bottom left (index 2, 6, 10, ...)
                    vertices[2::4, 0] = left_x
                    vertices[2::4, 1] = mesh_y_bottom
                    vertices[2::4, 2] = left_z
                    # Bottom right (index 3, 7, 11, ...)
                    vertices[3::4, 0] = right_x
                    vertices[3::4, 1] = mesh_y_bottom
                    vertices[3::4, 2] = right_z

                    if len(valid_indices) > 0:
                        # Vertex indices for segment i: tl=i*4, tr=i*4+1, bl=i*4+2, br=i*4+3
                        tl0 = vertex_offset + valid_indices * 4
                        tr0 = tl0 + 1
                        bl0 = tl0 + 2
                        br0 = tl0 + 3
                        tl1 = tl0 + 4
                        tr1 = tl0 + 5
                        bl1 = tl0 + 6
                        br1 = tl0 + 7

                        # Top surface
                        top_faces = np.column_stack([
                            np.column_stack([tl0, tl1, tr0]),
                            np.column_stack([tr0, tl1, tr1]),
                        ]).reshape(-1, 3)

                        # Bottom surface (reversed winding)
                        bottom_faces = np.column_stack([
                            np.column_stack([bl0, br0, bl1]),
                            np.column_stack([br0, br1, bl1]),
                        ]).reshape(-1, 3)

                        # Left wall (tl0 -> bl0 -> tl1 -> bl1)
                        left_faces = np.column_stack([
                            np.column_stack([tl0, bl0, tl1]),
                            np.column_stack([tl1, bl0, bl1]),
                        ]).reshape(-1, 3)

                        # Right wall (tr0 -> tr1 -> br0 -> br1)
                        right_faces = np.column_stack([
                            np.column_stack([tr0, tr1, br0]),
                            np.column_stack([tr1, br1, br0]),
                        ]).reshape(-1, 3)

                        faces = np.vstack([top_faces, bottom_faces, left_faces, right_faces])
                        all_faces.append(faces)
                else:
                    # Flat road: 2 vertices per point
                    vertices = np.zeros((n_points * 2, 3), dtype=np.float32)
                    vertices[0::2, 0] = left_x
                    vertices[0::2, 1] = mesh_y
                    vertices[0::2, 2] = left_z
                    vertices[1::2, 0] = right_x
                    vertices[1::2, 1] = mesh_y
                    vertices[1::2, 2] = right_z

                    if len(valid_indices) > 0:
                        v0 = vertex_offset + valid_indices * 2
                        v1 = v0 + 1
                        v2 = v0 + 2
                        v3 = v0 + 3

                        # 4 faces per segment (double-sided)
                        faces = np.column_stack([
                            np.column_stack([v0, v2, v1]),
                            np.column_stack([v1, v2, v3]),
                            np.column_stack([v0, v1, v2]),
                            np.column_stack([v1, v3, v2]),
                        ]).reshape(-1, 3)

                        all_faces.append(faces)

                all_vertices.append(vertices)
                vertex_offset += len(vertices)

        if not all_vertices:
            return None

        vertices = np.vstack(all_vertices)
        faces = np.vstack(all_faces) if all_faces else np.empty((0, 3), dtype=np.int32)

        # Use PBR material for Blender compatibility
        r, g, b = road_cfg.road_color
        material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[r / 255, g / 255, b / 255, 1.0],
            metallicFactor=0.0,
            roughnessFactor=1.0,
        )
        visuals = trimesh.visual.TextureVisuals(material=material)

        mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            visual=visuals,
            process=False,
        )
        return mesh

    # Reproject roads to DEM CRS if needed
    if cache.crs is not None and roads.crs != cache.crs:
        roads = roads.to_crs(cache.crs)

    # Clip roads to DEM bounds
    from shapely.geometry import box
    bounds_box = box(cache.bounds.left, cache.bounds.bottom, cache.bounds.right, cache.bounds.top)
    roads = roads.clip(bounds_box)

    # Group roads by road type
    id_column = road_config.road_id_column
    has_id_column = id_column in roads.columns

    # Collect geometries by road type using vectorized groupby
    geometries_by_type: dict[int | str, list] = {road_id: [] for road_id in road_config.road_id_config}
    geometries_by_type["default"] = []

    if has_id_column:
        configured_ids = set(road_config.road_id_config.keys())
        for road_id, group in roads.groupby(id_column):
            geoms = group.geometry.tolist()
            if road_id in configured_ids:
                geometries_by_type[road_id] = geoms
            else:
                geometries_by_type["default"].extend(geoms)
    else:
        geometries_by_type["default"] = roads.geometry.tolist()

    # Build parent layer with children
    parent = GlbLayer(name="roads")

    # Create child layer for each configured road type
    for road_id, road_cfg in road_config.road_id_config.items():
        geoms = geometries_by_type.get(road_id, [])
        if geoms:
            mesh = build_road_mesh(geoms, road_cfg)
            if mesh is not None:
                parent.add_child(GlbLayer(name=str(road_id), mesh=mesh))

    # Create default child layer
    default_geoms = geometries_by_type.get("default", [])
    if default_geoms:
        mesh = build_road_mesh(default_geoms, road_config.default_road)
        if mesh is not None:
            parent.add_child(GlbLayer(name="default", mesh=mesh))

    return parent


@dataclass
class BuildingOutlineLayer:
    """Configuration for a building outline type."""

    name: str
    """Display name for this building type."""

    width: float = 1.0
    """Outline width in real-world meters."""

    color: tuple[int, int, int] = (256, 0, 0)
    """RGB color of the outline."""


def _default_building_outline_config() -> dict[int, BuildingOutlineLayer]:
    """Default building outline configurations by objekttypnr."""
    return {
        2061: BuildingOutlineLayer(name="Bostad", color=(255, 200, 100)),
        2062: BuildingOutlineLayer(name="Industri", color=(150, 150, 150)),
        2063: BuildingOutlineLayer(name="Samhällsfunktion", color=(100, 150, 255)),
        2064: BuildingOutlineLayer(name="Verksamhet", color=(200, 100, 200)),
        2065: BuildingOutlineLayer(name="Ekonomibyggnad", color=(139, 90, 43)),
        2066: BuildingOutlineLayer(name="Komplementbyggnad", color=(180, 180, 100)),
        2067: BuildingOutlineLayer(name="Övrig byggnad", color=(128, 128, 128)),
    }


@dataclass
class BuildingOutlineConfig:
    """Configuration for building outline layer."""

    default_building: BuildingOutlineLayer = field(
        default_factory=lambda: BuildingOutlineLayer(name="default")
    )
    """Default building appearance for unknown objekttypnr values."""

    building_layers: dict[int, BuildingOutlineLayer] = field(
        default_factory=_default_building_outline_config
    )
    """Building configurations by objekttypnr value."""

    building_id_column: str = "objekttypnr"
    """Column name in GeoDataFrame containing building type identifiers."""

    height_delta: float = 2
    """Height offset above the terrain in real-world meters."""

    sample_distance: float | None = None
    """Distance between elevation samples along outlines in real-world meters.
    If None, uses DEM pixel size. Smaller values = tighter terrain following."""

    simplify_ratio: float | None = None
    """Target ratio for mesh simplification (0.0-1.0). None disables simplification.
    E.g., 0.5 reduces mesh to ~50% of original faces."""


def create_dem_building_outline_layer(
    cache: DemCache,
    buildings: GeoDataFrame,
    building_config: BuildingOutlineConfig,
) -> GlbLayer:
    """Create a GlbLayer with building outlines draped over the terrain.

    Building outlines follow the terrain elevation plus a height offset.
    Buildings are grouped by building_id_column into child layers.

    Args:
        cache: Prepared DEM cache from prepare_dem()
        buildings: GeoDataFrame containing building polygon geometries
        building_config: Building outline configuration

    Returns:
        GlbLayer "buildings" with child layers per building type plus a 'default' child
    """
    from .glb import GlbLayer

    # Scale the height_delta from real-world to mesh coordinates
    scaled_height_delta = building_config.height_delta * cache.mesh_height_scale

    # Calculate sample distance (default to DEM pixel size)
    sample_distance = building_config.sample_distance or min(cache.pixel_size_x, cache.pixel_size_y)

    def subdivide_line(coords: np.ndarray) -> np.ndarray:
        """Subdivide line segments to sample elevation more frequently."""
        if len(coords) < 2:
            return coords

        # Vectorized subdivision
        segments = coords[1:] - coords[:-1]
        lengths = np.linalg.norm(segments, axis=1)
        n_subdivs = np.maximum(1, np.ceil(lengths / sample_distance).astype(int))

        # Preallocate result array
        total_points = int(np.sum(n_subdivs)) + 1
        result = np.empty((total_points, 2), dtype=coords.dtype)

        idx = 0
        for i in range(len(coords) - 1):
            n = n_subdivs[i]
            if n == 1:
                result[idx] = coords[i]
                idx += 1
            else:
                t = np.linspace(0, 1, n, endpoint=False).reshape(-1, 1)
                result[idx:idx + n] = coords[i] + t * segments[i]
                idx += n
        result[idx] = coords[-1]
        return result[:idx + 1]

    def build_outline_mesh(
        building_geometries: list,
        outline_cfg: BuildingOutlineLayer,
    ) -> trimesh.Trimesh | None:
        """Build a mesh for a set of building outline geometries."""
        scaled_width = outline_cfg.width * cache.x_scale / 2

        all_vertices = []
        all_faces = []
        vertex_offset = 0

        for geom in building_geometries:
            # Extract polygon exteriors
            if isinstance(geom, MultiPolygon):
                polygons = list(geom.geoms)
            elif isinstance(geom, Polygon):
                polygons = [geom]
            else:
                continue

            for polygon in polygons:
                if polygon.is_empty:
                    continue

                # Get exterior ring coordinates (closed loop)
                coords = np.array(polygon.exterior.coords)
                if len(coords) < 3:
                    continue

                coords = subdivide_line(coords)

                elevations = cache.sample_elevation(coords)
                point_valid = cache.sample_validity(coords)

                mesh_x = cache.geo_to_mesh_x(coords[:, 0])
                mesh_z = cache.geo_to_mesh_z(coords[:, 1])
                mesh_y = cache.elevation_to_mesh_y(elevations) + scaled_height_delta

                tangent = np.zeros_like(coords)
                tangent[:-1] = coords[1:] - coords[:-1]
                tangent[-1] = tangent[-2]

                tangent_mesh = np.column_stack([
                    -tangent[:, 0] * cache.x_scale,
                    -tangent[:, 1] * cache.z_scale,
                ])
                lengths = np.linalg.norm(tangent_mesh, axis=1, keepdims=True)
                lengths = np.where(lengths == 0, 1, lengths)
                tangent_mesh = tangent_mesh / lengths

                perp_x = -tangent_mesh[:, 1]
                perp_z = tangent_mesh[:, 0]

                left_x = mesh_x + perp_x * scaled_width
                left_z = mesh_z + perp_z * scaled_width
                right_x = mesh_x - perp_x * scaled_width
                right_z = mesh_z - perp_z * scaled_width

                n_points = len(coords)
                vertices = np.zeros((n_points * 2, 3), dtype=np.float32)
                vertices[0::2, 0] = left_x
                vertices[0::2, 1] = mesh_y
                vertices[0::2, 2] = left_z
                vertices[1::2, 0] = right_x
                vertices[1::2, 1] = mesh_y
                vertices[1::2, 2] = right_z

                # Vectorized face generation
                segment_valid = point_valid[:-1] & point_valid[1:]
                valid_indices = np.where(segment_valid)[0]

                if len(valid_indices) > 0:
                    v0 = vertex_offset + valid_indices * 2
                    v1 = v0 + 1
                    v2 = v0 + 2
                    v3 = v0 + 3

                    # 4 faces per segment (double-sided)
                    faces = np.column_stack([
                        np.column_stack([v0, v2, v1]),
                        np.column_stack([v1, v2, v3]),
                        np.column_stack([v0, v1, v2]),
                        np.column_stack([v1, v3, v2]),
                    ]).reshape(-1, 3)

                    all_faces.append(faces)

                all_vertices.append(vertices)
                vertex_offset += len(vertices)

        if not all_vertices:
            return None

        vertices = np.vstack(all_vertices)
        faces = np.vstack(all_faces) if all_faces else np.empty((0, 3), dtype=np.int32)

        # Apply mesh simplification if configured
        if building_config.simplify_ratio is not None and len(faces) > 0:
            simplified_verts, simplified_faces = fast_simplification.simplify(
                vertices,
                faces.astype(np.int64),
                target_reduction=1.0 - building_config.simplify_ratio,
            )
            vertices = simplified_verts.astype(np.float32)
            faces = simplified_faces

        # Use PBR material for Blender compatibility
        r, g, b = outline_cfg.color
        material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[r / 255, g / 255, b / 255, 1.0],
            metallicFactor=0.0,
            roughnessFactor=1.0,
        )
        visuals = trimesh.visual.TextureVisuals(material=material)

        return trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            visual=visuals,
            process=False,
        )

    # Reproject buildings to DEM CRS if needed
    if cache.crs is not None and buildings.crs != cache.crs:
        buildings = buildings.to_crs(cache.crs)

    # Clip buildings to DEM bounds
    from shapely.geometry import box
    bounds_box = box(cache.bounds.left, cache.bounds.bottom, cache.bounds.right, cache.bounds.top)
    buildings = buildings.clip(bounds_box)

    # Group buildings by type using vectorized groupby
    id_column = building_config.building_id_column
    has_id_column = id_column in buildings.columns

    geometries_by_type: dict[int | str, list] = {bid: [] for bid in building_config.building_layers}
    geometries_by_type["default"] = []

    if has_id_column:
        configured_ids = set(building_config.building_layers.keys())
        for building_id, group in buildings.groupby(id_column):
            geoms = group.geometry.tolist()
            if building_id in configured_ids:
                geometries_by_type[building_id] = geoms
            else:
                geometries_by_type["default"].extend(geoms)
    else:
        geometries_by_type["default"] = buildings.geometry.tolist()

    # Build parent layer with children
    parent = GlbLayer(name="buildings_outline")

    # Create child layer for each configured building type
    for building_id, outline_cfg in building_config.building_layers.items():
        geoms = geometries_by_type.get(building_id, [])
        if geoms:
            mesh = build_outline_mesh(geoms, outline_cfg)
            if mesh is not None:
                parent.add_child(GlbLayer(name=f"{outline_cfg.name}_outline", mesh=mesh))

    # Create default child layer
    default_geoms = geometries_by_type.get("default", [])
    if default_geoms:
        mesh = build_outline_mesh(default_geoms, building_config.default_building)
        if mesh is not None:
            parent.add_child(GlbLayer(name="default_outline", mesh=mesh))

    return parent


@dataclass
class BuildingAutoHeightLayer:
    """Configuration for a 3D building type."""

    name: str
    """Display name for this building type."""

    height: float = 2.0
    """Building height in real-world meters."""

    color: tuple[int, int, int] = (128, 128, 128)
    """RGB color of the building."""


def _default_building_auto_height_config() -> dict[int, BuildingAutoHeightLayer]:
    """Default 3D building configurations by objekttypnr."""
    return {
        2061: BuildingAutoHeightLayer(name="Bostad", height=3.0, color=(255, 0, 0)),
        2062: BuildingAutoHeightLayer(name="Industri", height=8.0, color=(150, 150, 150)),
        2063: BuildingAutoHeightLayer(name="Samhällsfunktion", height=5.0, color=(0, 0, 255)),
        2064: BuildingAutoHeightLayer(name="Verksamhet", height=10.0, color=(200, 100, 200)),
        2065: BuildingAutoHeightLayer(name="Ekonomibyggnad", height=2.0, color=(139, 90, 43)),
        2066: BuildingAutoHeightLayer(name="Komplementbyggnad", height=2.0, color=(180, 180, 100)),
        2067: BuildingAutoHeightLayer(name="Övrig byggnad", height=1.0, color=(128, 128, 128)),
    }


@dataclass
class BuildingAutoHeightConfig:
    """Configuration for 3D building layer."""

    default_building: BuildingAutoHeightLayer = field(
        default_factory=lambda: BuildingAutoHeightLayer(name="default")
    )
    """Default building appearance for unknown objekttypnr values."""

    building_layers: dict[int, BuildingAutoHeightLayer] = field(
        default_factory=_default_building_auto_height_config
    )
    """Building configurations by objekttypnr value."""

    building_id_column: str = "objekttypnr"
    """Column name in GeoDataFrame containing building type identifiers."""

    height_delta: float = 0
    """Height offset above the terrain center in real-world meters."""


def create_dem_buildings_auto_height_layer(
    cache: DemCache,
    buildings: GeoDataFrame,
    building_config: BuildingAutoHeightConfig,
) -> GlbLayer:
    """Create a GlbLayer with 3D building volumes.

    Buildings use the center point elevation as base, not draped onto terrain.
    Buildings are grouped by building_id_column into child layers.

    Args:
        cache: Prepared DEM cache from prepare_dem()
        buildings: GeoDataFrame containing building polygon geometries
        building_config: Building configuration

    Returns:
        GlbLayer "buildings_3d" with child layers per building type plus a 'default' child
    """
    from .glb import GlbLayer

    # Scale the height_delta from real-world to mesh coordinates
    scaled_height_delta = building_config.height_delta * cache.mesh_height_scale

    def build_3d_mesh(
        building_geometries: list,
        layer_cfg: BuildingAutoHeightLayer,
    ) -> trimesh.Trimesh | None:
        """Build a 3D mesh for a set of building geometries."""
        scaled_height = layer_cfg.height * cache.mesh_height_scale

        all_vertices = []
        all_faces = []
        vertex_offset = 0

        for geom in building_geometries:
            # Extract polygons
            if isinstance(geom, MultiPolygon):
                polygons = list(geom.geoms)
            elif isinstance(geom, Polygon):
                polygons = [geom]
            else:
                continue

            for polygon in polygons:
                if polygon.is_empty:
                    continue

                # Get exterior ring coordinates
                coords = np.array(polygon.exterior.coords)[:-1]  # Remove closing point
                if len(coords) < 3:
                    continue

                n_verts = len(coords)

                # Calculate centroid and sample elevation at center
                centroid = polygon.centroid
                center_geo = np.array([[centroid.x, centroid.y]])
                center_elevation = cache.sample_elevation(center_geo)[0]

                # Check if center is valid
                if not cache.sample_validity(center_geo)[0]:
                    continue

                # Calculate base and top Y coordinates
                base_y = cache.elevation_to_mesh_y(center_elevation) + scaled_height_delta
                top_y = base_y + scaled_height

                # Convert exterior coords to mesh coordinates
                mesh_x = cache.geo_to_mesh_x(coords[:, 0])
                mesh_z = cache.geo_to_mesh_z(coords[:, 1])

                # Create vertices: base ring + top ring
                vertices = np.zeros((n_verts * 2, 3), dtype=np.float32)
                # Base vertices (wall bottom)
                vertices[:n_verts, 0] = mesh_x
                vertices[:n_verts, 1] = base_y
                vertices[:n_verts, 2] = mesh_z
                # Top vertices (wall top)
                vertices[n_verts:, 0] = mesh_x
                vertices[n_verts:, 1] = top_y
                vertices[n_verts:, 2] = mesh_z

                faces = []

                # Wall faces (double-sided)
                for i in range(n_verts):
                    i_next = (i + 1) % n_verts
                    base_i = vertex_offset + i
                    base_next = vertex_offset + i_next
                    top_i = vertex_offset + n_verts + i
                    top_next = vertex_offset + n_verts + i_next

                    # Front faces
                    faces.append([base_i, base_next, top_i])
                    faces.append([top_i, base_next, top_next])
                    # Back faces (reversed winding)
                    faces.append([base_i, top_i, base_next])
                    faces.append([top_i, top_next, base_next])

                # Roof and floor faces - use earcut for proper concave polygon triangulation
                # earcut expects 2D array shape (n, 2) and ring sizes as uint32 array
                roof_coords = np.column_stack([mesh_x, mesh_z]).astype(np.float64)
                ring_sizes = np.array([n_verts], dtype=np.uint32)
                tri_indices = mapbox_earcut.triangulate_float64(roof_coords, ring_sizes)
                cap_faces = tri_indices.reshape(-1, 3)

                # Add roof triangles (referencing top ring vertices)
                top_offset = vertex_offset + n_verts
                for face in cap_faces:
                    v0 = top_offset + face[0]
                    v1 = top_offset + face[1]
                    v2 = top_offset + face[2]
                    faces.append([v0, v1, v2])
                    faces.append([v0, v2, v1])

                # Add floor triangles (referencing base ring vertices, reversed winding)
                base_offset = vertex_offset
                for face in cap_faces:
                    v0 = base_offset + face[0]
                    v1 = base_offset + face[1]
                    v2 = base_offset + face[2]
                    faces.append([v0, v2, v1])
                    faces.append([v0, v1, v2])

                all_vertices.append(vertices)
                all_faces.extend(faces)
                vertex_offset += len(vertices)

        if not all_vertices:
            return None

        vertices = np.vstack(all_vertices)
        faces = np.array(all_faces, dtype=np.int32)

        # Use PBR material for Blender compatibility
        r, g, b = layer_cfg.color
        material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[r / 255, g / 255, b / 255, 1.0],
            metallicFactor=0.0,
            roughnessFactor=1.0,
        )
        visuals = trimesh.visual.TextureVisuals(material=material)

        return trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            visual=visuals,
            process=False,
        )

    # Reproject buildings to DEM CRS if needed
    if cache.crs is not None and buildings.crs != cache.crs:
        buildings = buildings.to_crs(cache.crs)

    # Clip buildings to DEM bounds
    from shapely.geometry import box
    bounds_box = box(cache.bounds.left, cache.bounds.bottom, cache.bounds.right, cache.bounds.top)
    buildings = buildings.clip(bounds_box)

    # Group buildings by type using vectorized groupby
    id_column = building_config.building_id_column
    has_id_column = id_column in buildings.columns

    geometries_by_type: dict[int | str, list] = {bid: [] for bid in building_config.building_layers}
    geometries_by_type["default"] = []

    if has_id_column:
        configured_ids = set(building_config.building_layers.keys())
        for building_id, group in buildings.groupby(id_column):
            geoms = group.geometry.tolist()
            if building_id in configured_ids:
                geometries_by_type[building_id] = geoms
            else:
                geometries_by_type["default"].extend(geoms)
    else:
        geometries_by_type["default"] = buildings.geometry.tolist()

    # Build parent layer with children
    parent = GlbLayer(name="buildings_3d")

    # Create child layer for each configured building type
    for building_id, layer_cfg in building_config.building_layers.items():
        geoms = geometries_by_type.get(building_id, [])
        if geoms:
            mesh = build_3d_mesh(geoms, layer_cfg)
            if mesh is not None:
                parent.add_child(GlbLayer(name=f"{layer_cfg.name}_3d", mesh=mesh))

    # Create default child layer
    default_geoms = geometries_by_type.get("default", [])
    if default_geoms:
        mesh = build_3d_mesh(default_geoms, building_config.default_building)
        if mesh is not None:
            parent.add_child(GlbLayer(name="default_3d", mesh=mesh))

    return parent
