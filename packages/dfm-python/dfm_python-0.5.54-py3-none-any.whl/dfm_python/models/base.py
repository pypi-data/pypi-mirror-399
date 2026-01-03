"""Base interface for factor models.

This module defines the common interface that all factor models (DFM, DDFM, etc.)
must implement, ensuring consistent API across different model types.

API Differences Between Models
------------------------------
The models in this package (KDFM, DFM, DDFM) have intentionally different APIs
to reflect their different architectures and use cases. They are NOT polymorphic
and cannot be used interchangeably.

**KDFM (Kernelized Dynamic Factor Model)**:
- Training: Uses `training_step()` method (PyTorch Lightning training loop)
- Prediction: `predict(horizon, last_observation)` - REQUIRES `last_observation` parameter
- Result extraction: `get_result()` returns KDFMResult with IRF data
- Architecture: Companion matrix parameterization, structural identification layer
- Use case: Direct IRF estimation, explicit structural shock analysis

**DFM (Dynamic Factor Model)**:
- Training: Uses `fit(data)` method (statsmodels-style)
- Prediction: `predict(horizon)` - NO `last_observation` parameter
- Result extraction: `get_result()` returns DFMResult with factor loadings
- Architecture: Traditional factor model with EM algorithm
- Use case: Dimensionality reduction, factor extraction

**DDFM (Deep Dynamic Factor Model)**:
- Training: Uses `fit_mcmc(data)` method (MCMC sampling)
- Prediction: `predict(horizon)` - NO `last_observation` parameter
- Result extraction: `get_result()` returns DDFMResult with uncertainty quantification
- Architecture: Deep learning + Bayesian inference
- Use case: Probabilistic forecasting with uncertainty quantification

**Why Different APIs?**
These models serve different purposes and have fundamentally different architectures.
KDFM's requirement for `last_observation` reflects its need to compute initial factor
state from the last observed data point, while DFM/DDFM use their internal state.
This design choice enables KDFM's direct IRF estimation capability but requires
explicit state management.

**Usage Examples**:
    # KDFM
    model = KDFM(config=config)
    model.initialize_from_data(data)
    # Training via PyTorch Lightning Trainer
    trainer.fit(model, datamodule)
    forecasts = model.predict(horizon=8, last_observation=last_obs)
    
    # DFM
    model = DFM(config=config)
    model.fit(data)
    forecasts = model.predict(horizon=8)
    
    # DDFM
    model = DDFM(config=config)
    model.fit_mcmc(data)
    forecasts = model.predict(horizon=8)
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple, Any, Dict, List, TYPE_CHECKING
from pathlib import Path
import numpy as np

if TYPE_CHECKING:
    from ..datamodule import KDFMDataModule, DFMDataModule, DDFMDataModule

from ..config import (
    DFMConfig, make_config_source, ConfigSource,
    BaseResult
)
from ..config.constants import DEFAULT_BLOCK_NAME, DEFAULT_DTYPE, DEFAULT_FORECAST_HORIZON, MAX_WARNING_ITEMS, MAX_ERROR_ITEMS, DEFAULT_CLOCK_FREQUENCY
from ..logger import get_logger
from ..utils.errors import ConfigurationError, ModelNotTrainedError, ModelNotInitializedError
from ..utils.validation import check_has_attr

_logger = get_logger(__name__)


class BaseFactorModel(ABC):
    """Abstract base class for all factor models.
    
    This base class provides the common interface that all factor models
    (DFM, DDFM, etc.) must implement. It is a pure abstract class without
    any framework dependencies.
    
    Attributes
    ----------
    _config : Optional[DFMConfig]
        Current configuration object
    _result : Optional[BaseResult]
        Last fit result
    training_state : Optional[Any]
        Training state (model-specific, e.g., DFMTrainingState or DDFMTrainingState)
    """
    
    def __init__(self):
        """Initialize factor model instance."""
        self._config: Optional[DFMConfig] = None
        self._result: Optional[BaseResult] = None
        self.training_state: Optional[Any] = None
        self._data_module: Optional[Any] = None
    
    @property
    def config(self) -> DFMConfig:
        """Get model configuration.
        
        Returns
        -------
        DFMConfig
            Current model configuration object
            
        Raises
        ------
        ConfigurationError
            If model configuration has not been set
        """
        model_type = self.__class__.__name__
        check_has_attr(self, '_config', model_type, error_class=ConfigurationError)
        if self._config is None:
            raise ConfigurationError(
                f"{model_type} config access failed: model configuration has not been set",
                details="Please call load_config() or pass config to __init__() first"
            )
        return self._config
    
    def _check_trained(self) -> None:
        """Check if model is trained, raise error if not.
        
        Raises
        ------
        ValueError
            If model has not been trained yet
        """
        if self._result is None:
            # Try to extract result from training state if available
            training_state = getattr(self, 'training_state', None)
            if training_state is not None:
                try:
                    self._result = self.get_result()
                    return
                except (NotImplementedError, AttributeError):
                    # get_result() not implemented or failed, model not fully trained
                    pass
            
            raise ModelNotTrainedError(
                f"{self.__class__.__name__} operation failed: model has not been trained yet",
                details="Please call fit() or train the model before accessing results"
            )
    
    def _create_temp_config(self, block_name: Optional[str] = None) -> DFMConfig:
        """Create a temporary configuration for model initialization.
        
        Parameters
        ----------
        block_name : str, optional
            Name for the default block. If None, uses DEFAULT_BLOCK_NAME.
            
        Returns
        -------
        DFMConfig
            Minimal default configuration with a single temporary series and block
        """
        if block_name is None:
            block_name = DEFAULT_BLOCK_NAME
        
        return DFMConfig(
            frequency={'temp': DEFAULT_CLOCK_FREQUENCY},
            blocks={block_name: {'factors': 1, 'ar_lag': 1, 'clock': 'm'}}
        )
    
    def _initialize_config(self, config: Optional[DFMConfig] = None) -> DFMConfig:
        """Initialize configuration with common pattern.
        
        Parameters
        ----------
        config : DFMConfig, optional
            Configuration to use. If None, creates temporary config.
            
        Returns
        -------
        DFMConfig
            Initialized configuration
        """
        if config is None:
            config = self._create_temp_config()
        
        self._config = config
        return config
    
    def _load_config_common(
        self,
        source: Optional[Union[str, Path, Dict[str, Any], DFMConfig, ConfigSource]] = None,
        *,
        yaml: Optional[Union[str, Path]] = None,
        mapping: Optional[Dict[str, Any]] = None,
        hydra: Optional[Union[Dict[str, Any], Any]] = None,
    ) -> DFMConfig:
        """Common config loading logic shared by all models."""
        config_source = make_config_source(
            source=source,
            yaml=yaml,
            mapping=mapping,
            hydra=hydra,
        )
        
        new_config = config_source.load()
        self._config = new_config
        return new_config
    
    def _get_datamodule(self) -> Union['KDFMDataModule', 'DFMDataModule', 'DDFMDataModule']:
        """Get DataModule from model or trainer.
        
        This method attempts to retrieve the DataModule from:
        1. Model's _data_module attribute (if set directly)
        2. Trainer's datamodule attribute (if model has trainer and trainer.fit() was called)
        
        This is a common helper used by predict() methods to access data preprocessing
        parameters (Mx, Wx) and target series configuration.
        
        **Type Note**: Uses TYPE_CHECKING to avoid circular imports. The return type
        is `Union[KDFMDataModule, DFMDataModule, DDFMDataModule]` depending on model type.
        TYPE_CHECKING allows proper type hints without runtime circular dependencies.
        
        Returns
        -------
        Any
            DataModule instance (KDFMDataModule, DFMDataModule, or DDFMDataModule)
            - KDFMDataModule: For KDFM models
            - DFMDataModule: For DFM models
            - DDFMDataModule: For DDFM models
            
        Raises
        ------
        ModelNotInitializedError
            If DataModule is not available from any source. This typically means:
            - Trainer.fit() has not been called yet
            - DataModule was not attached to trainer
            - DataModule was not set directly on model
            - Model was not properly initialized before use
            
        Examples
        --------
        >>> # After trainer.fit(), DataModule is available from trainer
        >>> data_module = model._get_datamodule()
        >>> target_series = data_module.target_series
        >>> target_scaler = data_module.target_scaler
        """
        data_module = getattr(self, '_data_module', None)
        
        if data_module is None:
            trainer = getattr(self, 'trainer', None)
            if trainer is not None:
                data_module = getattr(trainer, 'datamodule', None)
        
        if data_module is None:
            raise ModelNotInitializedError(
                f"{self.__class__.__name__}: DataModule not available",
                details=(
                    "DataModule is required for data access and preprocessing. "
                    "Please ensure: (1) DataModule is attached to trainer, "
                    "(2) Trainer.fit() has been called, or (3) DataModule is set directly on model."
                )
            )
        return data_module
    
    @staticmethod
    def _validate_ndarray(arr: Any, name: str, expected_ndim: int) -> None:
        """Validate a numpy array has expected number of dimensions.
        
        Parameters
        ----------
        arr : Any
            Array to validate
        name : str
            Name of the array for error messages
        expected_ndim : int
            Expected number of dimensions
            
        Raises
        ------
        DataValidationError
            If array is not a numpy array or has wrong number of dimensions
        """
        from ..utils.errors import DataValidationError
        if not isinstance(arr, np.ndarray) or arr.ndim != expected_ndim:
            raise DataValidationError(
                f"{name} must be {expected_ndim}D numpy array, got shape {arr.shape if isinstance(arr, np.ndarray) else 'not array'}"
            )
    
    def _forecast_var_factors(
        self,
        Z_last: np.ndarray,
        A: np.ndarray,
        p: int = 1,
        horizon: int = 1,
        Z_prev: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Forecast factors using AR(1) dynamics.
        
        Uses iterative matrix multiplication for efficient computation.
        
        **AR(1) Dynamics**: f_t = A @ f_{t-1}
        
        This method is used by both KDFM and DDFM for factor forecasting, ensuring
        consistent AR dynamics computation across models.
        
        Parameters
        ----------
        Z_last : np.ndarray
            Last factor state of shape (m,) where m is number of factors.
            Must be 1D array with m >= 1.
        A : np.ndarray
            Transition matrix of shape (m, m) for AR(1).
            Must be 2D array with compatible dimensions.
        p : int, default 1
            AR order (always 1).
        horizon : int, default 1
            Number of periods to forecast. Must be >= 1.
        Z_prev : np.ndarray, optional
            Ignored (unused parameter).
            
        Returns
        -------
        np.ndarray
            Forecasted factors of shape (horizon, m) where:
            - horizon: Number of forecast periods
            - m: Number of factors (matches Z_last.shape[0])
            
        Raises
        ------
        DataValidationError
            If input shapes are incompatible or invalid
        NumericalError
            If matrix operations produce NaN/Inf values
            If forecast computation produces NaN/Inf values
            
        Examples
        --------
        >>> # AR(1) forecast
        >>> from dfm_python.numeric.stability import create_scaled_identity
        >>> Z_last = np.array([1.0, 2.0, 3.0])  # 3 factors
        >>> A = create_scaled_identity(3, 0.9)  # Use helper function for scaled identity
        >>> Z_forecast = model._forecast_var_factors(Z_last, A, p=1, horizon=5)
        >>> assert Z_forecast.shape == (5, 3)
        """
        from ..utils.errors import DataValidationError, NumericalError
        from ..numeric.validator import validate_no_nan_inf
        
        # Validate inputs
        self._validate_ndarray(Z_last, "Z_last", 1)
        self._validate_ndarray(A, "A", 2)
        
        m = Z_last.shape[0]
        if m < 1:
            raise DataValidationError(f"Z_last must have at least 1 factor, got m={m}")
        
        if horizon < 1:
            raise DataValidationError(f"horizon must be >= 1, got {horizon}")
        
        validate_no_nan_inf(Z_last, name="Z_last")
        validate_no_nan_inf(A, name="transition matrix A")
        
        # Helper function to validate array shape consistently
        def _validate_shape(
            array: np.ndarray,
            expected_shape: Tuple[int, ...],
            name: str
        ) -> None:
            """Validate array has expected shape.
            
            Args:
                array: Array to validate
                expected_shape: Expected shape tuple
                name: Name of array for error message
            """
            if array.shape != expected_shape:
                raise DataValidationError(
                    f"{name} must have shape {expected_shape}, got {array.shape}"
                )
        
        if Z_prev is not None:
            validate_no_nan_inf(Z_prev, name="Z_prev")
            _validate_shape(Z_prev, (m,), "Z_prev")
        
        # Helper function to handle forecast computation errors consistently
        def _handle_forecast_error(
            error: Exception,
            error_message: str,
            error_details: str,
            exceptions_to_re_raise: Tuple[Any, ...]
        ) -> None:
            """Handle forecast computation errors consistently.
            
            Args:
                error: The exception that occurred
                error_message: Main error message
                error_details: Detailed diagnostic information
                exceptions_to_re_raise: Tuple of exception types to re-raise without wrapping
            """
            if isinstance(error, exceptions_to_re_raise):
                raise
            raise NumericalError(
                error_message,
                details=error_details
            ) from error
        
        try:
            # AR(1) dynamics only (simplified)
            # Validate AR(1) shape
            _validate_shape(A, (m, m), "A (transition matrix)")
            
            # AR(1): f_t = A @ f_{t-1}
            Z_forecast = np.zeros((horizon, m), dtype=DEFAULT_DTYPE)
            Z_forecast[0, :] = A @ Z_last
            for h in range(1, horizon):
                Z_forecast[h, :] = A @ Z_forecast[h - 1, :]
            
            # Validate output
            validate_no_nan_inf(Z_forecast, name="forecasted factors")
            _validate_shape(Z_forecast, (horizon, m), "Forecast output")
            
            return Z_forecast
            
        except (RuntimeError, ValueError, TypeError, AttributeError, KeyError, IndexError) as e:
            # Specific exceptions for forecast computation failures
            _handle_forecast_error(
                error=e,
                error_message=f"Forecast computation failed: {e}",
                error_details=(
                    f"Z_last shape: {Z_last.shape}, A shape: {A.shape}, "
                    f"p={p}, horizon={horizon}. Check: (1) Matrix dimensions, "
                    f"(2) Numerical stability, (3) Input validity."
                ),
                exceptions_to_re_raise=(ConfigurationError, DataValidationError)
            )
    
    # Legacy method removed: _transform_factors_to_observations()
    # This method used Mx/Wx arrays which are no longer used.
    # Models now use target_scaler.inverse_transform() directly in their predict() methods.
    
    def _resolve_target_series(
        self,
        series_ids: Optional[List[str]] = None,
        result: Optional[BaseResult] = None
    ) -> Tuple[Optional[List[str]], Optional[List[int]]]:
        """Resolve target series from DataModule.
        
        This helper method resolves target series from the DataModule's target_series attribute.
        Target series should be set during DataModule initialization.
        
        Parameters
        ----------
        series_ids : List[str], optional
            Available series IDs from config or result. Used for validation.
        result : BaseResult, optional
            Result object that may contain series_ids. Used as fallback.
            
        Returns
        -------
        Tuple[Optional[List[str]], Optional[List[int]]]
            Tuple of (target_series_ids, target_indices) where:
            - target_series_ids: List of target series IDs (None if not resolved)
            - target_indices: List of indices into series_ids (None if not resolved)
            
        Raises
        ------
        DataError
            If target series are not found in available series
        """
        from ..utils.errors import DataError
        
        # Get target series from DataModule
        target_series = None
        try:
            data_module = self._get_datamodule()
            target_series = getattr(data_module, 'target_series', None)
            if target_series is not None and len(target_series) > 0:
                target_series = target_series if isinstance(target_series, list) else [target_series]
        except (ModelNotInitializedError, AttributeError):
            target_series = None
        
        # Get series_ids for validation
        if series_ids is None:
            if result is not None:
                series_ids = getattr(result, 'series_ids', None)
            if series_ids is None and self._config is not None:
                series_ids = self._config.get_series_ids()
        
        # Resolve indices if we have both target_series and series_ids
        target_indices = None
        if target_series is not None and series_ids is not None:
            target_indices = []
            for tgt_id in target_series:
                if tgt_id in series_ids:
                    target_indices.append(series_ids.index(tgt_id))
                else:
                    _logger.warning(
                        f"{self.__class__.__name__} prediction: target series '{tgt_id}' not found in series_ids. "
                        f"Available: {series_ids[:MAX_WARNING_ITEMS]}{'...' if len(series_ids) > MAX_WARNING_ITEMS else ''}. "
                        f"Skipping this target series."
                    )
            
            if len(target_indices) == 0:
                raise DataError(
                    f"{self.__class__.__name__} prediction failed: none of the specified target series found",
                    details=f"Target: {target_series}, Available: {series_ids[:MAX_ERROR_ITEMS]}{'...' if len(series_ids) > MAX_ERROR_ITEMS else ''}"
                )
        
        return target_series, target_indices
    
    def _compute_default_horizon(self, default: Optional[int] = None) -> int:
        """Compute default forecast horizon from clock frequency.
        
        Parameters
        ----------
        default : int, optional
            Default value to use if clock frequency cannot be determined.
            If None, uses DEFAULT_FORECAST_HORIZON constant.
            
        Returns
        -------
        int
            Default horizon in periods (typically 1 year worth of periods)
        """
        if default is None:
            default = DEFAULT_FORECAST_HORIZON
        
        try:
            from ..config import get_periods_per_year
            from ..utils.misc import get_clock_frequency
            
            if self._config is not None:
                clock = get_clock_frequency(self._config)
                return get_periods_per_year(clock)
        except (AttributeError, ImportError, ValueError):
            _logger.debug(f"Could not determine horizon from clock frequency, using default={default}")
        
        return default
    
    
    @staticmethod
    def _create_default_standardization_arrays(
        n_series: int,
        dtype: Optional[type] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create default standardization arrays (for internal use only).
        
        Creates arrays representing standardized data (mean=0, std=1).
        Used internally when data is already standardized and no scaler is provided.
        
        Parameters
        ----------
        n_series : int
            Number of series
        dtype : type, optional
            Data type for arrays. If None, uses DEFAULT_DTYPE.
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            (mean_array, std_array) both of shape (n_series,)
            mean_array: zeros (standardized data has zero mean)
            std_array: ones (standardized data has unit variance)
        """
        if dtype is None:
            dtype = DEFAULT_DTYPE
        
        mean_array = np.zeros(n_series, dtype=dtype)
        std_array = np.ones(n_series, dtype=dtype)
        
        return mean_array, std_array
    
    # Legacy method removed: _standardize_data()
    # This method used Mx/Wx arrays which are no longer used.
    # Data standardization should be done using sklearn scalers before passing to models.
    
    def reset(self) -> 'BaseFactorModel':
        """Reset model state."""
        self._config = None
        self._result = None
        self.training_state = None
        self._data_module = None
        return self
    
    @abstractmethod
    def get_result(self) -> BaseResult:
        """Extract result from trained model.
        
        Returns
        -------
        BaseResult
            Model-specific result object
        """
        raise NotImplementedError("Subclasses must implement get_result()")
