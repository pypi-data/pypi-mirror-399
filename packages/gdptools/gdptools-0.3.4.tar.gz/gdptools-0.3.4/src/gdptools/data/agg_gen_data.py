"""Data classes for aggregation operations.

This module defines the data structures used to transfer data between different
components of the `gdptools` aggregation workflow. These dataclasses ensure
that data is consistently structured and contains all necessary metadata for
processing.

Classes:
    AggData: A container for data prepared for aggregation operations.

"""

from dataclasses import dataclass

from geopandas import GeoDataFrame
from xarray import DataArray

from gdptools.data.odap_cat_data import CatClimRItem


@dataclass(repr=True)
class AggData:
    """A container for data prepared for aggregation operations.

    This dataclass holds all the necessary data for a single variable that has
    been pre-processed for aggregation. This includes the original gridded data
    subsetted to the area of interest, the target geometries, and relevant
    metadata.

    Instances of `AggData` are typically created internally by `gdptools` during
    the aggregation process. For each variable specified in a `UserData` object,
    an `AggData` instance is generated.

    Attributes:
        variable (str): Name of the data variable being processed.
        cat_cr (CatClimRItem): Catalog metadata describing the gridded dataset.
        da (DataArray): The gridded data, spatially and temporally subsetted
            to the area of interest.
        target_gdf (GeoDataFrame): Target vector geometries for aggregation.
        target_id (str): Column name in `target_gdf` that uniquely identifies
            each geometry.
        source_time_period (list[str]): Start and end dates for the time slice
            used to prepare this data.

    """

    variable: str
    cat_cr: CatClimRItem
    da: DataArray
    target_gdf: GeoDataFrame
    target_id: str
    source_time_period: list[str]
