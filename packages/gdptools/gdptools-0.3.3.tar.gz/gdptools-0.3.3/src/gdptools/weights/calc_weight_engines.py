# sourcery skip: inline-immediately-returned-variable
"""Computational Engines for Spatial Weight Generation.

This module provides the backend processing engines for calculating spatial
intersection weights between two sets of vector geometries. It includes an
abstract base class (`CalcWeightEngine`) and its concrete implementations for
serial, parallel (joblib), and distributed (Dask) computation.

These engines are the core computational components used by the higher-level
`WeightGen` (for grid-to-polygon) and `WeightGenP2P` (for polygon-to-polygon)
classes.
"""

import logging
import os
import time
import warnings
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Literal

import dask.bag as db
import dask_geopandas as dgpd
import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
from pyproj import CRS
from shapely import area, intersection, within

from gdptools.utils import (
    _check_feature_crs,
    _check_grid_cell_crs,
    _check_source_poly_idx,
    _check_target_poly_idx,
    _get_crs,
    _make_valid,
    _reproject_for_weight_calc,
)

logger = logging.getLogger(__name__)

SOURCE_TYPES = Literal["grid", "poly"]


class CalcWeightEngine(ABC):
    """Abstract base class for spatial weight calculation engines.

    This class defines the common interface for all weight calculation engines
    (serial, parallel, dask). It uses the template method pattern, where
    `calc_weights` orchestrates the process, and subclasses must implement the
    `get_weight_components` method to provide the specific computational logic.

    This engine can handle both grid-to-polygon and polygon-to-polygon
    intersections.
    """

    def calc_weights(
        self,
        target_poly: gpd.GeoDataFrame,
        target_poly_idx: str,
        source_poly: gpd.GeoDataFrame,
        source_poly_idx: list[str],
        source_type: SOURCE_TYPES,
        wght_gen_crs: str | int | CRS,
        filename: str = "",
        intersections: bool = False,
        jobs: int = -1,
        verbose: bool = False,
    ) -> tuple[pd.DataFrame, gpd.GeoDataFrame] | pd.DataFrame:
        """Calculate weights between target and source polygons.

        This is the main entry point for all weight calculation engines. It
        prepares the data, invokes the weight calculation logic implemented by
        subclasses, and optionally saves the results to a file.

        Args:
            target_poly: The GeoDataFrame of target polygons.
            target_poly_idx: The column name for unique IDs in `target_poly`.
            source_poly: The GeoDataFrame of source polygons.
            source_poly_idx: A list of column names for unique IDs in
                `source_poly`.
            source_type: The type of source polygons ('grid' or 'poly').
            wght_gen_crs: The CRS to use for area calculations.
            filename: Optional path to save the weights DataFrame as a CSV file.
            intersections: If True, calculate and return intersection
                geometries.
            jobs: The number of parallel jobs to use. Defaults to -1.
            verbose: If True, print detailed processing information.

        Returns:
            A pandas DataFrame with the calculated weights. If `intersections`
            is True, it returns a tuple of (weights_df, intersections_gdf).

        """
        # Buffer polygons with self-intersections
        tstrt = time.perf_counter()
        print("     - validating target polygons")
        target_poly = _make_valid(target_poly)
        print("     - validating source polygons")
        source_poly = _make_valid(source_poly)
        tend = time.perf_counter()
        print(f"Validate polygons finished in {tend - tstrt:0.4f} seconds")

        self.target_poly = target_poly.reset_index()
        self.target_poly_idx = target_poly_idx

        self.source_poly = source_poly.reset_index()
        self.source_poly_idx = source_poly_idx

        self.source_type = source_type
        self.wght_gen_crs = wght_gen_crs
        self.filename = filename
        self.intersections = intersections

        available_cpus = os.cpu_count() or 1
        if jobs == -1:
            self.jobs = max(1, int(available_cpus / 2))
            logger.info(" ParallelWghtGenEngine getting jobs from os.cpu_count()")
        elif jobs is None:
            self.jobs = available_cpus
        else:
            self.jobs = jobs
        if self.jobs > available_cpus:
            warnings.warn(
                (
                    f"jobs={self.jobs} exceeds the available CPU count ({available_cpus}). "
                    "Reducing jobs to match available processors."
                ),
                RuntimeWarning,
                stacklevel=2,
            )
            self.jobs = available_cpus
        elif self.jobs < 1:
            warnings.warn(
                "jobs must be a positive integer; defaulting to 1.",
                RuntimeWarning,
                stacklevel=2,
            )
            self.jobs = 1
        logger.info(f"  ParallelWghtGenEngine using {self.jobs} jobs")
        self.verbose = verbose
        _check_target_poly_idx(self.target_poly, self.target_poly_idx)
        _check_source_poly_idx(self.source_poly, self.source_poly_idx)
        _check_feature_crs(poly=self.target_poly)
        _check_grid_cell_crs(grid_cells=self.source_poly)
        self.grid_out_crs = _get_crs(self.wght_gen_crs)
        self.target_poly, self.source_poly = _reproject_for_weight_calc(
            target_poly=self.target_poly,
            source_poly=self.source_poly,
            wght_gen_crs=self.grid_out_crs,
        )
        if self.intersections:
            print(f"Intersections = {self.intersections}")
            if self.source_type == "grid":
                (
                    self.plist,
                    self.ilist,
                    self.jlist,
                    self.wghtlist,
                    self.calc_intersect,
                ) = self.get_weight_components_and_intesections()
            elif self.source_type == "poly":
                (
                    self.plist,
                    self.splist,
                    self.wghtlist,
                    self.calc_intersect,
                ) = self.get_weight_components_and_intesections()
        elif self.source_type == "grid":
            (
                self.plist,
                self.ilist,
                self.jlist,
                self.wghtlist,
            ) = self.get_weight_components()
        elif self.source_type == "poly":
            (
                self.plist,
                self.splist,
                self.wghtlist,
            ) = self.get_weight_components()
        self.wght_df = self.create_wght_df()
        if self.filename:
            self.wght_df.to_csv(self.filename, index=False)
        if self.intersections:
            return self.wght_df, self.calc_intersect
        else:
            return self.wght_df
        # return (  # type: ignore
        #     self.wght_df, self.calc_intersect
        #     if self.intersections
        #     else self.wght_df
        # )

    @abstractmethod
    def get_weight_components(
        self,
    ) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
        """Abstract method to calculate weight components.

        Subclasses must implement this to provide the core logic for calculating
        the weights between source and target polygons.

        Returns:
            A tuple of lists containing the components of the weight table.
            For "grid" source type, returns (target_ids, i_indices,
            j_indices, weights). For "poly" source type, returns
            (target_ids, source_ids, weights).

        """
        pass

    @abstractmethod
    def get_weight_components_and_intesections(
        self,
    ) -> (
        tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
        | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
    ):
        """Abstract method to calculate weight components and intersections.

        Subclasses must implement this to provide the core logic for calculating
        the weights and the resulting intersection geometries.

        Returns:
            A tuple containing the weight components and a GeoDataFrame of the
            intersection geometries. For "grid" source type, returns
            (target_ids, i_indices, j_indices, weights, intersections_gdf).
            For "poly" source type, returns (target_ids, source_ids,
            weights, intersections_gdf).

        """
        pass

    def create_wght_df(self) -> pd.DataFrame:
        """Create a DataFrame from the calculated weight components.

        This method constructs a pandas DataFrame from the lists of weight
        components generated by the engine. It handles both "grid" and "poly"
        source types and includes logic for extensive variable aggregation
        for polygon-to-polygon weights.

        Returns:
            A pandas DataFrame containing the final weight table.

        """
        if self.source_type == "grid":
            wght_df = pd.DataFrame(
                {
                    self.target_poly_idx: self.plist,
                    "i": self.ilist,
                    "j": self.jlist,
                    "wght": self.wghtlist,
                }
            )
            wght_df = wght_df.astype({"i": int, "j": int, "wght": float, self.target_poly_idx: str})
        elif self.source_type == "poly":
            source_idx_col = self.source_poly_idx[0] if isinstance(self.source_poly_idx, list) else self.source_poly_idx
            source_poly_area_header = f"{self.source_poly_idx}_area"
            target_poly_area_header = f"{self.target_poly_idx}_area"
            wght_df = pd.DataFrame(
                {
                    self.target_poly_idx: self.plist,
                    source_idx_col: self.splist,
                    "wght": self.wghtlist,
                }
            )
            self.source_poly[source_poly_area_header] = self.source_poly.geometry.area
            self.target_poly[target_poly_area_header] = self.target_poly.geometry.area

            for idx, ref_df in [(source_idx_col, self.source_poly), (self.target_poly_idx, self.target_poly)]:
                if idx in wght_df and idx in ref_df:
                    wght_df[idx] = wght_df[idx].astype(ref_df[idx].dtype)

            # Merge the area columns with the weights dataframe
            wght_df = wght_df.merge(
                self.source_poly[[source_idx_col, source_poly_area_header]], how="left", on=self.source_poly_idx
            )
            wght_df = wght_df.merge(
                self.target_poly[[self.target_poly_idx, target_poly_area_header]], how="left", on=self.target_poly_idx
            )
            # Calculate area_weight and add it to the weights DataFrame
            wght_df["area_weight"] = wght_df["wght"] * wght_df[target_poly_area_header]
            # Normalize the area_weight
            wght_df["normalized_area_weight"] = wght_df["wght"]
            # Reorder the columns as required
            wght_df = wght_df[
                [
                    self.source_poly_idx,
                    self.target_poly_idx,
                    source_poly_area_header,
                    target_poly_area_header,
                    "area_weight",
                    "normalized_area_weight",
                ]
            ]
            wght_df = wght_df.astype(
                {
                    source_idx_col: str,
                    self.target_poly_idx: str,
                    source_poly_area_header: float,
                    target_poly_area_header: float,
                    "area_weight": float,
                    "normalized_area_weight": float,
                }
            )
        return wght_df


