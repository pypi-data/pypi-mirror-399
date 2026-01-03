"""Tests for config.constants module."""

import pytest
from dfm_python.config.constants import (
    DEFAULT_CLOCK_FREQUENCY,
    PERIODS_PER_YEAR,
    DEFAULT_BLOCK_NAME
)


class TestConstants:
    """Test suite for configuration constants."""
    
    def test_default_clock_frequency(self):
        """Test default clock frequency constant."""
        assert DEFAULT_CLOCK_FREQUENCY is not None
        assert isinstance(DEFAULT_CLOCK_FREQUENCY, str)
    
    def test_periods_per_year(self):
        """Test periods per year mapping."""
        assert isinstance(PERIODS_PER_YEAR, dict)
        assert 'M' in PERIODS_PER_YEAR
        assert 'Q' in PERIODS_PER_YEAR
        assert 'A' in PERIODS_PER_YEAR
    
    def test_default_block_name(self):
        """Test default block name constant."""
        assert DEFAULT_BLOCK_NAME is not None
        assert isinstance(DEFAULT_BLOCK_NAME, str)

