import trimesh

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

    def add_layer(self, layer: GlbLayer) -> None:
        """Add a layer to the generator."""
        self.layers.append(layer)

    def _collect_meshes(self, layer: GlbLayer) -> dict[str, trimesh.Trimesh]:
        """Recursively collect meshes from a layer and its children."""
        meshes: dict[str, trimesh.Trimesh] = {}
        if layer.mesh is not None:
            meshes[layer.name] = layer.mesh
        for child in layer.children:
            meshes.update(self._collect_meshes(child))
        return meshes

    def generate_glb(self, glb_filename: str) -> None:
        """Generate a GLB file from all layers."""
        all_meshes: dict[str, trimesh.Trimesh] = {}
        for layer in self.layers:
            all_meshes.update(self._collect_meshes(layer))

        if not all_meshes:
            raise ValueError("No meshes to export")

        scene = trimesh.Scene(geometry=all_meshes)

        # include_normals=True needs scipy
        scene.export(glb_filename, file_type="glb", include_normals=False)



