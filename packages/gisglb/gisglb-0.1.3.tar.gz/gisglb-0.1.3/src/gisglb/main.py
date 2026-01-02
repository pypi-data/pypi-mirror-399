
from .dem import DemData
from .layers import HeightmapConfig, create_dem_heightmap_layer
from .glb import GlbGenerator


def gen_heightmap_glb(
    dem: DemData, glb_filename: str, config: HeightmapConfig | None = None
) -> None:
    """Generate a GLB file with a colored heightmap from DEM data.

    The mesh is centered at origin (0, 0, 0).
    Height is indicated by a color texture using a terrain colormap.
    """
    layer = create_dem_heightmap_layer(dem, config)
    generator = GlbGenerator()
    generator.add_layer(layer)
    generator.generate_glb(glb_filename)

def main() -> None:
    print("Hello from gisglb!")


if __name__ == "__main__":
    main()
