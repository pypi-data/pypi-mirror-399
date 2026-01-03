"""Data classes for weight generation.

This module defines the data structures used to transfer data between different
components of the `gdptools` weight generation workflow. These dataclasses ensure
that data is consistently structured for calculating spatial intersection weights.

Classes:
    WeightData: A container for data prepared for weight generation.

"""

from dataclasses import dataclass

import geopandas as gpd


@dataclass(repr=True)
class WeightData:
    """A container for data prepared for weight generation.

    This dataclass holds all the necessary data for calculating spatial
    intersection weights. This includes the target vector geometries and the
    source grid cell geometries.

    Instances of `WeightData` are typically created internally by `gdptools`
    during the weight generation process.

    Attributes:
        target_gdf: The `geopandas.GeoDataFrame` containing the
            target vector geometries.
        target_id: The column name in `target_gdf` that serves as the
            unique identifier for each geometry.
        grid_cells: The `geopandas.GeoDataFrame` containing the source
            grid cell polygons.

    """

    target_gdf: gpd.GeoDataFrame
    target_id: str
    grid_cells: gpd.GeoDataFrame
