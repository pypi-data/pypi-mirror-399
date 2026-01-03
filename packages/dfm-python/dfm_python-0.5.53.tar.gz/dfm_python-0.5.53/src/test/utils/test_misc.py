"""Tests for utils.misc module."""

import pytest
from dfm_python.utils.misc import resolve_param


class TestResolveParam:
    """Test suite for resolve_param."""
    
    def test_resolve_param_with_value(self):
        """Test resolve_param with provided value."""
        value = resolve_param(5, None, 10)
        assert value == 5
    
    def test_resolve_param_with_config(self):
        """Test resolve_param with config value."""
        class Config:
            def __init__(self):
                self.num_factors = 3
        
        config = Config()
        value = resolve_param(None, config.num_factors, 10)
        assert value == 3
    
    def test_resolve_param_with_default(self):
        """Test resolve_param with default value."""
        value = resolve_param(None, None, 10)
        assert value == 10

