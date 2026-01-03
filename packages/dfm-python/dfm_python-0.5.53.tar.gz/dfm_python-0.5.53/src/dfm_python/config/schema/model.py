"""Configuration schema for DFM models.

This module provides model-specific configuration dataclasses:
- BaseModelConfig: Base class with shared model structure (series, clock, data handling)
- DFMConfig(BaseModelConfig): Linear DFM with EM algorithm parameters and block structure
- DDFMConfig(BaseModelConfig): Deep DFM with neural network training parameters (no blocks)
- KDFMConfig(BaseModelConfig): Kernelized DFM with VARMA parameters

The configuration hierarchy:
- BaseModelConfig: Model structure (series, clock, data handling) - NO blocks
- DFMConfig: Adds blocks structure and EM algorithm parameters (max_iter, threshold, regularization)
- DDFMConfig: Adds neural network parameters (epochs, learning_rate, encoder_layers) - NO blocks
- KDFMConfig: Adds VARMA parameters (ar_order, ma_order, structural_method) - NO blocks

Note: Series are specified via frequency dict mapping column names to frequencies. Result classes are in schema/results.py

Blocks are DFM-specific and defined as Dict[str, Dict[str, Any]] where each block is a dict with:
- num_factors: int (number of factors)
- series: List[str] (list of series names/column names in this block)

For loading configurations from files (YAML) or other sources,
see the config.adapter module which provides source adapters.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

if TYPE_CHECKING:
    try:
        from sklearn.preprocessing import StandardScaler, RobustScaler
        ScalerType = Union[StandardScaler, RobustScaler, Any]
    except ImportError:
        ScalerType = Any
else:
    ScalerType = Any

# Import ConfigurationError and DataError lazily to avoid circular imports
# They are only used in methods, not at module level
from ..constants import (
    DEFAULT_LEARNING_RATE,
    DEFAULT_MAX_EPOCHS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_DDFM_BATCH_SIZE,
    DEFAULT_GRAD_CLIP_VAL,
    DEFAULT_REGULARIZATION_SCALE,
    DEFAULT_STRUCTURAL_REG_WEIGHT,
    DEFAULT_CONVERGENCE_THRESHOLD,
    DEFAULT_EM_THRESHOLD,
    DEFAULT_EM_MAX_ITER,
    DEFAULT_MAX_ITER,
    DEFAULT_MAX_MCMC_ITER,
    DEFAULT_TOLERANCE,
    DEFAULT_DATA_CLIP_THRESHOLD,
    DEFAULT_MIN_OBS_IDIO,
    DEFAULT_DISP,
    DEFAULT_IDIO_RHO0,
    AR_CLIP_MIN,
    AR_CLIP_MAX,
    MIN_EIGENVALUE,
    MAX_EIGENVALUE,
    MIN_DIAGONAL_VARIANCE,
    DEFAULT_NAN_METHOD,
    DEFAULT_NAN_K,
    DEFAULT_CLOCK_FREQUENCY,
)



# ============================================================================
# Base Model Configuration
# ============================================================================

@dataclass
class BaseModelConfig:
    """Base configuration class with shared model structure.
    
    This base class contains the model structure that is common to all
    factor models (DFM, DDFM, KDFM):
    - Series definitions (via frequency dict mapping column names to frequencies)
    - Clock frequency (required, base frequency for latent factors)
    - Data preprocessing (missing data handling)
    
    Series Configuration:
    - Provide `frequency` dict: {'column_name': 'frequency_code'} to specify per-series frequencies
    - If `frequency` is None, all columns will use `clock` frequency
    - If a column is missing from `frequency` dict, it will use `clock` frequency
    - When data is loaded, missing columns in `frequency` dict are automatically added with `clock` frequency
    
    Note: Blocks are DFM-specific and are NOT included in BaseModelConfig.
    DFMConfig adds block structure, while DDFMConfig and KDFMConfig do not use blocks.
    
    Subclasses (DFMConfig, DDFMConfig, KDFMConfig) add model-specific training parameters.
    
    Examples
    --------
    >>> # With explicit frequency mapping
    >>> config = DFMConfig(
    ...     frequency={'gdp': 'q', 'unemployment': 'm', 'interest_rate': 'm'},
    ...     clock='m',
    ...     blocks={...}
    ... )
    >>> 
    >>> # Without frequency (all use clock)
    >>> config = DFMConfig(
    ...     frequency=None,  # or omit it
    ...     clock='m',
    ...     blocks={...}
    ... )
    >>> # Series will be built from data columns using clock='m' when data is loaded
    """
    # ========================================================================
    # Model Structure (WHAT - defines the model)
    # ========================================================================
    frequency: Optional[Dict[str, str]] = None  # Optional: Maps column names to frequencies {'column_name': 'frequency'}
    # If None, all series use clock frequency (data is assumed aligned with clock)
    
    # ========================================================================
    # Shared Data Handling Parameters
    # ========================================================================
    clock: str = 'm'  # Required: Base frequency for latent factors (global clock): 'd', 'w', 'm', 'q', 'sa', 'a' (defaults to 'm' for monthly)
    target_scaler: Optional[ScalerType] = None  # Sklearn scaler instance (StandardScaler, RobustScaler, etc.) for target series only. Pass scaler object directly, not string. Feature series are assumed to be manually preprocessed.
    # Note: nan_method and nan_k are internal constants (DEFAULT_NAN_METHOD, DEFAULT_NAN_K) used during initialization only
    
    def __post_init__(self):
        """Validate basic model structure.
        
        This method performs basic validation of the model configuration:
        - Validates clock frequency
        - Validates frequency dict if provided
        
        Raises
        ------
        ValueError
            If any validation check fails, with a descriptive error message
            indicating what needs to be fixed.
        """
        from ...config.adapter import _raise_config_error, _is_dict_like
        
        # Validate global clock (required)
        self.clock = validate_frequency(self.clock)
        
        # Validate frequency dict if provided
        if self.frequency is not None:
            if not _is_dict_like(self.frequency):
                _raise_config_error(
                    f"frequency must be a dict mapping column names to frequencies, got {type(self.frequency)}"
                )
            
            # Empty frequency dict is allowed (will be filled from columns later with clock frequency)
            
            # Validate all frequencies in the dict
            for col_name, freq in self.frequency.items():
                if not isinstance(col_name, str):
                    _raise_config_error(f"frequency dict keys must be strings (column names), got {type(col_name)}")
                validate_frequency(freq)
    
    def get_frequencies(self, columns: Optional[List[str]] = None) -> List[str]:
        """Get frequencies. Auto-creates dict from columns if None, defaults to clock for missing."""
        if columns is not None:
            # Auto-create frequency dict if None
            if self.frequency is None:
                self.frequency = {col: self.clock for col in columns}
            # Return frequencies, defaulting to clock for missing columns
            return [self.frequency.get(col, self.clock) for col in columns]
        
        # No columns provided - return from existing dict
        if self.frequency is None:
            return []
        return list(self.frequency.values())
    
    def get_series_ids(self, columns: Optional[List[str]] = None) -> List[str]:
        """Get series IDs. Auto-creates frequency dict from columns if None."""
        if columns is not None:
            # Auto-create frequency dict if None
            if self.frequency is None:
                self.frequency = {col: self.clock for col in columns}
            return columns
        
        # No columns provided - return from existing dict
        if self.frequency is None:
            return []
        return list(self.frequency.keys())
    
    @classmethod
    def _extract_base(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract shared base parameters from config dict."""
        from ...config.adapter import _convert_series_to_frequency_dict
        
        base_params = {
            'clock': data.get('clock', DEFAULT_CLOCK_FREQUENCY),
            'target_scaler': data.get('target_scaler', None),
        }
        
        # Handle frequency dict (new API) or legacy series list/dict
        from ...config.adapter import _extract_frequency_dict
        frequency_dict = _extract_frequency_dict(data, base_params['clock'])
        if frequency_dict is not None:
            base_params['frequency'] = frequency_dict
        
        return base_params
    
    @classmethod
    def _extract_params(cls, data: Dict[str, Any], param_map: Dict[str, Any]) -> Dict[str, Any]:
        """Generic parameter extraction helper.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Source data dictionary
        param_map : Dict[str, Any]
            Mapping of parameter names to default values
            
        Returns
        -------
        Dict[str, Any]
            Extracted parameters with defaults applied
        """
        return {key: data.get(key, default) for key, default in param_map.items()}


