"""Tests for utils.errors module."""

import pytest
from dfm_python.utils.errors import (
    NumericalError,
    ModelNotTrainedError,
    ConfigurationError
)


class TestNumericalError:
    """Test suite for NumericalError."""
    
    def test_numerical_error_initialization(self):
        """Test NumericalError can be raised."""
        with pytest.raises(NumericalError):
            raise NumericalError("Test error")


class TestModelNotTrainedError:
    """Test suite for ModelNotTrainedError."""
    
    def test_model_not_trained_error(self):
        """Test ModelNotTrainedError can be raised."""
        with pytest.raises(ModelNotTrainedError):
            raise ModelNotTrainedError("Model not trained")


class TestConfigurationError:
    """Test suite for ConfigurationError."""
    
    def test_configuration_error(self):
        """Test ConfigurationError can be raised."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Configuration error")

