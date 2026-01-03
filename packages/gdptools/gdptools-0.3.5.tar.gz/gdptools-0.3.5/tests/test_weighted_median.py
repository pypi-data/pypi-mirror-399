"""Test of weighted median calculations."""

import numpy as np
from gdptools.agg import stats_methods


def test_weighted_median() -> None:
    """Test weighted median calculation.

    The weighted median is computed by:
    1. Sorting values (and weights) by value, then by weight for ties
    2. Computing cumulative weights
    3. Finding the value at the 0.5 quantile via interpolation

    For row 0: [1, 1, 4, 5, 8] with weights [0.4, 0.1, 0.2, 0.2, 0.1]
    - Sorted by (value, weight): [1(0.1), 1(0.4), 4(0.2), 5(0.2), 8(0.1)]
    - Cumsum: [0.1, 0.5, 0.7, 0.9, 1.0]
    - CDF positions: [0.05, 0.3, 0.6, 0.8, 0.95]
    - Median at 0.5 interpolates between 1 (at 0.3) and 4 (at 0.6) = 3.0

    For row 1: [1, 1, NaN, 5, 8] with weights [0.4, 0.1, 0.2, 0.2, 0.1]
    - Valid values: [1, 1, 5, 8] with weights [0.4, 0.1, 0.2, 0.1] (NaN excluded)
    - Sorted: [1(0.1), 1(0.4), 5(0.2), 8(0.1)]
    - Total weight: 0.8, Cumsum: [0.1, 0.5, 0.7, 0.8]
    - CDF positions: [0.0625, 0.375, 0.75, 0.9375]
    - Median at 0.5 interpolates between 1 (at 0.375) and 5 (at 0.75) ≈ 2.333
    """
    ndata = np.array([[1, 1, 4, 5, 8], [1, 1, np.nan, 5, 8]])
    wghts = np.array([0.4, 0.1, 0.2, 0.2, 0.1])

    # Test masked weighted median function
    # Row 0: median = 3.0
    # Row 1: NaN at index 2 is excluded, median of [1,1,5,8] ≈ 2.333
    masked_median = stats_methods.MAWeightedMedian(ndata, wghts, np.nan)

    np.testing.assert_allclose(
        masked_median.get_stat(),
        np.array([3.0, 2.333333333]),
        rtol=1e-4,
        verbose=True,
    )

    # Test unmasked weighted median function
    # Row 0: median = 3.0
    # Row 1: has NaN, returns default value (np.nan)
    median = stats_methods.WeightedMedian(ndata, wghts, np.nan)

    np.testing.assert_allclose(median.get_stat(), np.array([3.0, np.nan]), rtol=1e-4, verbose=True)