class SerialWghtGenEngine(CalcWeightEngine):
    """A serial engine for calculating spatial intersection weights.

    This engine processes all target and source polygons sequentially in a
    single thread. It is reliable and useful for smaller datasets or for
    debugging purposes. The core logic is adapted from the `area_tables_binning`
    method in the `tobler` package.
    """

    def get_weight_components(
        self,
    ) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
        """Calculate weight components serially.

        This method implements the weight calculation logic for a serial
        execution environment. It calls the `area_tables_binning` worker
        function to perform the spatial intersections and calculate weights.

        Returns:
            A tuple of lists containing the components of the weight table.
            For "grid" source type, returns (target_ids, i_indices,
            j_indices, weights). For "poly" source type, returns
            (target_ids, source_ids, weights).

        """
        tsrt = time.perf_counter()
        if self.source_type == "grid":
            plist, ilist, jlist, wghtslist = self.area_tables_binning(
                source_df=self.source_poly,
                target_df=self.target_poly,
                source_type=self.source_type,
            )
        elif self.source_type == "poly":
            plist, splist, wghtslist = self.area_tables_binning(
                source_df=self.source_poly,
                target_df=self.target_poly,
                source_type=self.source_type,
            )
        tend = time.perf_counter()
        print(f"Weight gen finished in {tend - tsrt:0.4f} seconds")
        return (
            (plist, ilist, jlist, wghtslist)
            if self.source_type == "grid"
            else (plist, splist, wghtslist)
        )

    def get_weight_components_and_intesections(
        self,
    ) -> (
        tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
        | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
    ):
        """Calculate weight components and intersection geometries serially.

        This method implements the weight calculation logic for a serial
        execution environment, including the generation of intersection
        geometries. It calls the `area_tables_binning_and_intersections`
        worker function.

        Returns:
            A tuple containing the weight components and a GeoDataFrame of the
            intersection geometries.

        """
        tsrt = time.perf_counter()
        if self.source_type == "grid":
            plist, ilist, jlist, wghtslist, gdf = self.area_tables_binning_and_intersections(
                source_df=self.source_poly,
                target_df=self.target_poly,
                source_type=self.source_type,
            )
        elif self.source_type == "poly":
            plist, splist, wghtslist, gdf = self.area_tables_binning_and_intersections(
                source_df=self.source_poly,
                target_df=self.target_poly,
                source_type=self.source_type,
            )
        tend = time.perf_counter()
        print(f"Weight gen finished in {tend - tsrt:0.4f} seconds")
        return (
            (plist, ilist, jlist, wghtslist, gdf)
            if self.source_type == "grid"
            else (plist, splist, wghtslist, gdf)
        )

    def area_tables_binning(
        self: "SerialWghtGenEngine",
        source_df: gpd.GeoDataFrame,
        target_df: gpd.GeoDataFrame,
        source_type: SOURCE_TYPES,
    ) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
        """Generate area allocation and source-target correspondence tables.

        This method constructs area allocation and source-target correspondence
        tables using a spatial index query. It is based on and adapted from
        the `tobler` package.

        Optimization: Source polygons fully contained within target polygons
        use source.area directly, avoiding expensive intersection() calls.

        Args:
            source_df: GeoDataFrame containing the source polygons.
            target_df: GeoDataFrame containing the target polygons.
            source_type: Type of the source geometry ('grid' or 'poly').

        Returns:
            A tuple of lists containing the components of the weight table.

        """
        tstrt = time.perf_counter()
        ids_tgt, ids_src = source_df.sindex.query(target_df.geometry, predicate="intersects")

        source_geoms = source_df.geometry.values[ids_src]
        target_geoms = target_df.geometry.values[ids_tgt]

        # Partition into contained (cheap) vs boundary (expensive) pairs
        contained_mask = within(source_geoms, target_geoms)
        n_total = len(ids_src)
        n_contained = contained_mask.sum()
        logger.info(
            f"  Optimization: {n_contained}/{n_total} pairs contained "
            f"({100 * n_contained / n_total:.1f}% skip intersection)"
        )

        # Compute areas: contained pairs use source area, boundary pairs need intersection
        intersection_areas = np.empty(n_total, dtype=np.float64)
        intersection_areas[contained_mask] = area(source_geoms[contained_mask])
        if (~contained_mask).any():
            boundary_src = source_geoms[~contained_mask]
            boundary_tgt = target_geoms[~contained_mask]
            intersection_areas[~contained_mask] = area(intersection(boundary_src, boundary_tgt))

        # Normalize by target area
        areas = intersection_areas / area(target_geoms)
        tend = time.perf_counter()
        print(f"Intersections finished in {tend - tstrt:0.4f} seconds")

        if source_type == "grid":
            return (
                target_df[self.target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
                source_df.i_index.iloc[ids_src].values.astype(int).tolist(),
                source_df.j_index.iloc[ids_src].values.astype(int).tolist(),
                areas.astype(float).tolist(),
            )
        else:
            return (
                target_df[self.target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
                source_df[self.source_poly_idx].iloc[ids_src].values.astype(object).tolist(),
                areas.astype(float).tolist(),
            )

    def area_tables_binning_and_intersections(
        self: "SerialWghtGenEngine",
        source_df: gpd.GeoDataFrame,
        target_df: gpd.GeoDataFrame,
        source_type: SOURCE_TYPES,
    ) -> (
        tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
        | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
    ):
        """Generate area allocation tables and intersection geometries.

        This method constructs area allocation tables and the resulting
        intersection geometries using a spatial index query. It is based on
        and adapted from the `tobler` package.

        Optimization: Source polygons fully contained within target polygons
        use source geometry/area directly, avoiding expensive intersection() calls.

        Args:
            source_df: GeoDataFrame containing the source polygons.
            target_df: GeoDataFrame containing the target polygons.
            source_type: Type of the source geometry ('grid' or 'poly').

        Returns:
            A tuple containing the weight components and a GeoDataFrame of the
            intersection geometries.

        """
        tstrt = time.perf_counter()
        ids_tgt, ids_src = source_df.sindex.query(target_df.geometry, predicate="intersects")

        source_geoms = source_df.geometry.values[ids_src]
        target_geoms = target_df.geometry.values[ids_tgt]

        # Partition into contained (cheap) vs boundary (expensive) pairs
        contained_mask = within(source_geoms, target_geoms)
        n_total = len(ids_src)
        n_contained = contained_mask.sum()
        logger.info(
            f"  Optimization: {n_contained}/{n_total} pairs contained "
            f"({100 * n_contained / n_total:.1f}% skip intersection)"
        )

        # Build intersection geometries and areas
        f_intersect = np.empty(n_total, dtype=object)
        intersection_areas = np.empty(n_total, dtype=np.float64)

        # Contained pairs: intersection geometry = source geometry
        f_intersect[contained_mask] = source_geoms[contained_mask]
        intersection_areas[contained_mask] = area(source_geoms[contained_mask])

        # Boundary pairs: compute actual intersection
        if (~contained_mask).any():
            boundary_src = source_geoms[~contained_mask]
            boundary_tgt = target_geoms[~contained_mask]
            boundary_intersect = intersection(boundary_src, boundary_tgt)
            f_intersect[~contained_mask] = boundary_intersect
            intersection_areas[~contained_mask] = area(boundary_intersect)

        # Normalize by target area
        weights = intersection_areas / area(target_geoms)
        gdf_inter = target_df.iloc[ids_tgt]
        gdf_inter = gdf_inter.iloc[:].set_geometry(f_intersect)
        gdf_inter["weights"] = weights.astype(float)
        tend = time.perf_counter()
        print(f"Intersections finished in {tend - tstrt:0.4f} seconds")

        if source_type == "grid":
            return (
                target_df[self.target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
                source_df.i_index.iloc[ids_src].values.astype(int).tolist(),
                source_df.j_index.iloc[ids_src].values.astype(int).tolist(),
                weights.astype(float).tolist(),
                gdf_inter,
            )
        elif source_type == "poly":
            return (
                target_df[self.target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
                source_df[self.source_poly_idx[0]].iloc[ids_src].values.astype(object).tolist(),
                weights.astype(float).tolist(),
                gdf_inter,
            )


class ParallelWghtGenEngine(CalcWeightEngine):
    """A parallel engine for calculating spatial intersection weights using joblib.

    This engine distributes the weight calculation across multiple CPU cores by
    chunking the input geometries. It is well-suited for medium-to-large
    datasets on a single machine to improve performance over serial processing.
    The core logic is adapted from the `tobler` package.
    """

    def get_weight_components(
        self,
    ) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
        """Calculate weight components in parallel.

        This method implements the weight calculation logic for a parallel
        execution environment using `joblib`. It calls the
        `_area_tables_binning_parallel` worker function to perform the spatial
        intersections and calculate weights.

        Returns:
            A tuple of lists containing the components of the weight table.
            For "grid" source type, returns (target_ids, i_indices,
            j_indices, weights). For "poly" source type, returns
            (target_ids, source_ids, weights).

        """
        tsrt = time.perf_counter()
        result = _area_tables_binning_parallel(
            source_df=self.source_poly,
            source_poly_idx=self.source_poly_idx,
            source_type=self.source_type,
            target_df=self.target_poly,
            target_poly_idx=self.target_poly_idx,
            n_jobs=self.jobs,
        )
        tend = time.perf_counter()
        print(f"Weight gen finished in {tend - tsrt:0.4f} seconds")
        return result

    def get_weight_components_and_intesections(
        self,
    ) -> (
        tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
        | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
    ):
        """Calculate weight components and intersection geometries in parallel.

        This method implements the parallel weight calculation logic, including
        the generation of intersection geometries. It calls the
        `_area_tables_binning_parallel_and_intersections` worker function.

        Returns:
            A tuple containing the weight components and a GeoDataFrame of the
            intersection geometries.

        """
        tsrt = time.perf_counter()
        result = _area_tables_binning_parallel_and_intersections(
            source_df=self.source_poly,
            source_poly_idx=self.source_poly_idx,
            source_type=self.source_type,
            target_df=self.target_poly,
            target_poly_idx=self.target_poly_idx,
            n_jobs=self.jobs,
        )
        tend = time.perf_counter()
        print(f"Weight gen finished in {tend - tsrt:0.4f} seconds")
        return result


def _area_tables_binning_parallel_and_intersections(
    source_df: gpd.GeoDataFrame,
    source_poly_idx: str,
    source_type: SOURCE_TYPES,
    target_df: gpd.GeoDataFrame,
    target_poly_idx: str,
    n_jobs: int = -1,
) -> (
    tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
    | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
):
    """Compute spatial intersections and area tables in parallel.

    This function orchestrates the parallel calculation of intersection
    geometries and their corresponding area weights. It chunks the input
    data and distributes the work across multiple processes using `joblib`.

    Args:
        source_df: GeoDataFrame of source polygons.
        source_poly_idx: Column name for unique IDs of source polygons.
        source_type: Type of the source geometry ('grid' or 'poly').
        target_df: GeoDataFrame of target polygons.
        target_poly_idx: Column name for unique IDs of target polygons.
        n_jobs: Number of parallel jobs. Defaults to -1 (use all
            available CPUs).

    Returns:
        A tuple containing the weight components and a GeoDataFrame of the
        intersection geometries.

    """
    if n_jobs == -1:
        n_jobs = int(os.cpu_count() / 2)  # type: ignore
        logger.info(" ParallelWghtGenEngine getting jobs from os.cpu_count()")
    logger.info(f"  ParallelWghtGenEngine using {n_jobs} jobs")

    # Chunk the largest, ship the smallest in full
    to_chunk, df_full = _get_chunks_for_parallel(source_df, target_df)

    # Spatial index query: Reindex on positional IDs
    to_workers = _chunk_dfs(
        gpd.GeoSeries(to_chunk.geometry.values, crs=to_chunk.crs),
        gpd.GeoSeries(df_full.geometry.values, crs=df_full.crs),
        n_jobs,
    )

    worker_out = _get_ids_for_parallel(n_jobs, to_workers)
    ids_src, ids_tgt = np.concatenate(worker_out).T

    # Intersection + area calculation
    chunks_to_intersection = _chunk_polys(
        np.vstack([ids_src, ids_tgt]).T, source_df.geometry, target_df.geometry, n_jobs
    )
    worker_out = _get_areas_and_intersections_for_parallel(n_jobs, chunks_to_intersection)
    areas = np.concatenate([item[0] for item in worker_out])
    inter_geom = np.concatenate([item[1] for item in worker_out])

    print("Processing intersections for output.")
    inter_sect = target_df.iloc[ids_tgt, :].set_geometry(inter_geom)
    weights = areas.astype(float) / target_df.geometry[ids_tgt].area
    inter_sect["weights"] = weights

    if source_type == "grid":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df.i_index.iloc[ids_src].values.astype(int).tolist(),
            source_df.j_index.iloc[ids_src].values.astype(int).tolist(),
            weights.tolist(),
            inter_sect,
        )
    elif source_type == "poly":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df[source_poly_idx[0]].iloc[ids_src].values.astype(object).tolist(),
            weights.tolist(),
            inter_sect,
        )


def _get_areas_and_intersections_for_parallel(
    n_jobs: int,
    chunks_to_intersection: Generator[tuple[gpd.GeoSeries, gpd.GeoSeries], None, None],
) -> list[tuple[gpd.GeoSeries, gpd.GeoSeries]]:
    """Compute intersection areas and geometries for chunks in parallel.

    Args:
        n_jobs: The number of parallel jobs to run.
        chunks_to_intersection: A generator yielding tuples of GeoSeries pairs
            to be processed.

    Returns:
        A list of results from each chunk, where each result is a tuple of
        (area GeoSeries, intersection GeoSeries).

    """
    with parallel_backend("loky", inner_max_num_threads=1):
        worker_out = Parallel(n_jobs=n_jobs)(
            delayed(_intersect_area_on_chunk)(*chunk_pair) for chunk_pair in chunks_to_intersection
        )
    return worker_out


def _get_areas_for_parallel(
    n_jobs: int,
    chunks_to_intersection: Generator[tuple[gpd.GeoSeries, gpd.GeoSeries], None, None],
) -> list[gpd.GeoSeries]:
    """Compute intersection areas for geometry chunks in parallel.

    Args:
        n_jobs: The number of parallel jobs to run.
        chunks_to_intersection: A generator yielding tuples of GeoSeries pairs
            to be processed.

    Returns:
        A list of GeoSeries, where each series contains the calculated
        intersection areas for a chunk.

    Example:
        >>> chunks = _chunk_polys(ids_array, source_geom, target_geom, n_jobs=4)
        >>> areas = _get_areas_for_parallel(4, chunks)
        >>> total_areas = gpd.GeoSeries(pd.concat(areas))

    Note:
        Uses the 'loky' parallel backend with single-threaded inner operations
        to prevent thread conflicts in GEOS operations.

    """
    with parallel_backend("loky", inner_max_num_threads=1):
        worker_out = Parallel(n_jobs=n_jobs)(
            delayed(_area_on_chunk)(*chunk_pair) for chunk_pair in chunks_to_intersection
        )
    return worker_out


def _get_ids_for_parallel(
    n_jobs: int, to_workers: Generator[tuple[gpd.GeoSeries, gpd.GeoSeries], None, None]
) -> list[np.ndarray]:
    """Perform spatial index queries in parallel to get intersecting IDs.

    Args:
        n_jobs: The number of parallel jobs to run.
        to_workers: A generator that yields tuples of GeoSeries, where each
            tuple represents a pair of geometries to query.

    Returns:
        A list of NumPy arrays, where each array contains pairs of
        intersecting geometry IDs from a chunk.

    Example:
        >>> chunks = _chunk_polys(ids_array, source_geom, target_geom, n_jobs=4)
        >>> id_pairs = _get_ids_for_parallel(4, chunks)
        >>> all_pairs = np.concatenate(id_pairs)

    Note:
        Uses spatial indexing for efficient intersection queries before
        computing actual geometric intersections.

    """
    with parallel_backend("loky", inner_max_num_threads=1):
        worker_out = Parallel(n_jobs=n_jobs)(delayed(_index_n_query)(*chunk_pair) for chunk_pair in to_workers)
    return worker_out


def _get_chunks_for_parallel(df1: gpd.GeoDataFrame, df2: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Determine which GeoDataFrame to chunk for parallel processing.

    Args:
        df1: The first GeoDataFrame.
        df2: The second GeoDataFrame.

    Returns:
        A tuple containing (to_chunk, df_full) where to_chunk is the dataframe
        to be divided into chunks and df_full is kept intact.

    Note:
        Currently returns df1 as the dataframe to chunk. This function provides
        a hook for future optimization based on dataframe sizes or geometry complexity.

    """
    to_chunk = df1
    df_full = df2
    return to_chunk, df_full


def _area_tables_binning_parallel(
    source_df: gpd.GeoDataFrame,
    source_poly_idx: str,
    source_type: SOURCE_TYPES,
    target_df: gpd.GeoDataFrame,
    target_poly_idx: str,
    n_jobs: int = -1,
) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
    """Calculate spatial intersections and area tables in parallel.

    This function orchestrates the parallel calculation of area weights, but
    does not generate the intersection geometries. It chunks the input data
    and distributes the work across multiple processes using `joblib`.

    Args:
        source_df: GeoDataFrame of source polygons.
        source_poly_idx: Column name for unique IDs of source polygons.
        source_type: Type of the source geometry ('grid' or 'poly').
        target_df: GeoDataFrame of target polygons.
        target_poly_idx: Column name for unique IDs of target polygons.
        n_jobs: Number of parallel jobs. Defaults to -1.

    Returns:
        A tuple of lists containing the components of the weight table.

    """
    if n_jobs == -1:
        n_jobs = int(os.cpu_count() / 2)  # type: ignore
        logger.info(" ParallelWghtGenEngine getting jobs from os.cpu_count()")
    logger.info(f"  ParallelWghtGenEngine using {n_jobs} jobs")

    # Chunk the largest, ship the smallest in full
    to_chunk, df_full = _get_chunks_for_parallel(source_df, target_df)

    # Spatial index query: Reindex on positional IDs
    to_workers = _chunk_dfs(
        gpd.GeoSeries(to_chunk.geometry.values, crs=to_chunk.crs),
        gpd.GeoSeries(df_full.geometry.values, crs=df_full.crs),
        n_jobs,
    )

    worker_out = _get_ids_for_parallel(n_jobs, to_workers)
    ids_src, ids_tgt = np.concatenate(worker_out).T

    # Intersection + area calculation
    chunks_to_intersection = _chunk_polys(
        np.vstack([ids_src, ids_tgt]).T, source_df.geometry, target_df.geometry, n_jobs
    )
    worker_out = _get_areas_for_parallel(n_jobs, chunks_to_intersection)
    areas = np.concatenate(worker_out)

    if source_type == "grid":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df.i_index.iloc[ids_src].values.astype(int).tolist(),
            source_df.j_index.iloc[ids_src].values.astype(int).tolist(),
            (areas.astype(float) / target_df.geometry[ids_tgt].area).tolist(),
        )
    elif source_type == "poly":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df[source_poly_idx[0]].iloc[ids_src].values.astype(object).tolist(),
            (areas.astype(float) / target_df.geometry[ids_tgt].area).tolist(),
        )


class DaskWghtGenEngine(CalcWeightEngine):
    """A distributed engine for calculating spatial intersection weights using Dask.

    This engine is designed for very large datasets and can scale computations
    across a Dask cluster. It partitions data and computations to be executed
    in parallel on multiple workers. The core logic is adapted from the
    `tobler` package.
    """

    def get_weight_components(
        self,
    ) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
        """Calculate weight components in a distributed manner using Dask.

        This method implements the weight calculation logic for a distributed
        execution environment. It calls the `_area_tables_binning_for_dask`
        worker function to perform the spatial intersections and calculate weights.

        Returns:
            A tuple of lists containing the components of the weight table.
            For "grid" source type, returns (target_ids, i_indices,
            j_indices, weights). For "poly" source type, returns
            (target_ids, source_ids, weights).

        """
        tsrt = time.perf_counter()
        if self.source_type == "grid":
            plist, ilist, jlist, wghtslist = _area_tables_binning_for_dask(
                source_df=self.source_poly,
                source_poly_idx=self.source_poly_idx,
                source_type=self.source_type,
                target_df=self.target_poly,
                target_poly_idx=self.target_poly_idx,
                n_jobs=self.jobs,
            )
        elif self.source_type == "poly":
            plist, splist, wghtslist = _area_tables_binning_for_dask(
                source_df=self.source_poly,
                source_poly_idx=self.source_poly_idx,
                source_type=self.source_type,
                target_df=self.target_poly,
                target_poly_idx=self.target_poly_idx,
                n_jobs=self.jobs,
            )
        tend = time.perf_counter()
        print(f"Weight gen finished in {tend - tsrt:0.4f} seconds")

        return (
            (plist, ilist, jlist, wghtslist)
            if self.source_type == "grid"
            else (plist, splist, wghtslist)
        )

    def get_weight_components_and_intesections(
        self,
    ) -> (
        tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
        | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
    ):
        """Calculate weight components and intersections using Dask.

        This method implements the distributed weight calculation logic, including
        the generation of intersection geometries. It calls the
        `_area_tables_binning_and_intersections_for_dask` worker function.

        Returns:
            A tuple containing the weight components and a GeoDataFrame of the
            intersection geometries.

        """
        tsrt = time.perf_counter()
        if self.source_type == "grid":
            (
                plist,
                ilist,
                jlist,
                wghtslist,
                gdf,
            ) = _area_tables_binning_and_intersections_for_dask(
                source_df=self.source_poly,
                source_poly_idx=self.source_poly_idx,
                source_type=self.source_type,
                target_df=self.target_poly,
                target_poly_idx=self.target_poly_idx,
                n_jobs=self.jobs,
            )
        elif self.source_type == "poly":
            (
                plist,
                splist,
                wghtslist,
                gdf,
            ) = _area_tables_binning_and_intersections_for_dask(
                source_df=self.source_poly,
                source_poly_idx=self.source_poly_idx,
                source_type=self.source_type,
                target_df=self.target_poly,
                target_poly_idx=self.target_poly_idx,
                n_jobs=self.jobs,
            )
        tend = time.perf_counter()
        print(f"Weight gen finished in {tend - tsrt:0.4f} seconds")

        return (
            (plist, ilist, jlist, wghtslist, gdf)
            if self.source_type == "grid"
            else (plist, splist, wghtslist, gdf)
        )


def _area_tables_binning_and_intersections_for_dask(
    source_df: gpd.GeoDataFrame,
    source_poly_idx: str,
    source_type: SOURCE_TYPES,
    target_df: gpd.GeoDataFrame,
    target_poly_idx: str,
    n_jobs: int = -1,
) -> (
    tuple[list[object], list[int], list[int], list[float], gpd.GeoDataFrame]
    | tuple[list[object], list[object], list[float], gpd.GeoDataFrame]
):
    """Calculate intersection tables and weights using Dask.

    This function orchestrates the distributed calculation of intersection
    geometries and their corresponding area weights. It partitions the input
    data and distributes the work across a Dask cluster.

    Args:
        source_df: GeoDataFrame of source polygons.
        source_poly_idx: Column name for unique IDs of source polygons.
        source_type: Type of the source geometry ('grid' or 'poly').
        target_df: GeoDataFrame of target polygons.
        target_poly_idx: Column name for unique IDs of target polygons.
        n_jobs: Number of Dask partitions to use.

    Returns:
        A tuple containing the weight components and a GeoDataFrame of the
        intersection geometries.

    """
    if n_jobs == -1:
        n_jobs = max(1, int((os.cpu_count() or 1) / 2))
        logger.info(" DaskWghtGenEngine getting jobs from os.cpu_count()")
    logger.info(f"  DaskWghtGenEngine using {n_jobs} jobs")

    # Chunk the largest, ship the smallest in full
    sdf, tdf = _get_chunks_for_dask(n_jobs, source_df, target_df)
    sdf.calculate_spatial_partitions()

    id_chunks = _ids_for_dask_generator(sdf=sdf, tdf=tdf)
    worker_out = _get_ids_for_dask(id_chunks)
    ids_src, ids_tgt = np.concatenate(worker_out).T

    # Intersection + area calculation
    chunks_to_intersection = _chunk_polys_dask(
        np.vstack([ids_src, ids_tgt]).T, source_df.geometry, target_df.geometry, n_jobs
    )

    worker_out = _get_areas_and_intersections_for_dask(n_jobs, chunks_to_intersection)
    areas = np.concatenate([item[0] for item in worker_out])
    inter_geom = np.concatenate([item[1] for item in worker_out])

    print("Processing intersections for output.")
    inter_sect = target_df.iloc[ids_tgt, :].set_geometry(inter_geom)
    weights = areas.astype(float) / target_df.geometry[ids_tgt].area
    inter_sect["weights"] = weights

    if source_type == "grid":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df.i_index.iloc[ids_src].values.astype(int).tolist(),
            source_df.j_index.iloc[ids_src].values.astype(int).tolist(),
            weights.tolist(),
            inter_sect,
        )
    elif source_type == "poly":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df[source_poly_idx[0]].iloc[ids_src].values.astype(object).tolist(),
            weights.tolist(),
            inter_sect,
        )


def _ids_for_dask_generator(
    sdf: dgpd.GeoDataFrame, tdf: dgpd.GeoDataFrame
) -> Generator[tuple[gpd.GeoSeries, gpd.GeoSeries], Any, Any]:
    """Generate chunks for Dask spatial queries.

    This generator iterates through partitions of the target Dask GeoDataFrame,
    finds the corresponding spatial chunk in the source GeoDataFrame, and
    yields pairs of GeoSeries for intersection queries.

    Args:
        sdf: The source Dask GeoDataFrame with a spatial partition.
        tdf: The target Dask GeoDataFrame.

    """
    for part in tdf.partitions:
        target_chunk = part.compute()
        bnds = target_chunk.total_bounds
        source_chunk = sdf.cx[bnds[0] : bnds[1], bnds[2] : bnds[3]].compute()
        yield (
            gpd.GeoSeries(
                source_chunk.geometry.values,
                index=source_chunk.index,
                crs=source_chunk.crs,
            ),
            gpd.GeoSeries(
                target_chunk.geometry.values,
                index=target_chunk.index,
                crs=target_chunk.crs,
            ),
        )


def _get_areas_and_intersections_for_dask(
    jobs: int,
    chunks_to_intersection: Generator[tuple[npt.NDArray[np.object_], npt.NDArray[np.object_]], Any, Any],
) -> list[tuple[npt.NDArray[np.float64], npt.NDArray[np.object_]]]:
    """Compute intersection areas and geometries for Dask chunks.

    Args:
        jobs: The number of Dask partitions to use.
        chunks_to_intersection: A generator that yields tuples of geometry chunks.

    Returns:
        A list of tuples, where each tuple contains the areas (NumPy array of
        floats) and intersections (NumPy array of geometry objects) for a chunk.

    """
    b = db.from_sequence(chunks_to_intersection, npartitions=jobs)  # type: ignore
    b = b.map(_intersect_area_on_chunk_dask)
    return b.compute()


def _get_areas_for_dask(
    jobs: int,
    chunks_to_intersection: Generator[tuple[npt.ArrayLike, npt.ArrayLike], None, None],
) -> list[gpd.GeoSeries]:
    """Compute intersection areas for Dask chunks.

    Args:
        jobs: Number of Dask partitions to use.
        chunks_to_intersection: A generator yielding pairs of geometry arrays
            to be intersected.

    Returns:
        A list of GeoSeries containing intersection areas, one per chunk.

    """
    b = db.from_sequence(chunks_to_intersection, npartitions=jobs)  # type: ignore
    b = b.map(_area_on_chunk_dask)
    return b.compute()


def _get_ids_for_dask(to_workers: Generator[tuple[gpd.GeoSeries, gpd.GeoSeries], Any, Any]) -> list[np.ndarray]:
    """Retrieve intersecting geometry IDs using a Dask Bag.

    Args:
        to_workers: A generator that yields tuples of GeoSeries to query.

    Returns:
        A list of NumPy arrays, where each array contains pairs of
        intersecting geometry IDs.

    """
    b = db.from_sequence(to_workers)  # type: ignore
    result = b.map(_index_n_query_dask)
    return result.compute()


def _area_tables_binning_for_dask(
    source_df: gpd.GeoDataFrame,
    source_poly_idx: str,
    source_type: SOURCE_TYPES,
    target_df: gpd.GeoDataFrame,
    target_poly_idx: str,
    n_jobs: int = -1,
) -> tuple[list[object], list[int], list[int], list[float]] | tuple[list[object], list[object], list[float]]:
    """Calculate intersection tables and weights using Dask.

    This function orchestrates the distributed calculation of area weights, but
    does not generate the intersection geometries. It partitions the input
    data and distributes the work across a Dask cluster.

    Args:
        source_df: GeoDataFrame of source polygons.
        source_poly_idx: Column name for unique IDs of source polygons.
        source_type: Type of the source geometry ('grid' or 'poly').
        target_df: GeoDataFrame of target polygons.
        target_poly_idx: Column name for unique IDs of target polygons.
        n_jobs: Number of Dask partitions to use.

    Returns:
        A tuple of lists containing the components of the weight table.

    """
    if n_jobs == -1:
        n_jobs = max(1, int((os.cpu_count() or 1) / 2))
        logger.info(" DaskWghtGenEngine getting jobs from os.cpu_count()")
    logger.info(f"  DaskWghtGenEngine using {n_jobs} jobs")

    # Chunk the largest, ship the smallest in full
    sdf, tdf = _get_chunks_for_dask(n_jobs, source_df, target_df)
    sdf.calculate_spatial_partitions()

    id_chunks = _ids_for_dask_generator(sdf=sdf, tdf=tdf)
    worker_out = _get_ids_for_dask(id_chunks)
    ids_src, ids_tgt = np.concatenate(worker_out).T

    # Intersection + area calculation
    chunks_to_intersection = _chunk_polys_dask(
        np.vstack([ids_src, ids_tgt]).T, source_df.geometry, target_df.geometry, n_jobs
    )

    worker_out = _get_areas_for_dask(n_jobs, chunks_to_intersection)
    areas = np.concatenate(worker_out)
    if source_type == "grid":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df.i_index.iloc[ids_src].values.astype(int).tolist(),
            source_df.j_index.iloc[ids_src].values.astype(int).tolist(),
            (areas.astype(float) / target_df.geometry[ids_tgt].area).tolist(),
        )
    elif source_type == "poly":
        return (
            target_df[target_poly_idx].iloc[ids_tgt].values.astype(object).tolist(),
            source_df[source_poly_idx[0]].iloc[ids_src].values.astype(object).tolist(),
            (areas.astype(float) / target_df.geometry[ids_tgt].area).tolist(),
        )


def _get_chunks_for_dask(
    jobs: int, source_df: gpd.GeoDataFrame, target_df: gpd.GeoDataFrame
) -> tuple[dgpd.GeoDataFrame, dgpd.GeoDataFrame]:
    """Partition GeoDataFrames into chunks for parallel processing with Dask.

    This function takes GeoDataFrames and the number of jobs, and returns
    Dask GeoDataFrames partitioned into 'npartitions' equal to the number of jobs.

    Args:
        jobs (int): The number of jobs (partitions) for parallel processing.
        source_df (gpd.GeoDataFrame): The source GeoDataFrame to be partitioned.
        target_df (gpd.GeoDataFrame): The target GeoDataFrame to be partitioned.

    Returns:
        Tuple[dgpd.GeoDataFrame, dgpd.GeoDataFrame]: A tuple containing the partitioned
        source and target Dask GeoDataFrames.

    """
    return (
        dgpd.from_geopandas(source_df, npartitions=jobs),
        dgpd.from_geopandas(target_df, npartitions=jobs),
    )


def _chunk_dfs(
    geoms_to_chunk: gpd.GeoSeries, geoms_full: gpd.GeoSeries, n_jobs: int
) -> Generator[tuple[gpd.GeoSeries, gpd.GeoSeries], Any, Any]:
    """Partition GeoSeries into chunks for parallel processing.

    This function takes two GeoSeries and the number of jobs, and yields
    tuples of GeoSeries chunks for parallel processing. The 'geoms_to_chunk'
    GeoSeries is divided into 'n_jobs' number of chunks, while 'geoms_full'
    is passed as is in each tuple.

    Args:
        geoms_to_chunk (gpd.GeoSeries): The GeoSeries to be chunked.
        geoms_full (gpd.GeoSeries): The full GeoSeries to be included in each chunk.
        n_jobs (int): The number of jobs (chunks) for parallel processing.

    Yields:
        Generator[Tuple[gpd.GeoSeries, gpd.GeoSeries], Any, Any]: A generator that yields
        tuples containing a chunk of 'geoms_to_chunk' and the full 'geoms_full' GeoSeries.

    """
    chunk_size = geoms_to_chunk.shape[0] // n_jobs + 1
    for i in range(n_jobs):
        start = i * chunk_size
        yield geoms_to_chunk.iloc[start : start + chunk_size], geoms_full


def _index_n_query(geoms1: gpd.GeoSeries, geoms2: gpd.GeoSeries) -> npt.ArrayLike:
    """Retrieve intersecting geometry IDs using spatial indexing.

    This function takes two GeoSeries, builds an STRTree spatial index on the
    first GeoSeries, and then queries the second GeoSeries to find intersecting
    geometries. The function returns an array of tuples containing the global IDs
    of intersecting geometries from both GeoSeries.

    Args:
        geoms1 (gpd.GeoSeries): The first GeoSeries, used for building the STRTree spatial index.
        geoms2 (gpd.GeoSeries): The second GeoSeries, used for querying against the spatial index.

    Returns:
        npt.ArrayLike: A NumPy array containing tuples of global IDs for intersecting geometries.
                       Each tuple contains two elements:
                       - The global ID from 'geoms1'
                       - The global ID from 'geoms2'
    """
    # Pick largest for STRTree, query the smallest

    # Build tree + query
    qry_polyids, tree_polyids = geoms1.sindex.query(geoms2, predicate="intersects")
    # Remap IDs to global
    large_global_ids = geoms1.iloc[tree_polyids].index.values
    small_global_ids = geoms2.iloc[qry_polyids].index.values

    return np.array([large_global_ids, small_global_ids]).T


def _index_n_query_dask(bag: tuple[gpd.GeoSeries, gpd.GeoSeries]) -> npt.ArrayLike:
    """Retrieve intersecting geometry IDs for parallel processing using Dask.

    This function takes a tuple of two GeoSeries, builds an STRTree spatial index on the
    first GeoSeries, and then queries the second GeoSeries to find intersecting
    geometries. The function returns an array of tuples containing the global IDs
    of intersecting geometries from both GeoSeries.

    Args:
        bag (Tuple[gpd.GeoSeries, gpd.GeoSeries]): A tuple containing two GeoSeries.
            - bag[0]: The first GeoSeries, used for building the STRTree spatial index.
            - bag[1]: The second GeoSeries, used for querying against the spatial index.

    Returns:
        npt.ArrayLike: A NumPy array containing tuples of global IDs for intersecting geometries.
                       Each tuple contains two elements:
                       - The global ID from 'bag[0]'
                       - The global ID from 'bag[1]'

    """
    # Build tree + query
    source_df = bag[0]
    target_df = bag[1]
    qry_polyids, tree_polyids = source_df.sindex.query(target_df, predicate="intersects")
    # Remap IDs to global
    large_global_ids = source_df.iloc[tree_polyids].index.values
    small_global_ids = target_df.iloc[qry_polyids].index.values

    return np.array([large_global_ids, small_global_ids]).T


def _chunk_polys(
    id_pairs: npt.NDArray[np.int_],
    geoms_left: gpd.GeoSeries,
    geoms_right: gpd.GeoSeries,
    n_jobs: int,
) -> Generator[tuple[npt.ArrayLike, npt.ArrayLike], Any, Any]:
    """Divide geometry pairs into chunks for parallel processing.

    This function takes an array of ID pairs and two GeoSeries, and divides them into
    smaller chunks for parallel processing. The function yields tuples containing
    chunks of geometries from both GeoSeries based on the provided ID pairs.

    Args:
        id_pairs (npt.NDArray[np.int_]): A NumPy array of shape (N, 2) containing pairs of IDs
                                         that correspond to intersecting geometries in
                                         'geoms_left' and 'geoms_right'.
        geoms_left (gpd.GeoSeries): The first GeoSeries containing geometries.
        geoms_right (gpd.GeoSeries): The second GeoSeries containing geometries.
        n_jobs (int): Number of chunks to create for parallel processing.

    Yields:
        Generator[Tuple[npt.ArrayLike, npt.ArrayLike], Any, Any]: A generator that yields
                                                                  tuples of NumPy arrays.
                                                                  Each tuple contains:
                                                                  - A chunk of geometries from 'geoms_left'
                                                                  - A chunk of geometries from 'geoms_right'

    """
    chunk_size = id_pairs.shape[0] // n_jobs + 1
    for i in range(n_jobs):
        start = i * chunk_size
        chunk1 = np.asarray(geoms_left.values[id_pairs[start : start + chunk_size, 0]])
        chunk2 = np.asarray(geoms_right.values[id_pairs[start : start + chunk_size, 1]])
        yield chunk1, chunk2


def _chunk_polys_dask(
    id_pairs: npt.NDArray[np.int_],
    geoms_left: gpd.GeoSeries,
    geoms_right: gpd.GeoSeries,
    n_jobs: int,
) -> Generator[tuple[npt.ArrayLike, npt.ArrayLike], Any, Any]:
    """Chunk polys for parallel processing."""
    chunk_size = id_pairs.shape[0] // n_jobs + 1
    for i in range(n_jobs):
        start = i * chunk_size
        chunk1 = np.asarray(geoms_left.values[id_pairs[start : start + chunk_size, 0]])
        chunk2 = np.asarray(geoms_right.values[id_pairs[start : start + chunk_size, 1]])
        yield (chunk1, chunk2)


def _intersect_area_on_chunk(geoms1: gpd.GeoSeries, geoms2: gpd.GeoSeries) -> tuple[gpd.GeoSeries, gpd.GeoSeries]:
    """Compute the intersection and area between two GeoSeries of geometries.

    This function calculates the intersection of two GeoSeries of geometries and
    returns the area of the intersection along with the intersected geometries.

    Optimization: Source polygons fully contained within target polygons
    use source geometry/area directly, avoiding expensive intersection() calls.

    Args:
        geoms1 (gpd.GeoSeries): The first set of geometries (source).
        geoms2 (gpd.GeoSeries): The second set of geometries (target).

    Returns:
        Tuple[gpd.GeoSeries, gpd.GeoSeries]: A tuple containing:
            - A GeoSeries of areas of the intersected geometries.
            - A GeoSeries of the intersected geometries.

    """
    # Partition into contained (cheap) vs boundary (expensive) pairs
    contained_mask = within(geoms1, geoms2)
    n_total = len(geoms1)

    f_intersect = np.empty(n_total, dtype=object)
    intersection_areas = np.empty(n_total, dtype=np.float64)

    # Contained pairs: intersection geometry = source geometry
    f_intersect[contained_mask] = geoms1[contained_mask]
    intersection_areas[contained_mask] = area(geoms1[contained_mask])

    # Boundary pairs: compute actual intersection
    if (~contained_mask).any():
        boundary_intersect = intersection(geoms1[~contained_mask], geoms2[~contained_mask])
        f_intersect[~contained_mask] = boundary_intersect
        intersection_areas[~contained_mask] = area(boundary_intersect)

    return intersection_areas, f_intersect


def _area_on_chunk(geoms1: gpd.GeoSeries, geoms2: gpd.GeoSeries) -> gpd.GeoSeries:
    """Calculate intersection areas between two GeoSeries.

    This function computes the areas of intersections between two sets of geometries
    using the intersection operation. It is typically used in parallel processing
    of spatial data.

    Optimization: Source polygons fully contained within target polygons
    use source.area directly, avoiding expensive intersection() calls.

    Args:
        geoms1 (gpd.GeoSeries): The first set of geometries (source).
        geoms2 (gpd.GeoSeries): The second set of geometries (target).

    Returns:
        gpd.GeoSeries: A GeoSeries containing the areas of intersections.

    """
    # Partition into contained (cheap) vs boundary (expensive) pairs
    contained_mask = within(geoms1, geoms2)
    n_total = len(geoms1)
    intersection_areas = np.empty(n_total, dtype=np.float64)

    # Contained pairs: use source area directly
    intersection_areas[contained_mask] = area(geoms1[contained_mask])

    # Boundary pairs: compute actual intersection
    if (~contained_mask).any():
        intersection_areas[~contained_mask] = area(
            intersection(geoms1[~contained_mask], geoms2[~contained_mask])
        )

    return intersection_areas


def _area_on_chunk_dask(dask_bag: tuple[npt.ArrayLike, npt.ArrayLike]) -> gpd.GeoSeries:
    """Get intersection areas.

    Optimization: Source polygons fully contained within target polygons
    use source.area directly, avoiding expensive intersection() calls.
    """
    geoms1 = dask_bag[0]
    geoms2 = dask_bag[1]

    # Partition into contained (cheap) vs boundary (expensive) pairs
    contained_mask = within(geoms1, geoms2)
    n_total = len(geoms1)
    intersection_areas = np.empty(n_total, dtype=np.float64)

    # Contained pairs: use source area directly
    intersection_areas[contained_mask] = area(geoms1[contained_mask])

    # Boundary pairs: compute actual intersection
    if (~contained_mask).any():
        intersection_areas[~contained_mask] = area(
            intersection(geoms1[~contained_mask], geoms2[~contained_mask])
        )

    return intersection_areas


def _intersect_area_on_chunk_dask(
    dask_bag: tuple[npt.NDArray[np.object_], npt.NDArray[np.object_]],
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.object_]]:
    """Compute the intersection and area between two arrays of geometries using Dask.

    This function calculates the intersection and area for pairs of geometries within
    Dask bags, enabling parallel computation. It returns the areas and the intersected
    geometries.

    Optimization: Source polygons fully contained within target polygons
    use source geometry/area directly, avoiding expensive intersection() calls.

    Args:
        dask_bag (Tuple[npt.NDArray[np.object_], npt.NDArray[np.object_]]): A tuple containing two
            NumPy arrays of geometry objects.

    Returns:
        Tuple[npt.NDArray[np.float64], npt.NDArray[np.object_]]: A tuple containing:
            - The areas of the intersected geometries.
            - The intersected geometries.

    """
    geoms1 = dask_bag[0]
    geoms2 = dask_bag[1]

    # Partition into contained (cheap) vs boundary (expensive) pairs
    contained_mask = within(geoms1, geoms2)
    n_total = len(geoms1)

    f_intersect = np.empty(n_total, dtype=object)
    intersection_areas = np.empty(n_total, dtype=np.float64)

    # Contained pairs: intersection geometry = source geometry
    f_intersect[contained_mask] = geoms1[contained_mask]
    intersection_areas[contained_mask] = area(geoms1[contained_mask])

    # Boundary pairs: compute actual intersection
    if (~contained_mask).any():
        boundary_intersect = intersection(geoms1[~contained_mask], geoms2[~contained_mask])
        f_intersect[~contained_mask] = boundary_intersect
        intersection_areas[~contained_mask] = area(boundary_intersect)

    return intersection_areas, f_intersect
