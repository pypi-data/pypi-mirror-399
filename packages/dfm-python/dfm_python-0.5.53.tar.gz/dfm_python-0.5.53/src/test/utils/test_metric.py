"""Tests for utils.metric module."""

import pytest
import numpy as np
from dfm_python.utils.metric import calculate_rmse


class TestCalculateRMSE:
    """Test suite for calculate_rmse."""
    
    def test_rmse_identical_arrays(self):
        """Test RMSE with identical arrays."""
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([1.0, 2.0, 3.0])
        rmse = calculate_rmse(y_true, y_pred)
        assert rmse == 0.0
    
    def test_rmse_different_arrays(self):
        """Test RMSE with different arrays."""
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([2.0, 3.0, 4.0])
        rmse = calculate_rmse(y_true, y_pred)
        assert rmse == pytest.approx(1.0)
    
    def test_rmse_shape_validation(self):
        """Test RMSE with mismatched shapes."""
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([1.0, 2.0])
        with pytest.raises(ValueError):
            calculate_rmse(y_true, y_pred)

