from dataclasses import dataclass

import numpy as np
import rasterio
import rasterio.features
from rasterio.crs import CRS
from rasterio.transform import Affine
from pyproj import Transformer
from shapely.geometry import Polygon


@dataclass
class TifMetaData:
    """Metadata from a TIF file."""

    crs: CRS | None
    transform: Affine | None
    nodata: float | None
    bounds: rasterio.coords.BoundingBox | None
    width: int
    height: int
    count: int
    dtypes: tuple[str, ...]
    driver: str
    profile: dict


class DemData:
    """Container for DEM elevation data."""

    def __init__(self) -> None:
        self.elevation: np.ndarray | None = None
        self.metadata: TifMetaData | None = None

    def read_tif(self, tif_filename: str) -> None:
        """Read elevation data from a TIF file."""
        with rasterio.open(tif_filename) as src:
            self.elevation = src.read(1).astype(np.float32)
            self.metadata = TifMetaData(
                crs=src.crs,
                transform=src.transform,
                nodata=src.nodata,
                bounds=src.bounds,
                width=src.width,
                height=src.height,
                count=src.count,
                dtypes=src.dtypes,
                driver=src.driver,
                profile=src.profile.copy(),
            )

            if self.metadata.nodata is not None:
                self.elevation = np.where(
                    self.elevation == self.metadata.nodata, np.nan, self.elevation
                )

    def clip(self, coordinates_crs: str, coordinates: list[list[float]]) -> None:
        """Clip elevation data to a polygon region.

        Positions outside the polygon are set to NaN.

        Args:
            coordinates_crs: CRS of the input coordinates (e.g., 'EPSG:4326')
            coordinates: List of [x, y] coordinate pairs defining the polygon
        """
        if self.elevation is None or self.metadata is None:
            raise ValueError("No elevation data loaded")

        if self.metadata.crs is None or self.metadata.transform is None:
            raise ValueError("DEM has no CRS or transform")

        # Transform coordinates to DEM CRS
        transformer = Transformer.from_crs(
            coordinates_crs, self.metadata.crs, always_xy=True
        )
        transformed_coords = [
            transformer.transform(coord[0], coord[1]) for coord in coordinates
        ]

        # Create polygon in DEM CRS
        polygon = Polygon(transformed_coords)

        # Rasterize the polygon to create a mask
        mask = rasterio.features.geometry_mask(
            [polygon],
            out_shape=self.elevation.shape,
            transform=self.metadata.transform,
            invert=True,  # True inside polygon
        )

        # Set values outside polygon to NaN
        self.elevation = np.where(mask, self.elevation, np.nan)
