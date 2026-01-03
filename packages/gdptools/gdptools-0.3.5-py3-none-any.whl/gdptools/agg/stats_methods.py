"""Statistical Methods for Area-Weighted Aggregation.

This module defines a collection of statistical methods implemented as dataclasses.
These classes are used by the aggregation engines (`agg_engines.py`) to perform
various area-weighted calculations, such as mean, median, standard deviation,
and sum.

Each class inherits from the `StatsMethod` abstract base class and implements
a `get_stat` method to compute a specific statistic. Both standard and
masked (NaN-ignoring) versions of the statistics are provided.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt


@dataclass  # type: ignore[misc]
class StatsMethod(ABC):
    """Abstract base class for calculating area-weighted statistics.

    This class defines the interface for statistical methods used in spatial
    aggregation. Each subclass implements a specific statistical calculation.

    Attributes:
        array (npt.NDArray): A 2D array of gridded data values for a target
            polygon, with dimensions (time, grid_cells).
        weights (npt.NDArray[np.double]): A 1D array of weights corresponding
            to each grid cell.
        def_val (Any): The default value to use for missing or invalid results.

    """

    array: npt.NDArray  # type: ignore
    weights: npt.NDArray[np.double]
    def_val: Any

    @abstractmethod
    def get_stat(
        self,
    ) -> npt.NDArray[np.int_ | np.double]:
        """Abstract method for calculating the statistic."""
        pass


@dataclass
class MAWeightedMean(StatsMethod):
    """Calculates the area-weighted mean, ignoring NaN values."""

    def get_stat(self) -> npt.NDArray[np.int_ | np.double]:
        """Calculate the masked weighted mean.

        Calculates the weighted mean of the input array, handling missing
        values (NaNs) by zeroing out their weights. Uses optimized NumPy
        operations instead of masked arrays for better performance.

        Returns:
            A 1D NumPy array containing the masked weighted mean for each time step.

        """
        # Create effective weights: zero out weights where values are NaN
        nan_mask = np.isnan(self.array)
        effective_weights = np.where(nan_mask, 0.0, self.weights)

        # Replace NaN with 0 for safe multiplication
        safe_array = np.where(nan_mask, 0.0, self.array)

        # Weighted sum and weight sum per row
        weighted_sum = np.sum(safe_array * effective_weights, axis=1)
        weight_sum = np.sum(effective_weights, axis=1)

        # Compute mean, returning 0.0 for all-NaN rows (legacy behavior)
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.where(weight_sum > 0, weighted_sum / weight_sum, 0.0)

        return result


@dataclass
class WeightedMean(StatsMethod):
    """Calculates the area-weighted mean."""

    def get_stat(self) -> npt.NDArray[np.int_ | np.double]:
        """Calculate the weighted mean.

        This method does not explicitly handle NaNs; they may propagate in
        the calculation.

        Returns:
            A 1D NumPy array containing the weighted mean for each time step.

        """
        try:
            tmp = np.average(self.array, weights=self.weights, axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return np.nan_to_num(tmp, nan=self.def_val)


@dataclass
class WeightedStd(StatsMethod):
    """Calculates the area-weighted standard deviation."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the weighted standard deviation.

        This method does not explicitly handle NaNs; they may propagate in
        the calculation.

        Returns:
            A 1D NumPy array of the weighted standard deviation for each time step.

        """
        try:
            avg = np.average(self.array, weights=self.weights, axis=1)
            variance = np.average((self.array - avg[:, None]) ** 2, weights=self.weights, axis=1)
            tmp = np.sqrt(variance)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return np.nan_to_num(tmp, nan=self.def_val)


@dataclass
class MAWeightedStd(StatsMethod):
    """Calculates the area-weighted standard deviation, ignoring NaN values."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the masked weighted standard deviation.

        Calculates the weighted standard deviation of the input array,
        handling missing values (NaNs) by zeroing out their weights.
        Uses optimized NumPy operations instead of masked arrays.

        Returns:
            A 1D NumPy array of the masked weighted standard deviation for each time step.

        """
        # Create effective weights: zero out weights where values are NaN
        nan_mask = np.isnan(self.array)
        effective_weights = np.where(nan_mask, 0.0, self.weights)
        safe_array = np.where(nan_mask, 0.0, self.array)

        # Sum of effective weights per row
        weight_sum = np.sum(effective_weights, axis=1)

        with np.errstate(divide="ignore", invalid="ignore"):
            # Weighted mean
            weighted_sum = np.sum(safe_array * effective_weights, axis=1)
            mean = np.where(weight_sum > 0, weighted_sum / weight_sum, 0.0)

            # Weighted variance: sum(w * (x - mean)^2) / sum(w)
            sq_dev = (safe_array - mean[:, None]) ** 2
            weighted_sq_dev_sum = np.sum(sq_dev * effective_weights, axis=1)
            variance = np.where(weight_sum > 0, weighted_sq_dev_sum / weight_sum, 0.0)

        # Standard deviation (returns 0.0 for all-NaN rows - legacy behavior)
        return np.sqrt(variance)


@dataclass
class MAWeightedMedian(StatsMethod):
    """Calculates the area-weighted median, ignoring NaN values."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the masked weighted median.

        Computes the weighted median for each time step, properly handling
        NaN values by excluding them from the calculation. Uses an optimized
        vectorized approach that avoids the overhead of np.apply_along_axis.

        The algorithm:
        1. For each time step, filter out NaN values
        2. Sort valid values and their corresponding weights
        3. Compute cumulative weights and CDF positions
        4. Interpolate to find the value at the 0.5 quantile

        Returns:
            A 1D NumPy array of masked weighted medians, one for each time step.

        """
        n_time, n_cells = self.array.shape
        result = np.empty(n_time, dtype=np.float64)

        for t in range(n_time):
            row = self.array[t]
            valid_mask = ~np.isnan(row)

            if not valid_mask.any():
                result[t] = self.def_val
                continue

            valid_vals = row[valid_mask]
            valid_weights = self.weights[valid_mask]

            # Sort by (value, weight) to match original behavior for duplicate values
            # This uses lexsort which sorts by the last key first, so we pass
            # (weights, values) to sort primarily by values, then by weights
            sort_idx = np.lexsort((valid_weights, valid_vals))
            sorted_vals = valid_vals[sort_idx]
            sorted_wts = valid_weights[sort_idx]

            # Cumulative sum for CDF
            cumsum = np.cumsum(sorted_wts)
            total = cumsum[-1]

            # Position in CDF (midpoint of each weight interval)
            p = (cumsum - sorted_wts / 2) / total

            # Interpolate to find value at 0.5
            result[t] = np.interp(0.5, p, sorted_vals)

        return result


@dataclass
class WeightedMedian(StatsMethod):
    """Calculates the area-weighted median."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the weighted median.

        Computes the weighted median for each time step. If any NaN values
        are present in a time step, returns the default value for that step.
        Uses an optimized vectorized approach that avoids the overhead of
        np.apply_along_axis.

        The algorithm:
        1. For each time step, check for NaN values
        2. Sort values and their corresponding weights
        3. Compute cumulative weights and CDF positions
        4. Interpolate to find the value at the 0.5 quantile

        Returns:
            A 1D NumPy array of weighted medians, one for each time step.

        """
        n_time, n_cells = self.array.shape
        result = np.empty(n_time, dtype=np.float64)

        for t in range(n_time):
            row = self.array[t]

            # Return default value if any NaNs are present
            if np.isnan(row).any():
                result[t] = self.def_val
                continue

            # Sort by (value, weight) to match original behavior for duplicate values
            sort_idx = np.lexsort((self.weights, row))
            sorted_vals = row[sort_idx]
            sorted_wts = self.weights[sort_idx]

            # Cumulative sum for CDF
            cumsum = np.cumsum(sorted_wts)
            total = cumsum[-1]

            # Position in CDF (midpoint of each weight interval)
            p = (cumsum - sorted_wts / 2) / total

            # Interpolate to find value at 0.5
            result[t] = np.interp(0.5, p, sorted_vals)

        return result


@dataclass
class MACount(StatsMethod):
    """Calculates the count of valid (non-NaN) data cells with non-zero weights."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.int_]:
        """Count masked grid cells.

        Counts the number of grid cells that are not NaN and have a
        corresponding non-zero weight.

        Returns:
            A 1D NumPy array of counts, one for each time step.

        """
        try:
            masked = np.ma.masked_array(self.array, np.isnan(self.array))
            weight_mask = self.weights == 0
            tmp = np.ma.masked_array(masked, mask=weight_mask | masked.mask).count(axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), 0)
        return tmp


