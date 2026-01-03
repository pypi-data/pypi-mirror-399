"""Optimized cell polygon generation for regular projected grids."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import CRS
from shapely import box


def _get_cells_poly_fast(
    xr_a: xr.Dataset | xr.DataArray,
    x: str,
    y: str,
    crs_in: str | int | CRS,
) -> gpd.GeoDataFrame:
    """Get cell polygons for a regular projected grid with 1D coordinates.

    This is an optimized version of _get_cells_poly for the common case where:
    - The dataset uses a projected CRS (not curvilinear)
    - The x and y coordinates are 1-dimensional arrays

    For regular grids, cell boundaries are simply the midpoints between
    adjacent coordinate values, which can be computed efficiently using
    vectorized operations.

    Args:
        xr_a: Source xarray dataset or dataarray.
        x: Name of the x coordinate variable.
        y: Name of the y coordinate variable.
        crs_in: Projection of the xarray object.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame of grid-cell polygons with i_index
        and j_index columns matching the original _get_cells_poly output.

    """
    # Extract 1D coordinate arrays
    x_coords = xr_a[x].values
    y_coords = xr_a[y].values

    # Compute cell boundaries as midpoints between coordinates
    # For interior cells (excluding first and last row/column)
    x_bounds = (x_coords[:-1] + x_coords[1:]) / 2
    y_bounds = (y_coords[:-1] + y_coords[1:]) / 2

    # Interior cells correspond to indices 1 to n-2 (matching original function)
    # Original uses range(1, shape-1) for both i and j
    n_y = len(y_coords)
    n_x = len(x_coords)

    # Number of interior cells
    n_interior_y = n_y - 2  # rows
    n_interior_x = n_x - 2  # cols
    numcells = n_interior_y * n_interior_x

    # Create index arrays for interior cells (i=1 to n_y-2, j=1 to n_x-2)
    # Matches original: for i in range(1, lon.shape[0] - 1): for j in range(1, lon.shape[1] - 1)
    i_indices, j_indices = np.meshgrid(
        np.arange(1, n_y - 1),
        np.arange(1, n_x - 1),
        indexing='ij'
    )
    i_index = i_indices.ravel().astype(float)
    j_index = j_indices.ravel().astype(float)

    # For each interior cell (i, j), the bounding box is:
    # x: from x_bounds[j-1] to x_bounds[j]
    # y: from y_bounds[i-1] to y_bounds[i]
    # This matches the centroid-based approach for regular grids

    # Vectorized extraction of bounds for all cells
    # j-1 and j map to x_bounds indices 0..n_x-3 and 1..n_x-2
    # i-1 and i map to y_bounds indices 0..n_y-3 and 1..n_y-2
    j_flat = j_indices.ravel()
    i_flat = i_indices.ravel()

    x_min = x_bounds[j_flat - 1]
    x_max = x_bounds[j_flat]
    y_min = y_bounds[i_flat - 1]
    y_max = y_bounds[i_flat]

    # Create boxes using shapely's vectorized box function
    polygons = box(x_min, y_min, x_max, y_max)

    # Build the GeoDataFrame
    df = pd.DataFrame({
        "i_index": i_index,
        "j_index": j_index
    })
    index = np.arange(numcells)

    return gpd.GeoDataFrame(df, index=index, geometry=polygons, crs=crs_in)


def estimate_memory_gb(n_x: int, n_y: int) -> dict[str, float]:
    """Estimate memory usage for _get_cells_poly_fast.

    Args:
        n_x: Number of x coordinates.
        n_y: Number of y coordinates.

    Returns:
        Dictionary with memory estimates in GB.
    """
    n_interior = (n_x - 2) * (n_y - 2)

    # Bounds arrays: 4 float64 arrays
    bounds_gb = 4 * n_interior * 8 / (1024**3)

    # Index arrays: 2 float64 arrays
    index_gb = 2 * n_interior * 8 / (1024**3)

    # Shapely geometries: rough estimate ~250 bytes per box polygon
    geom_gb = n_interior * 250 / (1024**3)

    # DataFrame overhead
    df_overhead_gb = 0.5  # Rough estimate

    total_gb = bounds_gb + index_gb + geom_gb + df_overhead_gb

    return {
        "n_cells": n_interior,
        "bounds_arrays_gb": round(bounds_gb, 2),
        "index_arrays_gb": round(index_gb, 2),
        "geometries_gb": round(geom_gb, 2),
        "total_estimated_gb": round(total_gb, 2),
    }


def _get_cells_poly_chunked(
    xr_a: xr.Dataset | xr.DataArray,
    x: str,
    y: str,
    crs_in: str | int | CRS,
    chunk_size: int = 100_000,
) -> Iterator[gpd.GeoDataFrame]:
    """Generate cell polygons in memory-efficient chunks.

    This generator yields chunks of the grid cells, allowing processing
    of very large grids without loading all geometries into memory at once.

    Args:
        xr_a: Source xarray dataset or dataarray.
        x: Name of the x coordinate variable.
        y: Name of the y coordinate variable.
        crs_in: Projection of the xarray object.
        chunk_size: Maximum number of cells per chunk (default: 100,000).

    Yields:
        gpd.GeoDataFrame: Chunks of grid-cell polygons.
    """
    x_coords = xr_a[x].values
    y_coords = xr_a[y].values

    x_bounds = (x_coords[:-1] + x_coords[1:]) / 2
    y_bounds = (y_coords[:-1] + y_coords[1:]) / 2

    n_y = len(y_coords)
    n_x = len(x_coords)
    n_interior_y = n_y - 2
    n_interior_x = n_x - 2
    total_cells = n_interior_y * n_interior_x

    # Process in chunks
    for start in range(0, total_cells, chunk_size):
        end = min(start + chunk_size, total_cells)
        chunk_len = end - start

        # Calculate i, j indices for this chunk
        i_index = np.empty(chunk_len, dtype=float)
        j_index = np.empty(chunk_len, dtype=float)
        x_min = np.empty(chunk_len, dtype=float)
        x_max = np.empty(chunk_len, dtype=float)
        y_min = np.empty(chunk_len, dtype=float)
        y_max = np.empty(chunk_len, dtype=float)

        for local_idx, flat_idx in enumerate(range(start, end)):
            # Convert flat index to i, j (matching original iteration order)
            i = flat_idx // n_interior_x + 1
            j = flat_idx % n_interior_x + 1

            i_index[local_idx] = i
            j_index[local_idx] = j
            x_min[local_idx] = x_bounds[j - 1]
            x_max[local_idx] = x_bounds[j]
            y_min[local_idx] = y_bounds[i - 1]
            y_max[local_idx] = y_bounds[i]

        polygons = box(x_min, y_min, x_max, y_max)
        df = pd.DataFrame({"i_index": i_index, "j_index": j_index})
        chunk_index = np.arange(start, end)

        yield gpd.GeoDataFrame(df, index=chunk_index, geometry=polygons, crs=crs_in)


def _get_cells_poly_fast(
    xr_a: xr.Dataset | xr.DataArray,
    x: str,
    y: str,
    crs_in: str | int | CRS,
    mode: Literal["full", "chunked"] = "full",
    chunk_size: int = 100_000,
    memory_limit_gb: float | None = None,
) -> gpd.GeoDataFrame | Iterator[gpd.GeoDataFrame]:
    """Get cell polygons for a regular projected grid with 1D coordinates.

    This is an optimized version of _get_cells_poly for the common case where:
    - The dataset uses a projected CRS (not curvilinear)
    - The x and y coordinates are 1-dimensional arrays

    For regular grids, cell boundaries are simply the midpoints between
    adjacent coordinate values, which can be computed efficiently using
    vectorized operations.

    Args:
        xr_a: Source xarray dataset or dataarray.
        x: Name of the x coordinate variable.
        y: Name of the y coordinate variable.
        crs_in: Projection of the xarray object.
        mode: "full" returns complete GeoDataFrame, "chunked" returns iterator.
        chunk_size: Cells per chunk when mode="chunked" (default: 100,000).
        memory_limit_gb: If set, automatically use chunked mode if estimated
            memory exceeds this limit.

    Returns:
        gpd.GeoDataFrame or Iterator[gpd.GeoDataFrame] depending on mode.

    Raises:
        MemoryError: If mode="full" and estimated memory exceeds memory_limit_gb.
    """
    n_x = len(xr_a[x])
    n_y = len(xr_a[y])

    # Check memory if limit specified
    if memory_limit_gb is not None:
        mem_est = estimate_memory_gb(n_x, n_y)
        if mem_est["total_estimated_gb"] > memory_limit_gb:
            if mode == "full":
                raise MemoryError(
                    f"Estimated memory ({mem_est['total_estimated_gb']:.1f} GB) exceeds "
                    f"limit ({memory_limit_gb} GB). Use mode='chunked' or increase limit."
                )

    if mode == "chunked":
        return _get_cells_poly_chunked(xr_a, x, y, crs_in, chunk_size)

    # Full mode - original optimized implementation
    try:
        x_coords = xr_a[x].values
        y_coords = xr_a[y].values

        x_bounds = (x_coords[:-1] + x_coords[1:]) / 2
        y_bounds = (y_coords[:-1] + y_coords[1:]) / 2

        n_interior_y = n_y - 2
        n_interior_x = n_x - 2
        numcells = n_interior_y * n_interior_x

        i_indices, j_indices = np.meshgrid(
            np.arange(1, n_y - 1),
            np.arange(1, n_x - 1),
            indexing='ij'
        )
        i_index = i_indices.ravel().astype(float)
        j_index = j_indices.ravel().astype(float)

        j_flat = j_indices.ravel()
        i_flat = i_indices.ravel()

        x_min = x_bounds[j_flat - 1]
        x_max = x_bounds[j_flat]
        y_min = y_bounds[i_flat - 1]
        y_max = y_bounds[i_flat]

        polygons = box(x_min, y_min, x_max, y_max)

        df = pd.DataFrame({
            "i_index": i_index,
            "j_index": j_index
        })
        index = np.arange(numcells)

        return gpd.GeoDataFrame(df, index=index, geometry=polygons, crs=crs_in)

    except MemoryError as e:
        mem_est = estimate_memory_gb(n_x, n_y)
        raise MemoryError(
            f"Ran out of memory creating {mem_est['n_cells']:,} grid cells "
            f"(estimated {mem_est['total_estimated_gb']:.1f} GB required). "
            f"Use mode='chunked' to process the grid incrementally with bounded memory, "
            f"or reduce chunk_size for finer-grained processing. Example:\n"
            f"  for chunk in _get_cells_poly_fast(ds, x, y, crs, mode='chunked', chunk_size=100000):\n"
            f"      process(chunk)"
        ) from e
