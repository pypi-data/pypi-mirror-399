"""Tests for decoder.linear module."""

import pytest
import numpy as np
import torch
from dfm_python.decoder.linear import Decoder


class TestDecoder:
    """Test suite for linear Decoder."""
    
    def test_decoder_initialization(self):
        """Test Decoder can be initialized."""
        input_dim = 3
        output_dim = 10
        decoder = Decoder(input_dim=input_dim, output_dim=output_dim)
        assert decoder is not None
        assert decoder.input_dim == input_dim
        assert decoder.output_dim == output_dim
    
    def test_decoder_forward(self):
        """Test Decoder forward pass."""
        decoder = Decoder(input_dim=3, output_dim=10)
        x = torch.randn(5, 3)
        output = decoder(x)
        assert output.shape == (5, 10)
    
    def test_decoder_to_numpy(self):
        """Test converting decoder to numpy."""
        # TODO: Implement test
        pass

