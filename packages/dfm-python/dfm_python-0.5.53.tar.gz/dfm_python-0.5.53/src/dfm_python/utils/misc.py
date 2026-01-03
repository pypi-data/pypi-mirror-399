"""Miscellaneous utilities for DFM operations.

This module combines:
- Helper functions (parameter resolution, config access)
- Validation utilities
- Exception classes
- Parameter resolution utilities
"""

from typing import Optional, Any, List, Union, Tuple, Dict, TYPE_CHECKING, NoReturn

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import torch
    from ..config.schema import DFMConfig, DFMResult, FitParams
    from ..datamodule import DFMDataModule
else:
    torch = None

try:
    import torch
    _has_torch = True
except ImportError:
    _has_torch = False
    if not TYPE_CHECKING:
        torch = None

from ..logger import get_logger

_logger = get_logger(__name__)


def resolve_param(
    override: Optional[Any] = None,
    config_value: Optional[Any] = None,
    default: Any = None,
    *,
    name: Optional[str] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    config: Optional[Any] = None,
    defaults: Optional[Dict[str, Any]] = None
) -> Any:
    """Resolve parameter value from multiple sources with priority.
    
    Supports two calling patterns:
    1. Legacy: resolve_param(override, config_value, default)
    2. New: resolve_param(name=name, kwargs=kwargs, config=config, defaults=defaults)
    
    Priority (new pattern): kwargs[name] > config.name > defaults[name] > None
    Priority (legacy pattern): override > config_value > default
    
    Parameters
    ----------
    override : Any, optional
        Parameter override value (highest priority in legacy mode)
    config_value : Any, optional
        Configuration value (medium priority in legacy mode)
    default : Any, optional
        Default value (lowest priority in legacy mode)
    name : str, optional
        Parameter name (for new pattern)
    kwargs : Dict[str, Any], optional
        Keyword arguments dict (for new pattern)
    config : Any, optional
        Configuration object with attributes (for new pattern)
    defaults : Dict[str, Any], optional
        Default values dictionary (for new pattern)
        
    Returns
    -------
    Any
        Resolved parameter value
    """
    # New pattern: extract by name from multiple sources
    if name is not None:
        if kwargs is not None and name in kwargs:
            return kwargs.pop(name) if isinstance(kwargs, dict) else kwargs.get(name)
        if config is not None and hasattr(config, name):
            return getattr(config, name)
        if defaults is not None and name in defaults:
            return defaults[name]
        return None
    
    # Legacy pattern: override > config_value > default
    if override is not None:
        return override
    if config_value is not None:
        return config_value
    return default


def extract_param(
    name: str,
    kwargs: Optional[Dict[str, Any]] = None,
    config: Optional[Any] = None,
    defaults: Optional[Dict[str, Any]] = None,
    default: Any = None
) -> Any:
    """Extract parameter with fallback chain: kwargs > config > defaults > default.
    
    Parameters
    ----------
    name : str
        Parameter name
    kwargs : Dict[str, Any], optional
        Keyword arguments dict
    config : Any, optional
        Configuration object with attributes
    defaults : Dict[str, Any], optional
        Default values dictionary
    default : Any, optional
        Final fallback value
        
    Returns
    -------
    Any
        Extracted parameter value
    """
    value = resolve_param(name=name, kwargs=kwargs, config=config, defaults=defaults)
    return value if value is not None else default


def extract_bool_param(
    name: str,
    kwargs: Optional[Dict[str, Any]] = None,
    config: Optional[Any] = None,
    defaults: Optional[Dict[str, Any]] = None,
    default: bool = False
) -> bool:
    """Extract boolean parameter with fallback chain.
    
    Parameters
    ----------
    name : str
        Parameter name
    kwargs : Dict[str, Any], optional
        Keyword arguments dict
    config : Any, optional
        Configuration object with attributes
    defaults : Dict[str, Any], optional
        Default values dictionary
    default : bool, default False
        Final fallback value
        
    Returns
    -------
    bool
        Extracted boolean parameter value
    """
    value = resolve_param(name=name, kwargs=kwargs, config=config, defaults=defaults)
    return value if value is not None else default


