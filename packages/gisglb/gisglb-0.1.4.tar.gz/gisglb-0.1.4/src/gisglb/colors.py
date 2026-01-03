from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import rasterio.coords
import rasterio.features
from geopandas import GeoDataFrame
from rasterio.crs import CRS
from rasterio.transform import Affine, from_bounds


@dataclass
class TextureContext:
    """Context information for texture generation."""

    tex_rows: int
    tex_cols: int
    min_elevation: float
    max_elevation: float
    bounds: rasterio.coords.BoundingBox | None
    crs: CRS | None
    transform: Affine | None


class HeightmapColorAlgorithm(ABC):
    """Base class for heightmap coloring algorithms."""

    def prepare(self, context: TextureContext) -> None:
        """Prepare for texture generation.

        Override to load ground cover data, precompute lookups, etc.
        Called before generate_texture().

        Args:
            context: Information about the texture and source DEM
        """
        pass

    @abstractmethod
    def generate_texture(self, normalized_heights: np.ndarray) -> np.ndarray:
        """Generate RGB texture from normalized heights.

        Args:
            normalized_heights: 2D array (rows, cols) with values 0.0-1.0

        Returns:
            3D array (rows, cols, 3) with RGB values 0-255, dtype uint8
        """
        pass


class DefaultHeightmapColorAlgorithm(HeightmapColorAlgorithm):
    """Default terrain colormap based on elevation bands."""

    def generate_texture(self, normalized_heights: np.ndarray) -> np.ndarray:
        """Generate RGB texture using terrain elevation bands.

        Color bands:
        - 0.0-0.2: Blue-green (low elevation / water)
        - 0.2-0.4: Green (vegetation)
        - 0.4-0.6: Yellow-green (higher vegetation)
        - 0.6-0.8: Orange (hills)
        - 0.8-1.0: Pink-white (peaks)
        """
        h = normalized_heights
        rows, cols = h.shape
        texture = np.zeros((rows, cols, 3), dtype=np.uint8)

        # Band 1: 0.0-0.2 (blue-green)
        mask = h < 0.2
        t = h[mask] / 0.2
        texture[mask, 0] = 0
        texture[mask, 1] = (100 + 155 * t).astype(np.uint8)
        texture[mask, 2] = (200 - 50 * t).astype(np.uint8)

        # Band 2: 0.2-0.4 (green)
        mask = (h >= 0.2) & (h < 0.4)
        t = (h[mask] - 0.2) / 0.2
        texture[mask, 0] = 0
        texture[mask, 1] = 255
        texture[mask, 2] = (150 * (1 - t)).astype(np.uint8)

        # Band 3: 0.4-0.6 (yellow-green)
        mask = (h >= 0.4) & (h < 0.6)
        t = (h[mask] - 0.4) / 0.2
        texture[mask, 0] = (255 * t).astype(np.uint8)
        texture[mask, 1] = 255
        texture[mask, 2] = 0

        # Band 4: 0.6-0.8 (orange)
        mask = (h >= 0.6) & (h < 0.8)
        t = (h[mask] - 0.6) / 0.2
        texture[mask, 0] = 255
        texture[mask, 1] = (255 - 120 * t).astype(np.uint8)
        texture[mask, 2] = 0

        # Band 5: 0.8-1.0 (pink-white)
        mask = h >= 0.8
        t = (h[mask] - 0.8) / 0.2
        texture[mask, 0] = 255
        texture[mask, 1] = (135 + 120 * t).astype(np.uint8)
        texture[mask, 2] = (255 * t).astype(np.uint8)

        return texture


