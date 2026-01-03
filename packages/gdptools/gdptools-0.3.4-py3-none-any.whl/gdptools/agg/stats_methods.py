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
        values (NaNs) using NumPy's masked array functionality.

        Returns:
            A 1D NumPy array containing the masked weighted mean for each time step.

        """
        masked = np.ma.masked_array(self.array, np.isnan(self.array))
        try:
            tmp = np.ma.average(masked, weights=self.weights, axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)

        return np.nan_to_num(tmp, nan=self.def_val)


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
        handling missing values (NaNs) using NumPy's masked array functionality.

        Returns:
            A 1D NumPy array of the masked weighted standard deviation for each time step.

        """
        try:
            masked = np.ma.masked_array(self.array, np.isnan(self.array))
            avg = np.ma.average(masked, weights=self.weights, axis=1)
            variance = np.ma.average((masked - avg[:, None]) ** 2, weights=self.weights, axis=1)
            tmp = np.sqrt(variance)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return np.nan_to_num(tmp, nan=self.def_val)


@dataclass
class MAWeightedMedian(StatsMethod):
    """Calculates the area-weighted median, ignoring NaN values."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def _get_median(self, array: npt.NDArray, weights: npt.NDArray[np.double], def_val: np.double) -> np.double:
        """Calculate the masked weighted median for a single time step.

        Calculates the weighted median of the input array for a single time
        step, handling missing values (NaNs).

        Args:
            array: Input array for a single time step.
            weights: Weights for the input array.
            def_val: Default fill value.

        Returns:
            The masked weighted median for the time step.

        """
        try:
            masked = np.ma.masked_array(array, np.isnan(array))
            # zip and sort array values and their corresponding weights
            pairs = sorted(list(zip(masked, weights)))  # noqa
            # mask nodata values from zipped values and weights
            masked_pairs = [tuple for tuple in pairs if not np.isnan(tuple[0])]
            # unzip tuples into a list of masked array values and their weights
            masked_vals, masked_wghts = map(list, zip(*masked_pairs))  # noqa
            i = np.array(masked_vals).argsort()
            sorted_weights = np.array(masked_wghts)[i]
            sorted_values = np.array(masked_vals)[i]
            s = sorted_weights.cumsum()
            p = (s - sorted_weights / 2) / s[-1]
            tmp = np.interp(0.5, p, sorted_values)
        except KeyError:
            tmp = def_val
        return tmp

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the masked weighted median.

        Applies the `_get_median` helper function to each time step in the
        input array.

        Returns:
            A 1D NumPy array of masked weighted medians, one for each time step.

        """
        return np.apply_along_axis(self._get_median, 1, self.array, self.weights, self.def_val)


@dataclass
class WeightedMedian(StatsMethod):
    """Calculates the area-weighted median."""

    array: npt.NDArray
    weights: npt.NDArray[np.double]
    def_val: Any

    def _get_median(
            self, array: npt.NDArray, weights: npt.NDArray[np.double], def_val: np.double
    ) -> npt.NDArray[np.double]:
        """Calculate the weighted median for a single time step.

        Calculates the weighted median of the input array for a single time
        step. This method does not explicitly handle NaNs.

        Args:
            array: Input array for a single time step.
            weights: Weights for the input array.
            def_val: Default fill value.

        Returns:
            The weighted median for the time step.

        """
        # First check to see if there are NoData values. Function will return def_val
        # if there are NoData values, as medians cannot be calculated if NoData values
        # exist.
        if np.isnan(array).any():
            return def_val
        try:
            # zip and sort array values and their corresponding weights
            pairs = sorted(list(zip(array, weights)))  # noqa
            # unzip tuples into a list of array values and their weights
            vals, wghts = map(list, zip(*pairs))  # noqa
            i = np.array(vals).argsort()
            sorted_weights = np.array(wghts)[i]
            sorted_values = np.array(vals)[i]
            s = sorted_weights.cumsum()
            p = (s - sorted_weights / 2) / s[-1]
            tmp = np.interp(0.5, p, sorted_values)

        except KeyError:
            tmp = def_val
        return tmp

    def get_stat(self) -> npt.NDArray[np.double]:
        """Calculate the weighted median.

        Applies the `_get_median` helper function to each time step in the
        input array.

        Returns:
            A 1D NumPy array of weighted medians, one for each time step.

        """
        return np.apply_along_axis(self._get_median, 1, self.array, self.weights, self.def_val)


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
        values (NaNs) using NumPy's masked array functionality.

        Returns:
            A 1D NumPy array of the masked weighted sum for each time step.

        """
        try:
            masked = np.ma.masked_array(self.array, np.isnan(self.array))
            tmp = np.ma.sum(masked * self.weights, axis=1)
        except KeyError:
            numpts = len(self.weights)
            tmp = np.full((numpts), self.def_val)
        return tmp


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
        Note: This calculation is not weighted.

        Returns:
            A 1D NumPy array of the minimum value for each time step.

        """
        try:
            masked = np.ma.masked_array(self.array, np.isnan(self.array))
            tmp = np.ma.min(masked, axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return tmp


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
        Note: This calculation is not weighted.

        Returns:
            A 1D NumPy array of the maximum value for each time step.

        """
        try:
            masked = np.ma.masked_array(self.array, np.isnan(self.array))
            tmp = np.ma.max(masked, axis=1)
        except KeyError:
            numpts = self.weights.shape[0]
            tmp = np.full((numpts), self.def_val)
        return np.nan_to_num(tmp, nan=self.def_val)


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