def extract_opt_param(
    name: str,
    kwargs: Optional[Dict[str, Any]] = None,
    config: Optional[Any] = None,
    defaults: Optional[Dict[str, Any]] = None
) -> Optional[Any]:
    """Extract optional parameter with fallback chain.
    
    Parameters
    ----------
    name : str
        Parameter name
    kwargs : Dict[str, Any], optional
        Keyword arguments dict
    config : Any, optional
        Configuration object with attributes
    defaults : Dict[str, Any], optional
        Default values dictionary
        
    Returns
    -------
    Optional[Any]
        Extracted parameter value, or None if not found
    """
    return resolve_param(name=name, kwargs=kwargs, config=config, defaults=defaults)


def get_clock_frequency(config: Optional["DFMConfig"], default: Optional[str] = None) -> str:
    """Get clock frequency from config.
    
    Parameters
    ----------
    config : DFMConfig, optional
        Configuration object
    default : str, optional
        Default clock frequency if config is None
        
    Returns
    -------
    str
        Clock frequency string
    """
    from ..config.constants import DEFAULT_CLOCK_FREQUENCY
    return getattr(config, 'clock', default or DEFAULT_CLOCK_FREQUENCY) if config else (default or DEFAULT_CLOCK_FREQUENCY)


# Removed redundant wrapper functions:
# - get_series_ids() -> use config.get_series_ids() directly
# - get_frequencies() -> use config.get_frequencies() directly  
# - get_series_id() -> use config.get_series_id() directly
# These were just thin wrappers that added no value


def check_finite_array(
    arr: np.ndarray,
    name: str = "array",
    context: Optional[str] = None,
    fallback: Optional[np.ndarray] = None
) -> np.ndarray:
    """Check if numpy array contains only finite values, with fallback.
    
    Parameters
    ----------
    arr : np.ndarray
        Array to check
    name : str, default "array"
        Name for error messages
    context : str, optional
        Additional context for error messages
    fallback : np.ndarray, optional
        Fallback array to use if check fails
        
    Returns
    -------
    np.ndarray
        Original array if finite, fallback if provided and check fails
        
    Raises
    ------
    ValueError
        If array contains non-finite values and no fallback provided
    """
    if not np.all(np.isfinite(arr)):
        nan_count = np.sum(~np.isfinite(arr))
        context_str = f" in {context}" if context else ""
        msg = f"{name}{context_str} contains {nan_count} non-finite values"
        
        if fallback is not None:
            _logger.warning(f"{msg}. Using fallback array")
            return fallback
        else:
            _logger.error(msg)
            raise ValueError(msg)
    
    return arr




# ============================================================================
# Exception classes (merged from exceptions.py)
# ============================================================================
"""Exception classes for DFM package.

This module provides specific exception types for better error handling
and clearer error messages throughout the package.
"""


# DFMError moved to utils.errors - import from there instead
# Removed exception aliases - use DFMError directly or proper exceptions from utils.errors
# Use:
# - DFMError (base exception) from utils.errors
# - ConfigurationError, DataError, NumericalError, etc. from utils.errors
from .errors import DFMError


# ParameterResolver removed - overengineered and unused
# Use resolve_param() function directly instead






# Preprocessing functions moved to dataset.process
# Re-export for backward compatibility (only commonly used functions)
from ..dataset.process import (
    _check_sklearn,
    _get_scaler,
    _get_scaler_attr,
    _normalize_wx,
    TimeIndex,
)
# Note: _get_mean and _get_scale are internal utilities, not re-exported
from ..config.constants import DEFAULT_DAMPING_FACTOR



# Time utilities moved to dataset.process
# Re-export parse_timestamp for backward compatibility
from ..dataset.process import parse_timestamp

# Metric functions moved to metric.py
# Re-export for backward compatibility
from .metric import (
    calculate_rmse,
    calculate_mae,
    calculate_mape,
    calculate_r2,
)