class GroundHeightmapColorAlgorithm(HeightmapColorAlgorithm):
    """Color algorithm based on ground cover types from a GeoDataFrame."""

    GROUND_TYPE_COLORS: dict[int, tuple[int, int, int]] = {
        2631: (0, 0, 139),        # Hav (Sea) - dark blue
        2632: (0, 100, 200),      # Sjö (Lake) - blue
        2633: (30, 144, 255),     # Vattendragsyta (Water course) - light blue
        2634: (70, 130, 180),     # Anlagt vatten (Artificial water) - steel blue
        2635: (255, 255, 255),    # Glaciär (Glacier) - white
        2636: (128, 128, 128),    # Sluten bebyggelse (Dense buildings) - gray
        2637: (105, 105, 105),    # Hög bebyggelse (High buildings) - dark gray
        2638: (192, 192, 192),    # Låg bebyggelse (Low buildings) - light gray
        2639: (64, 64, 64),       # Industri- och handelsbebyggelse (Industrial) - dark gray
        2640: (210, 180, 140),    # Öppen mark (Open land) - tan
        2642: (255, 215, 0),      # Åker (Field/Agriculture) - yellow
        2643: (173, 255, 47),     # Fruktodling (Fruit cultivation) - green yellow
        2644: (139, 119, 101),    # Kalfjäll (Bare mountain) - brown/gray
        2645: (34, 139, 34),      # Barr- och blandskog (Coniferous forest) - dark green
        2646: (107, 142, 35),     # Lövskog (Deciduous forest) - olive green
        2647: (144, 238, 144),    # Fjällbjörkskog (Mountain birch forest) - light green
        2648: (160, 160, 160),    # Ej karterat område (Not mapped) - medium gray
    }

    #DEFAULT_COLOR: tuple[int, int, int] = (128, 128, 128)
    DEFAULT_COLOR: tuple[int, int, int] = (255, 255, 255)

    def __init__(self, ground: GeoDataFrame, type_column: str = "objekttypnr") -> None:
        """Initialize with ground cover data.

        Args:
            ground: GeoDataFrame with ground cover polygons
            type_column: Column name containing ground type codes
        """
        self.ground = ground
        self.type_column = type_column
        self.ground_cover: np.ndarray | None = None

    def prepare(self, context: TextureContext) -> None:
        """Rasterize ground cover polygons to texture dimensions."""
        if context.bounds is None:
            raise ValueError("TextureContext must have bounds for ground cover")

        # Reproject ground data to DEM CRS if needed
        ground = self.ground
        if context.crs is not None and ground.crs != context.crs:
            ground = ground.to_crs(context.crs)

        # Clip to bounds - only process polygons that intersect the area
        from shapely.geometry import box
        bounds_box = box(
            context.bounds.left,
            context.bounds.bottom,
            context.bounds.right,
            context.bounds.top,
        )
        ground = ground.clip(bounds_box)

        # Create transform from bounds to texture pixels
        transform = from_bounds(
            context.bounds.left,
            context.bounds.bottom,
            context.bounds.right,
            context.bounds.top,
            context.tex_cols,
            context.tex_rows,
        )

        # Rasterize polygons with ground type as the burn value
        shapes = [
            (geom, value)
            for geom, value in zip(ground.geometry, ground[self.type_column])
            if not geom.is_empty
        ]

        self.ground_cover = rasterio.features.rasterize(
            shapes,
            out_shape=(context.tex_rows, context.tex_cols),
            transform=transform,
            fill=0,
            dtype=np.int32,
        )

    def generate_texture(self, normalized_heights: np.ndarray) -> np.ndarray:
        """Generate RGB texture from ground cover types."""
        rows, cols = normalized_heights.shape

        if self.ground_cover is None:
            texture = np.full((rows, cols, 3), self.DEFAULT_COLOR, dtype=np.uint8)
            return texture

        # Create lookup table for vectorized color mapping
        max_type = max(self.GROUND_TYPE_COLORS.keys()) + 1
        lut = np.full((max_type, 3), self.DEFAULT_COLOR, dtype=np.uint8)
        for ground_type, color in self.GROUND_TYPE_COLORS.items():
            lut[ground_type] = color

        # Use ground_cover values as indices into lookup table
        indices = np.clip(self.ground_cover, 0, max_type - 1)
        texture = lut[indices]

        return texture
