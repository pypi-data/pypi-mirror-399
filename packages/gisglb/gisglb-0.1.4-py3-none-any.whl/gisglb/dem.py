from dataclasses import dataclass

import numpy as np
import rasterio
import rasterio.features
from rasterio.crs import CRS
from rasterio.merge import merge
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

    def merge_tif(self, tif_filenames: list[str]) -> None:
        """Read and merge elevation data from multiple TIF files.

        Args:
            tif_filenames: List of paths to TIF files to merge
        """
        if not tif_filenames:
            raise ValueError("No TIF files provided")

        datasets = [rasterio.open(f) for f in tif_filenames]
        try:
            merged_data, merged_transform = merge(datasets)

            first_src = datasets[0]
            height, width = merged_data.shape[1], merged_data.shape[2]

            # Calculate merged bounds from transform and dimensions
            left = merged_transform.c
            top = merged_transform.f
            right = left + width * merged_transform.a
            bottom = top + height * merged_transform.e

            self.elevation = merged_data[0].astype(np.float32)
            self.metadata = TifMetaData(
                crs=first_src.crs,
                transform=merged_transform,
                nodata=first_src.nodata,
                bounds=rasterio.coords.BoundingBox(left, bottom, right, top),
                width=width,
                height=height,
                count=1,
                dtypes=(str(self.elevation.dtype),),
                driver=first_src.driver,
                profile={
                    **first_src.profile,
                    "width": width,
                    "height": height,
                    "transform": merged_transform,
                },
            )

            if self.metadata.nodata is not None:
                self.elevation = np.where(
                    self.elevation == self.metadata.nodata, np.nan, self.elevation
                )
        finally:
            for ds in datasets:
                ds.close()

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

    def save_tif(self, tif_filename: str) -> None:
        """Save elevation data to a GeoTIFF file.

        Args:
            tif_filename: Path to output TIF file
        """
        if self.elevation is None or self.metadata is None:
            raise ValueError("No elevation data to save")

        # Prepare elevation data, converting NaN back to nodata value
        output_data = self.elevation.copy()
        nodata_value = self.metadata.nodata if self.metadata.nodata is not None else -9999.0
        output_data = np.where(np.isnan(output_data), nodata_value, output_data)

        profile = {
            "driver": "GTiff",
            "dtype": output_data.dtype,
            "width": output_data.shape[1],
            "height": output_data.shape[0],
            "count": 1,
            "crs": self.metadata.crs,
            "transform": self.metadata.transform,
            "nodata": nodata_value,
            "compress": "deflate",
            "predictor": 3,  # Floating point predictor for better compression
        }

        with rasterio.open(tif_filename, "w", **profile) as dst:
            dst.write(output_data, 1)