# ============================================================================
# Model-Specific Configuration Classes
# ============================================================================
# BaseModelConfig is imported from base.py - no duplicate definition needed


@dataclass
class DFMConfig(BaseModelConfig):
    """Linear DFM configuration - EM algorithm parameters and block structure.
    
    This configuration class extends BaseModelConfig with parameters specific
    to linear Dynamic Factor Models trained using the Expectation-Maximization
    (EM) algorithm. DFM uses block structure to organize factors (global + sector-specific).
    
    The configuration can be built from:
    - Main settings (estimation parameters) from config/default.yaml
    - Series definitions via frequency dict (column names -> frequencies)
    - Block definitions from config/blocks/default.yaml
    """
    # ========================================================================
    # Block Structure (DFM-specific)
    # ========================================================================
    blocks: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Block configurations: {"block_name": {"num_factors": int, "series": [str]}}
    block_names: List[str] = field(init=False)  # Block names in order (derived from blocks dict)
    factors_per_block: List[int] = field(init=False)  # Number of factors per block (derived from blocks)
    _cached_blocks: Optional[np.ndarray] = field(default=None, init=False, repr=False)  # Internal cache
    
    # ========================================================================
    # EM Algorithm Parameters (HOW - controls the algorithm)
    # ========================================================================
    ar_lag: int = 1  # Number of lags in AR transition equation (lookback window). Must be 1 or 2 (maximum supported order is VAR(2))
    threshold: float = DEFAULT_EM_THRESHOLD  # EM convergence threshold
    max_iter: int = DEFAULT_EM_MAX_ITER  # Maximum EM iterations
    
    # ========================================================================
    # Numerical Stability Parameters (transparent and configurable)
    # ========================================================================
    # AR Coefficient Clipping
    clip_ar_coefficients: bool = True  # Enable AR coefficient clipping for stationarity
    ar_clip_min: float = AR_CLIP_MIN  # Minimum AR coefficient (must be > -1 for stationarity)
    ar_clip_max: float = AR_CLIP_MAX   # Maximum AR coefficient (must be < 1 for stationarity)
    warn_on_ar_clip: bool = True  # Warn when AR coefficients are clipped (indicates near-unit root)
    
    # Data Value Clipping
    clip_data_values: bool = True  # Enable clipping of extreme data values
    data_clip_threshold: float = 100.0  # Clip values beyond this many standard deviations
    warn_on_data_clip: bool = True  # Warn when data values are clipped (indicates outliers)
    
    # Regularization
    use_regularization: bool = True  # Enable regularization for numerical stability
    regularization_scale: float = DEFAULT_REGULARIZATION_SCALE  # Scale factor for ridge regularization (relative to trace, default 1e-5)
    min_eigenvalue: float = 1e-8  # Minimum eigenvalue for positive definite matrices
    max_eigenvalue: float = 1e6   # Maximum eigenvalue cap to prevent explosion
    warn_on_regularization: bool = True  # Warn when regularization is applied
    
    # Damped Updates
    use_damped_updates: bool = True  # Enable damped updates when likelihood decreases
    damping_factor: float = 0.8  # Damping factor (0.8 = 80% new, 20% old)
    warn_on_damped_update: bool = True  # Warn when damped updates are used
    
    # Idiosyncratic Component Augmentation
    augment_idio: bool = True  # Enable state augmentation with idiosyncratic components (default: True)
    augment_idio_slow: bool = True  # Enable tent-length chains for slower-frequency series (default: True)
    idio_rho0: float = DEFAULT_IDIO_RHO0  # Initial AR coefficient for idiosyncratic components (default: 0.1)
    idio_min_var: float = 1e-8  # Minimum variance for idiosyncratic innovation covariance (default: 1e-8)
    
    def __post_init__(self):
        """Validate blocks structure and derive block properties."""
        super().__post_init__()
        
        from ...config.adapter import _raise_config_error
        
        if not self.blocks:
            _raise_config_error("DFM configuration must contain at least one block.")
        
        # Derive block_names and factors_per_block
        block_names_list = list(self.blocks.keys())
        object.__setattr__(self, 'block_names', block_names_list)
        object.__setattr__(self, 'factors_per_block', 
                         [self.blocks[name].get('num_factors', 1) for name in self.block_names])
        
        # Validate blocks
        for block_name, block_cfg in self.blocks.items():
            num_factors = block_cfg.get('num_factors', 1)
            series_list = block_cfg.get('series', [])
            
            from ...config.adapter import _raise_config_error
            if num_factors < 1:
                _raise_config_error(f"Block '{block_name}' must have num_factors >= 1, got {num_factors}")
            
            if not isinstance(series_list, list):
                _raise_config_error(f"Block '{block_name}' must have 'series' as a list, got {type(series_list)}")
            
            # Validate series exist in frequency dict if available
            if self.frequency is not None:
                for series_name in series_list:
                    if series_name not in self.frequency:
                        # Auto-add missing series with clock frequency
                        self.frequency[series_name] = self.clock
        
        from ...config.adapter import _raise_config_error
        if any(f < 1 for f in self.factors_per_block):
            _raise_config_error("factors_per_block must contain positive integers >= 1")
    
    def get_blocks_array(self, columns: Optional[List[str]] = None) -> np.ndarray:
        """Get blocks as numpy array (N x B) where N is number of series and B is number of blocks.
        
        Returns 1 if series is in block, 0 otherwise.
        """
        if self._cached_blocks is None:
            # Auto-create frequency dict if needed
            if self.frequency is None:
                if columns is None:
                    from ...config.adapter import _raise_config_error
                    _raise_config_error("frequency dict or columns required")
                self.frequency = {col: self.clock for col in columns}
            
            series_ids = list(self.frequency.keys()) if columns is None else columns
            
            # Build blocks array from block series lists (N x B matrix)
            block_series_sets = {
                name: set(self.blocks[name].get('series', []))
                for name in self.block_names
            }
            blocks_list = [
                [1 if series_id in block_series_sets[name] else 0 for name in self.block_names]
                for series_id in series_ids
            ]
            
            self._cached_blocks = np.array(blocks_list, dtype=int)
        return self._cached_blocks
    
    @classmethod
    def _extract_dfm_params(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract DFM-specific parameters from config dict."""
        base_params = cls._extract_base(data)
        dfm_params = cls._extract_params(data, {
            'ar_lag': 1,
            'threshold': DEFAULT_EM_THRESHOLD,
            'max_iter': DEFAULT_EM_MAX_ITER,
            'clip_ar_coefficients': True,
            'ar_clip_min': -0.99,
            'ar_clip_max': 0.99,
            'use_regularization': True,
            'regularization_scale': 1e-5,
            'min_eigenvalue': MIN_EIGENVALUE,
            'max_eigenvalue': MAX_EIGENVALUE,
            'augment_idio': True,
            'augment_idio_slow': True,
            'idio_rho0': 0.1,
            'idio_min_var': MIN_DIAGONAL_VARIANCE,
        })
        base_params.update(dfm_params)
        return base_params
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Union['DFMConfig', 'DDFMConfig']:
        """Create DFMConfig or DDFMConfig from dictionary.
        
        Handles multiple formats:
        1. New format: {'frequency': {'column_name': 'frequency'}, ...}
        2. Legacy format (Hydra): {'series': {'series_id': {...}}, 'blocks': {...}}
        3. Legacy format (list): {'series': [{'series_id': ..., 'frequency': ...}], ...}
        
        Also accepts estimation parameters: ar_lag, threshold, max_iter, etc.
        """
        from ...config.adapter import detect_config_type, MODEL_TYPE_DDFM, _normalize_blocks_dict
        from ...utils.errors import ConfigurationError
        
        # Extract base params (handles frequency conversion from series if needed)
        base_params = cls._extract_base(data)
        
        # Determine config type
        config_type = detect_config_type(data)
        
        if config_type == MODEL_TYPE_DDFM:
            return DDFMConfig(**base_params, **DDFMConfig._extract_ddfm(data))
        
        # Handle blocks for DFM
        from ...config.adapter import _raise_config_error, _is_dict_like
        blocks_dict = data.get('blocks', {})
        if not blocks_dict:
            _raise_config_error("blocks dict is required for DFM config")
        if not _is_dict_like(blocks_dict):
            _raise_config_error(f"blocks must be a dict, got {type(blocks_dict)}")
        
        blocks_dict_normalized = _normalize_blocks_dict(blocks_dict)
        return DFMConfig(blocks=blocks_dict_normalized, **base_params, **DFMConfig._extract_dfm_params(data))


@dataclass
class DDFMConfig(BaseModelConfig):
    """Deep Dynamic Factor Model configuration - neural network training parameters.
    
    This configuration class extends BaseModelConfig with parameters specific
    to Deep Dynamic Factor Models trained using neural networks (autoencoders).
    
    Note: DDFM does NOT use block structure. Use num_factors directly to specify
    the number of factors. Blocks are DFM-specific and not needed for DDFM.
    
    The configuration can be built from:
    - Main settings (training parameters) from config/default.yaml
    - Series definitions via frequency dict (column names -> frequencies)
    """
    # ========================================================================
    # Neural Network Training Parameters
    # ========================================================================
    encoder_layers: Optional[List[int]] = None  # Hidden layer dimensions for encoder (default: [64, 32])
    num_factors: Optional[int] = None  # Number of factors (inferred from config if None)
    activation: str = 'relu'  # Activation function ('tanh', 'relu', 'sigmoid', default: 'relu' to match original DDFM)
    use_batch_norm: bool = True  # Use batch normalization in encoder (default: True)
    learning_rate: float = 0.001  # Learning rate for Adam optimizer (default: 0.001)
    epochs: int = 100  # Number of training epochs (default: 100)
    batch_size: int = 100  # Batch size for training (default: 100 to match original DDFM)
    factor_order: int = 1  # VAR lag order for factor dynamics. Must be 1 or 2 (maximum supported order is VAR(2), default: 1)
    use_idiosyncratic: bool = True  # Model idio components with AR(1) dynamics (default: True)
    min_obs_idio: int = 5  # Minimum observations for idio AR(1) estimation (default: 5)
    
    # Additional training parameters
    max_iter: int = DEFAULT_MAX_MCMC_ITER  # Maximum MCMC iterations for iterative factor extraction
    tolerance: float = DEFAULT_TOLERANCE  # Convergence tolerance for MCMC iterations
    disp: int = 10  # Display frequency for training progress
    seed: Optional[int] = None  # Random seed for reproducibility
    
    
    # ========================================================================
    # Factory Methods
    # ========================================================================
    
    @classmethod
    def _extract_ddfm(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract DDFM-specific parameters from config dict."""
        base_params = cls._extract_base(data)
        ddfm_params = cls._extract_params(data, {
            'encoder_layers': None,
            'num_factors': None,
            'activation': 'relu',
            'use_batch_norm': True,
            'learning_rate': DEFAULT_LEARNING_RATE,
            'epochs': DEFAULT_MAX_EPOCHS,
            'batch_size': DEFAULT_DDFM_BATCH_SIZE,
            'factor_order': 1,
            'use_idiosyncratic': True,
            'min_obs_idio': DEFAULT_MIN_OBS_IDIO,
            'max_iter': DEFAULT_MAX_MCMC_ITER,
            'tolerance': DEFAULT_TOLERANCE,
            'disp': DEFAULT_DISP,
            'seed': None,
        })
        base_params.update(ddfm_params)
        return base_params
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DDFMConfig':
        """Create DDFMConfig from dictionary (delegates to DFMConfig.from_dict for type detection)."""
        result = DFMConfig.from_dict(data)
        if isinstance(result, DDFMConfig):
            return result
        raise ValueError("Expected DDFMConfig but got DFMConfig")


@dataclass
class KDFMConfig(BaseModelConfig):
    """KDFM configuration dataclass.
    
    This dataclass contains all configuration parameters for the KDFM model.
    It inherits from BaseModelConfig and adds KDFM-specific parameters.
    """
    # VARMA parameters
    ar_order: int = 1  # VAR order p
    ma_order: int = 0  # MA order q (0 = pure VAR)
    
    # Structural identification
    structural_method: str = 'cholesky'  # 'cholesky', 'full', 'low_rank'
    structural_rank: Optional[int] = None  # For low-rank parameterization
    
    # Training parameters (use constants for defaults)
    learning_rate: float = DEFAULT_LEARNING_RATE
    max_epochs: int = DEFAULT_MAX_EPOCHS
    batch_size: int = DEFAULT_BATCH_SIZE
    weight_decay: float = DEFAULT_REGULARIZATION_SCALE
    grad_clip_val: float = DEFAULT_GRAD_CLIP_VAL
    
    # Regularization
    structural_reg_weight: float = DEFAULT_STRUCTURAL_REG_WEIGHT  # Weight for structural loss
    use_regularization: bool = True
    regularization_scale: float = DEFAULT_REGULARIZATION_SCALE


# ============================================================================
# Validation Functions
# ============================================================================

def validate_frequency(frequency: str) -> str:
    """Validate frequency code.
    
    Parameters
    ----------
    frequency : str
        Frequency code to validate
        
    Returns
    -------
    str
        Validated frequency code
        
    Raises
    ------
    ConfigurationError
        If frequency is not in VALID_FREQUENCIES
    """
    from ..constants import VALID_FREQUENCIES
    from ...utils.errors import ConfigurationError
    
    if not isinstance(frequency, str):
        raise ConfigurationError(
            f"Frequency must be a string, got {type(frequency).__name__}: {frequency}"
        )
    
    if frequency not in VALID_FREQUENCIES:
        raise ConfigurationError(
            f"Invalid frequency: '{frequency}'. Must be one of {VALID_FREQUENCIES}. "
            f"Common frequencies: 'd' (daily), 'w' (weekly), 'm' (monthly), "
            f"'q' (quarterly), 'sa' (semi-annual), 'a' (annual)."
        )
    
    return frequency

