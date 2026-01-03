"""Polygon-to-polygon weight generation for spatial intersections.

This module provides classes for calculating area-weighted intersection weights
between two sets of polygon geometries. These weights are essential for transferring
data between different administrative boundaries, ecological regions, or other
polygon-based spatial datasets.

Classes:
    WeightGenP2P: Calculates polygon-to-polygon intersection weights using various engines.

Examples:
    Basic polygon-to-polygon weight calculation:
        >>> from gdptools.weight_gen_p2p import WeightGenP2P
        >>> weight_gen = WeightGenP2P(
        ...     target_poly=watersheds,
        ...     target_poly_idx="watershed_id",
        ...     source_poly=counties,
        ...     source_poly_idx="county_id",
        ...     method="serial",
        ...     weight_gen_crs=5070
        ... )
        >>> weights = weight_gen.calculate_weights()

    Parallel processing with output file:
        >>> weight_gen = WeightGenP2P(
        ...     target_poly=regions,
        ...     target_poly_idx="region_id",
        ...     source_poly=zones,
        ...     source_poly_idx="zone_id",
        ...     method="parallel",
        ...     weight_gen_crs=5070,
        ...     output_file="weights.csv",
        ...     jobs=4
        ... )
        >>> weights = weight_gen.calculate_weights()

"""

import logging
import os
from typing import Literal

import geopandas as gpd
import pandas as pd
from pyproj import CRS

from gdptools.weights.calc_weight_engines import DaskWghtGenEngine, ParallelWghtGenEngine, SerialWghtGenEngine

logger = logging.getLogger(__name__)

WEIGHT_GEN_METHODS = Literal["serial", "parallel", "dask"]
"""Available polygon-to-polygon weight generation processing methods.

Options:
    serial: Sequential processing through polygon pairs one by one.
        Best for small datasets with few polygons or debugging.
    parallel: Multi-core processing with polygon chunks distributed across CPUs.
        Optimal for moderate datasets with many polygon intersections.
    dask: Distributed computing using Dask framework.
        Ideal for very large datasets or cluster environments.

Notes:
    Choose the method based on your computational resources and dataset complexity.
    Serial is most reliable, parallel offers good speedup for many intersections,
    and dask excels with very large polygon datasets or distributed computing.

Examples:
    >>> method = "serial"  # For smaller datasets
    >>> method = "parallel"  # For larger datasets
    >>> method = "dask"  # For very large or distributed datasets

"""


