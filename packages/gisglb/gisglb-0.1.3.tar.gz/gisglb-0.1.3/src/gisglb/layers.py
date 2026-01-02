from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import trimesh
import trimesh.visual
from PIL import Image
import fast_simplification

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


def create_dem_heightmap_layer(
    dem: DemData, config: HeightmapConfig | None = None
) -> GlbLayer:
    """Create a GlbLayer with a colored heightmap mesh from DEM data.

    The mesh is centered at origin (0, 0, 0).
    Height is indicated by a color texture using a terrain colormap.
    """
    from .glb import GlbLayer

    if config is None:
        config = HeightmapConfig()

    if dem.elevation is None:
        raise ValueError("DemData has no elevation data")

    print('create_dem_heightmap_layer : 00 :')

    sw_total = StopWatch()
    sw_setup = StopWatch()

    elevation = dem.elevation.copy()

    # Resample elevation to mesh_size if specified
    orig_rows, orig_cols = elevation.shape
    if config.mesh_size is not None:
        mesh_rows, mesh_cols = config.mesh_size, config.mesh_size
        elev_image = Image.fromarray(elevation, mode='F')
        elev_image = elev_image.resize((mesh_cols, mesh_rows), Image.Resampling.BILINEAR)
        elevation = np.array(elev_image)

    rows, cols = elevation.shape
    print(f'mesh rows={rows} cols={cols}')

    # Create grid coordinates centered at origin
    # X axis: West positive, so we flip the x coordinates
    x = np.linspace(config.x_size / 2, -config.x_size / 2, cols)  # West to East
    z = np.linspace(config.z_size / 2, -config.z_size / 2, rows)  # North to South
    xx, zz = np.meshgrid(x, z)

    # Normalize heights for Y coordinate (up axis)
    valid_mask = ~np.isnan(elevation)
    min_elev = np.nanmin(elevation)
    max_elev = np.nanmax(elevation)
    elev_range = max_elev - min_elev if max_elev != min_elev else 1.0
    normalized = (elevation - min_elev) / elev_range
    normalized = np.where(valid_mask, normalized, 0.0)

    # Scale Y to reasonable height
    yy = normalized * config.height_scale

    # Create vertices array (rows * cols, 3)
    vertices = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], axis=1)

    print(f'sw_setup={sw_setup}')

    sw_faces = StopWatch()

    # Create faces (triangles) for the grid, skipping cells with nodata
    # Vectorized implementation for performance
    i_idx, j_idx = np.meshgrid(np.arange(rows - 1), np.arange(cols - 1), indexing='ij')
    i_flat = i_idx.ravel()
    j_flat = j_idx.ravel()

    # Check if all 4 corners of each cell have valid data
    cell_valid = (valid_mask[:-1, :-1] & valid_mask[:-1, 1:] &
                  valid_mask[1:, :-1] & valid_mask[1:, 1:]).ravel()

    # Vertex indices for all cells
    v0 = i_flat * cols + j_flat
    v1 = i_flat * cols + (j_flat + 1)
    v2 = (i_flat + 1) * cols + j_flat
    v3 = (i_flat + 1) * cols + (j_flat + 1)

    # Filter to valid cells only
    v0_valid = v0[cell_valid]
    v1_valid = v1[cell_valid]
    v2_valid = v2[cell_valid]
    v3_valid = v3[cell_valid]

    # Two triangles per cell: [v0, v2, v1] and [v1, v2, v3]
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

    # Determine texture dimensions
    if config.texture_size is not None:
        tex_rows, tex_cols = config.texture_size, config.texture_size
        # Resample normalized heights to texture size
        norm_image = Image.fromarray((normalized * 255).astype(np.uint8), mode='L')
        norm_image = norm_image.resize((tex_cols, tex_rows), Image.Resampling.BILINEAR)
        tex_normalized = np.array(norm_image).astype(np.float32) / 255.0
    else:
        tex_rows, tex_cols = rows, cols
        tex_normalized = normalized

    print(f'tex_rows={tex_rows} tex_cols={tex_cols}')

    texture_colors = np.zeros((tex_rows, tex_cols, 3), dtype=np.uint8)
    for i in range(tex_rows):
        for j in range(tex_cols):
            h = tex_normalized[i, j]
            if h < 0.2:
                t = h / 0.2
                texture_colors[i, j] = [0, int(100 + 155 * t), int(200 - 50 * t)]
            elif h < 0.4:
                t = (h - 0.2) / 0.2
                texture_colors[i, j] = [0, 255, int(150 * (1 - t))]
            elif h < 0.6:
                t = (h - 0.4) / 0.2
                texture_colors[i, j] = [int(255 * t), 255, 0]
            elif h < 0.8:
                t = (h - 0.6) / 0.2
                texture_colors[i, j] = [255, int(255 - 120 * t), 0]
            else:
                t = (h - 0.8) / 0.2
                texture_colors[i, j] = [255, int(135 + 120 * t), int(255 * t)]
    texture_image = Image.fromarray(texture_colors, mode='RGB')
    print(f'sw_texture={sw_texture}')

    # Create mesh with texture
    sw_mesh = StopWatch()
    material = trimesh.visual.material.PBRMaterial(baseColorTexture=texture_image)
    visuals = trimesh.visual.TextureVisuals(uv=uv_coords, material=material)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, visual=visuals)
    print(f'sw_mesh={sw_mesh}')

    # Simplify mesh if requested
    if config.simplify_ratio is not None:
        sw_simplify = StopWatch()
        original_faces = len(mesh.faces)
        # fast_simplification works on vertices and faces directly
        simplified_verts, simplified_faces = fast_simplification.simplify(
            mesh.vertices,
            mesh.faces,
            target_reduction=1.0 - config.simplify_ratio,
        )
        # Rebuild UV coordinates for simplified mesh by interpolating
        # For now, use barycentric-ish approach: take UV from closest original vertex
        from scipy.spatial import cKDTree
        tree = cKDTree(vertices)
        _, indices = tree.query(simplified_verts)
        simplified_uv = uv_coords[indices]
        # Recreate mesh with simplified geometry
        visuals = trimesh.visual.TextureVisuals(uv=simplified_uv, material=material)
        mesh = trimesh.Trimesh(vertices=simplified_verts, faces=simplified_faces, visual=visuals)
        print(f'sw_simplify={sw_simplify} ({original_faces} -> {len(mesh.faces)} faces)')

    print(f'sw_total={sw_total}')

    return GlbLayer(name="heightmap", mesh=mesh)
