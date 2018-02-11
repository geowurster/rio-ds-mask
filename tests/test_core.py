"""Tests for non-cli features."""


import pytest
import numpy as np
from rio_ds_mask import _norm_gdal_mask


@pytest.mark.parametrize("mask,expected", [
    # Totally masked
    (np.array([0, 0]), np.array([0, 0])),
    # Partially masked + trigger heuristic
    (np.array([0, 1]), np.array([0, 255])),
    # Partially masked with 255's instead of 1's shouldn't be altered
    (np.array([0, 255]), np.array([0, 255])),
    # Totally transparent
    (np.array([1, 1]), np.array([255, 255])),
    # Varying alpha values shouldn't be altered
    (np.array([0, 1, 2]), np.array([0, 1, 2])),
    # Values past 255 shouldn't be altered
    (np.array([0, 256]), np.array([0, 256])),
])
def test_norm_gdal_mask(mask, expected):

    """Test for ``rio_ds_mask._norm_gdal_mask()``.  Tests both ``np.uint16``
    and ``np.int16``.
    """

    for dtype in (np.uint16, np.int16):
        mask = _norm_gdal_mask(
            np.array(mask, dtype=dtype),
            [np.dtype(dtype).name])
        assert np.array_equal(mask, expected)
        assert mask.dtype == dtype