@dataclass
class Count(StatsMethod):
    """Calculates the count of all data cells with non-zero weights."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.int_]:
        """Count grid cells.

        Counts the number of grid cells with non-zero weights. Note: This
        method returns a single scalar value, not an array per time step.

        Returns:
            The total count of grid cells with non-zero weights.

        """
        try:
            tmp = np.ma.masked_array(self.weights, mask=self.weights == 0).count()
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), 0)
        return tmp


@dataclass
class MASum(StatsMethod):
    """Calculates the area-weighted sum, ignoring NaN values."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the masked sum.

        Calculates the weighted sum of the input array, handling missing
        values (NaNs) using np.nansum for better performance.

        Returns:
            A 1D NumPy array of the masked weighted sum for each time step.

        """
        # Use np.nansum which treats NaN as zero in the sum
        return np.nansum(self.array * self.weights, axis=1)


@dataclass
class Sum(StatsMethod):
    """Calculates the area-weighted sum."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the sum.

        Calculates the weighted sum of the input array. This method does not
        explicitly handle NaNs.

        Returns:
            A 1D NumPy array of the weighted sum for each time step.

        """
        try:
            tmp = np.sum(self.array * self.weights, axis=1)
        except KeyError:
            numpts = len(self.weights)
            tmp = np.full((numpts), 0)
        return np.nan_to_num(tmp, nan=self.def_val)


@dataclass
class MAMin(StatsMethod):
    """Finds the minimum value, ignoring NaN values."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the masked minimum.

        Finds the minimum value in the array for each time step, ignoring NaNs.
        Uses np.nanmin for better performance than masked arrays.
        Note: This calculation is not weighted.

        Returns:
            A 1D NumPy array of the minimum value for each time step.

        """
        # np.nanmin ignores NaN values and returns min of remaining
        # For all-NaN slices, it returns NaN with a RuntimeWarning
        with np.errstate(all="ignore"):
            return np.nanmin(self.array, axis=1)


@dataclass
class Min(StatsMethod):
    """Finds the minimum value."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the minimum.

        Finds the minimum value in the array for each time step. This method
        does not explicitly handle NaNs. Note: This calculation is not weighted.

        Returns:
            A 1D NumPy array of the minimum value for each time step.

        """
        try:
            tmp = np.min(self.array, axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return np.nan_to_num(tmp, nan=self.def_val)


@dataclass
class MAMax(StatsMethod):
    """Finds the maximum value, ignoring NaN values."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the masked maximum.

        Finds the maximum value in the array for each time step, ignoring NaNs.
        Uses np.nanmax for better performance than masked arrays.
        Note: This calculation is not weighted.

        Returns:
            A 1D NumPy array of the maximum value for each time step.

        """
        # np.nanmax ignores NaN values and returns max of remaining
        # For all-NaN slices, it returns NaN with a RuntimeWarning
        with np.errstate(all="ignore"):
            result = np.nanmax(self.array, axis=1)
        return np.nan_to_num(result, nan=self.def_val)


@dataclass
class Max(StatsMethod):
    """Finds the maximum value."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the maximum.

        Finds the maximum value in the array for each time step. This method
        does not explicitly handle NaNs. Note: This calculation is not weighted.

        Returns:
            A 1D NumPy array of the maximum value for each time step.

        """
        try:
            tmp = np.max(self.array, axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return np.nan_to_num(tmp, nan=self.def_val)