class WeightGenP2P:
    """Calculates polygon-to-polygon intersection weights for spatial data transfer.

    This class computes spatial intersection weights between two sets of polygon
    geometries, enabling accurate transfer of data between different administrative
    boundaries, ecological regions, or other polygon-based spatial datasets.

    Args:
        target_poly: GeoDataFrame containing target polygons for weight calculation.
        target_poly_idx: Column name for unique identifiers of target polygons.
        source_poly: GeoDataFrame containing source polygons for weight calculation.
        source_poly_idx: Column name(s) for unique identifiers of source polygons.
        method: Processing method for weight calculation.
        weight_gen_crs: Coordinate reference system for weight calculations.
            Accepts EPSG codes, WKT strings, or pyproj CRS objects.
        output_file: Path to save weights CSV file. If None, weights are not saved.
        jobs: Number of processors for parallel or dask methods. -1 uses all available.
        intersections: Whether to calculate and store detailed intersection geometries.
        verbose: Whether to print detailed processing information.

    Attributes:
        intersections: GeoDataFrame of polygon intersections (if calculated).

    Raises:
        TypeError: If method is not one of the supported processing methods.

    Examples:
        Basic polygon-to-polygon weights:
            >>> weight_gen = WeightGenP2P(
            ...     target_poly=watersheds,
            ...     target_poly_idx="watershed_id",
            ...     source_poly=counties,
            ...     source_poly_idx="county_id",
            ...     method="serial",
            ...     weight_gen_crs=5070
            ... )
            >>> wght = weight_gen.calculate_weights()

        Parallel processing with intersections:
            >>> weight_gen = WeightGenP2P(
            ...     target_poly=regions,
            ...     target_poly_idx="region_id",
            ...     source_poly=zones,
            ...     source_poly_idx="zone_id",
            ...     method="parallel",
            ...     weight_gen_crs=5070,
            ...     intersections=True,
            ...     jobs=4
            ... )
            >>> wght = weight_gen.calculate_weights()
            >>> intersections_gdf = weight_gen.intersections

    """

    def __init__(
        self,
        *,
        target_poly: gpd.GeoDataFrame,
        target_poly_idx: str,
        source_poly: gpd.GeoDataFrame,
        source_poly_idx: str | list[str],
        method: WEIGHT_GEN_METHODS,
        weight_gen_crs: str | int | CRS,
        output_file: str | None = None,
        jobs: int | None = -1,
        intersections: bool = False,
        verbose: bool = False,
    ) -> None:
        """Initialize the WeightGenP2P class with configuration parameters.

        Sets up the polygon-to-polygon weight generation system by configuring
        the source and target geometries, processing method, and output options.

        Args:
            target_poly: GeoDataFrame containing target polygons.
                Must include the column specified in target_poly_idx and geometry column.
            target_poly_idx: Column name for target polygon unique identifiers.
            source_poly: GeoDataFrame containing source polygons.
                Must include the column(s) specified in source_poly_idx and geometry column.
            source_poly_idx: Column name(s) for source polygon unique identifiers.
                Can be a single column name or list of column names.
            method: Processing method for weight calculation ('serial', 'parallel', 'dask').
            weight_gen_crs: Coordinate reference system for calculations.
                Accepts EPSG codes, WKT strings, or pyproj CRS objects.
            output_file: Path to save weights as CSV file. If None, no file is saved.
            jobs: Number of processors for parallel/dask methods. -1 uses half available.
            intersections: If True, calculate and store detailed intersection geometries.
            verbose: If True, prints detailed processing information during execution.

        Raises:
            TypeError: If method is not one of the supported processing methods.

        Notes:
            Input polygons are automatically dissolved by their ID columns and sorted
            for consistent processing. Invalid geometries should be cleaned beforehand.

        """
        self.target_poly = target_poly.reset_index()
        self.target_poly_idx = target_poly_idx
        self.target_poly = self.target_poly.sort_values(self.target_poly_idx).dissolve(
            by=self.target_poly_idx, as_index=False
        )
        self.source_poly = source_poly.reset_index()
        self.source_poly_idx = source_poly_idx
        self.method = method
        self.output_file = "" if output_file is None else output_file
        self.weight_gen_crs = weight_gen_crs
        self.jobs = jobs
        self.calc_intersections = intersections
        self.verbose = verbose
        self._intersections: gpd.GeoDataFrame
        self.__calc_method: SerialWghtGenEngine | ParallelWghtGenEngine | DaskWghtGenEngine
        if self.method == "serial":
            self.__calc_method = SerialWghtGenEngine()
            print("Using serial engine")
        elif self.method == "parallel":
            self.__calc_method = ParallelWghtGenEngine()
            print("Using parallel engine")
        elif self.method == "dask":
            self.__calc_method = DaskWghtGenEngine()
        else:
            raise TypeError(f"method: {self.method} not in [serial, parallel]")

        if jobs == -1:
            self.jobs = int(os.cpu_count() / 2)  # type: ignore
            if self.method in ["parallel", "dask"]:
                logger.info(" Getting jobs from os.cpu_count()")
        else:
            self.jobs = jobs
        if self.method in ["parallel", "dask"]:
            logger.info(f"  Parallel or Dask multiprocessing  using {self.jobs} jobs")
        self.verbose = verbose

    def calculate_weights(self) -> pd.DataFrame:
        """Calculate spatial intersection weights between polygon sets.

        Computes area-weighted intersection weights between target and source
        polygons. The weights represent the proportional area contribution of
        each source polygon to each target polygon.

        Returns:
            pd.DataFrame: A DataFrame containing the calculated weights with columns:
        - ``target_id``: Identifier for the target polygon.
        - ``source_id``: Identifier for the source polygon.
        - ``wght``: Proportional area of the source polygon within the target (0.0-1.0).
        - ``source_id_area``: Total area of the source polygon (for extensive variables).
        - ``target_id_area``: Total area of the target polygon (for diagnostics).
        - ``area_weight``: Area of the intersection.

        Notes:
            For spatially continuous source polygons without gaps or overlaps, the
            ``wght`` values for each target polygon should sum to 1.0.

        Examples:
            >>> wght = weight_gen.calculate_weights()
            >>> print(f"Calculated {len(wght)} weight entries")
            >>> print(f"Weight range: {wght['wght'].min():.4f} to {wght['wght'].max():.4f}")

            >>> # Verify weights sum to 1 for each target (if source is continuous)
            >>> weight_sums = wght.groupby('target_id')["wght"].sum()
            >>> print(f"Weight sum range: {weight_sums.min():.4f} to {weight_sums.max():.4f}")

        """
        if self.calc_intersections:
            weights, self._intersections = self.__calc_method.calc_weights(
                target_poly=self.target_poly,
                target_poly_idx=self.target_poly_idx,
                source_poly=self.source_poly,
                source_poly_idx=self.source_poly_idx,
                source_type="poly",
                wght_gen_crs=self.weight_gen_crs,
                filename=self.output_file,
                intersections=self.calc_intersections,
                jobs=self.jobs,
                verbose=self.verbose,
            )
        else:
            weights = self.__calc_method.calc_weights(
                target_poly=self.target_poly,
                target_poly_idx=self.target_poly_idx,
                source_poly=self.source_poly,
                source_poly_idx=self.source_poly_idx,
                source_type="poly",
                wght_gen_crs=self.weight_gen_crs,
                filename=self.output_file,
                intersections=self.calc_intersections,
                jobs=self.jobs,
                verbose=self.verbose,
            )
        # source_poly_area_header = f"{self.source_poly_idx}_area"
        # target_poly_area_header = f"{self.target_poly_idx}_area"
        # # Calculate the area of source and target polygons
        # self.source_poly[source_poly_area_header] = self.source_poly.geometry.area
        # self.target_poly[target_poly_area_header] = self.target_poly.geometry.area

        # for idx, ref_df in [(self.source_poly_idx, self.source_poly), (self.target_poly_idx, self.target_poly)]:
        #     if idx in weights and idx in ref_df:
        #         weights[idx] = weights[idx].astype(ref_df[idx].dtype)


        # # Merge the area columns with the weights dataframe
        # weights = weights.merge(
        #     self.source_poly[[self.source_poly_idx, source_poly_area_header]], how="left", on=self.source_poly_idx
        # )
        # weights = weights.merge(
        #     self.target_poly[[self.target_poly_idx, target_poly_area_header]], how="left", on=self.target_poly_idx
        # )

        # # Calculate area_weight and add it to the weights DataFrame
        # weights["area_weight"] = weights["wght"] * weights[target_poly_area_header]

        # # Normalize the area_weight
        # weights["normalized_area_weight"] = weights["wght"]

        # # Reorder the columns as required
        # weights = weights[
        #     [
        #         self.source_poly_idx,
        #         self.target_poly_idx,
        #         source_poly_area_header,
        #         target_poly_area_header,
        #         "area_weight",
        #         "normalized_area_weight",
        #     ]
        # ]

        return weights

    @property
    def intersections(self) -> gpd.GeoDataFrame:
        """Get the polygon intersection geometries as a GeoDataFrame.

        Returns the detailed intersection geometries between target and source
        polygons. These represent the actual spatial overlap areas used in
        weight calculations.

        Returns:
            A geopandas GeoDataFrame containing intersection geometries with
            target and source identifiers, calculated areas, and intersection
            polygons.

        Notes:
            This property is only populated after calling `calculate_weights()`
            with `intersections=True`. If accessed otherwise, a message will
            be printed.

        Examples:
            >>> weight_gen = WeightGenP2P(..., intersections=True)
            >>> wght = weight_gen.calculate_weights()
            >>> intersections = weight_gen.intersections
            >>> print(f"Intersection areas: {intersections.geometry.area.describe()}")

        """
        if getattr(self, "_intersections", None) is None:
            print("intersections not calculated, Run calculate_weights(intersections=True)")
        return self._intersections  # type: ignore[return-value]
