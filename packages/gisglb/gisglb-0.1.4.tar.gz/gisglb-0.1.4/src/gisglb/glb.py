from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import trimesh

if TYPE_CHECKING:
    from .layers import DemCache


@dataclass
class GeoReference:
    """Geographic reference information for coordinate transformation."""

    crs: str
    """CRS as EPSG code (e.g., 'EPSG:3006') or WKT string."""

    bounds_left: float
    bounds_bottom: float
    bounds_right: float
    bounds_top: float
    """Geographic bounds in the CRS."""

    mesh_x_size: float
    mesh_z_size: float
    """Mesh dimensions."""

    min_elevation: float
    max_elevation: float
    """Elevation range in real-world units."""

    height_scale: float
    """Scale factor applied to elevation for mesh Y coordinate."""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "crs": self.crs,
            "bounds": {
                "left": self.bounds_left,
                "bottom": self.bounds_bottom,
                "right": self.bounds_right,
                "top": self.bounds_top,
            },
            "mesh_size": {
                "x": self.mesh_x_size,
                "z": self.mesh_z_size,
            },
            "elevation": {
                "min": self.min_elevation,
                "max": self.max_elevation,
                "height_scale": self.height_scale,
            },
        }

    @staticmethod
    def from_dem_cache(cache: "DemCache") -> "GeoReference":
        """Create GeoReference from a DemCache."""
        crs_str = cache.crs.to_string() if cache.crs else "unknown"
        return GeoReference(
            crs=crs_str,
            bounds_left=cache.bounds.left,
            bounds_bottom=cache.bounds.bottom,
            bounds_right=cache.bounds.right,
            bounds_top=cache.bounds.top,
            mesh_x_size=cache.x_size,
            mesh_z_size=cache.z_size,
            min_elevation=cache.min_elev,
            max_elevation=cache.max_elev,
            height_scale=cache.height_scale,
        )


class GlbLayer:
    """A layer containing mesh data for GLB generation."""

    def __init__(self, name: str, mesh: trimesh.Trimesh | None = None) -> None:
        self.name: str = name
        self.mesh: trimesh.Trimesh | None = mesh
        self.children: list[GlbLayer] = []

    def add_child(self, layer: "GlbLayer") -> None:
        """Add a child layer."""
        self.children.append(layer)


class GlbGenerator:
    """Generator for creating GLB files from layers."""

    def __init__(self) -> None:
        self.layers: list[GlbLayer] = []
        self.geo_reference: GeoReference | None = None

    def add_layer(self, layer: GlbLayer) -> None:
        """Add a layer to the generator."""
        self.layers.append(layer)

    def set_geo_reference(self, geo_ref: GeoReference) -> None:
        """Set geographic reference for coordinate transformation."""
        self.geo_reference = geo_ref

    def set_geo_reference_from_cache(self, cache: "DemCache") -> None:
        """Set geographic reference from a DemCache."""
        self.geo_reference = GeoReference.from_dem_cache(cache)

    def _add_layer_to_scene(
        self,
        scene: trimesh.Scene,
        layer: GlbLayer,
        parent_node: str | None = None,
    ) -> None:
        """Recursively add a layer and its children to the scene with hierarchy."""
        identity = np.eye(4)
        node_name = layer.name

        if layer.mesh is not None:
            # Add geometry and create node with parent relationship
            scene.add_geometry(
                geometry=layer.mesh,
                node_name=node_name,
                geom_name=node_name,
                parent_node_name=parent_node,
                transform=identity,
            )
        else:
            # Create empty node for hierarchy (no geometry)
            scene.graph.update(
                frame_to=node_name,
                frame_from=parent_node if parent_node else scene.graph.base_frame,
                matrix=identity,
            )

        # Recursively add children with this layer as parent
        for child in layer.children:
            self._add_layer_to_scene(scene, child, parent_node=node_name)

    def generate_glb(self, glb_filename: str) -> None:
        """Generate a GLB file from all layers with hierarchy preserved."""
        scene = trimesh.Scene()

        for layer in self.layers:
            self._add_layer_to_scene(scene, layer, parent_node=None)

        if len(scene.geometry) == 0:
            raise ValueError("No meshes to export")

        # Add geo reference as scene metadata (becomes extras in glTF)
        if self.geo_reference is not None:
            scene.metadata["extras"] = {"geoReference": self.geo_reference.to_dict()}

        scene.export(glb_filename, file_type="glb", include_normals=False)



