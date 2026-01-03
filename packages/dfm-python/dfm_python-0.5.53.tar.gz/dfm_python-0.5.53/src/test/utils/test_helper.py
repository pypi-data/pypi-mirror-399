"""Tests for utils.helper module."""

import pytest
import numpy as np
from dfm_python.utils.helper import (
    handle_linear_algebra_error,
    get_config_attr,
    validate_finite_array
)
from dfm_python.utils.errors import NumericalError


class TestHandleLinearAlgebraError:
    """Test suite for handle_linear_algebra_error."""
    
    def test_successful_operation(self):
        """Test successful operation without error."""
        result = handle_linear_algebra_error(
            np.linalg.solve,
            "matrix solve",
            fallback_value=np.eye(2),
            np.eye(2),
            np.array([1.0, 1.0])
        )
        assert result is not None
    
    def test_fallback_value(self):
        """Test fallback value on error."""
        def failing_operation(*args, **kwargs):
            raise np.linalg.LinAlgError("Singular matrix")
        
        fallback = np.eye(2)
        result = handle_linear_algebra_error(
            failing_operation,
            "failing operation",
            fallback_value=fallback
        )
        np.testing.assert_array_equal(result, fallback)
    
    def test_fallback_function(self):
        """Test fallback function on error."""
        def failing_operation(*args, **kwargs):
            raise np.linalg.LinAlgError("Singular matrix")
        
        def fallback_func(*args, **kwargs):
            return np.eye(2)
        
        result = handle_linear_algebra_error(
            failing_operation,
            "failing operation",
            fallback_func=fallback_func
        )
        assert result is not None
        assert result.shape == (2, 2)


class TestGetConfigAttr:
    """Test suite for get_config_attr."""
    
    def test_get_existing_attr(self):
        """Test getting existing attribute."""
        class Config:
            def __init__(self):
                self.num_factors = 3
        
        config = Config()
        value = get_config_attr(config, 'num_factors', default=2)
        assert value == 3
    
    def test_get_missing_attr_with_default(self):
        """Test getting missing attribute with default."""
        class Config:
            pass
        
        config = Config()
        value = get_config_attr(config, 'missing_attr', default=5)
        assert value == 5
    
    def test_get_required_attr_missing(self):
        """Test getting required attribute that is missing."""
        class Config:
            pass
        
        config = Config()
        with pytest.raises(AttributeError):
            get_config_attr(config, 'required_attr', required=True)
    
    def test_none_config_with_default(self):
        """Test getting attribute from None config."""
        value = get_config_attr(None, 'attr', default=10)
        assert value == 10


class TestValidateFiniteArray:
    """Test suite for validate_finite_array."""
    
    def test_valid_finite_array(self):
        """Test validation of finite array."""
        arr = np.array([1.0, 2.0, 3.0])
        validate_finite_array(arr, "test array")
        # Should not raise
    
    def test_array_with_nan(self):
        """Test validation fails on NaN."""
        arr = np.array([1.0, np.nan, 3.0])
        with pytest.raises(NumericalError):
            validate_finite_array(arr, "test array")
    
    def test_array_with_inf(self):
        """Test validation fails on Inf."""
        arr = np.array([1.0, np.inf, 3.0])
        with pytest.raises(NumericalError):
            validate_finite_array(arr, "test array")
    
    def test_array_with_context(self):
        """Test validation with context message."""
        arr = np.array([1.0, np.nan, 3.0])
        with pytest.raises(NumericalError, match=".*DDFM prediction.*"):
            validate_finite_array(arr, "forecast", context="DDFM prediction")

