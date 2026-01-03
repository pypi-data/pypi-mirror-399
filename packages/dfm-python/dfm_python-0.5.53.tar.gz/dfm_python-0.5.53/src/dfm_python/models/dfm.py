"""Linear Dynamic Factor Model (DFM) implementation.

This module contains the linear DFM implementation using EM algorithm.
DFM inherits from BaseFactorModel (not PyTorch Lightning) since all
calculations are performed in NumPy using pykalman.
"""

# Standard library imports
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

# Third-party imports
import numpy as np
from scipy.linalg import block_diag

# NumPy-based Kalman filter (pykalman) - now a required dependency
from ..ssm.kalman import DFMKalmanFilter

# Local imports
from ..config import (
    DFMConfig,
    ConfigSource,
    DFMResult,
)
from ..numeric.tent import get_agg_structure, get_tent_weights, get_slower_freq_tent_weights
from ..config.constants import (
    FREQUENCY_HIERARCHY,
    TENT_WEIGHTS_LOOKUP,
    DEFAULT_CONVERGENCE_THRESHOLD,
    DEFAULT_MAX_ITER,
    DEFAULT_NAN_METHOD,
    DEFAULT_NAN_K,
    DEFAULT_DTYPE,
    DEFAULT_CLOCK_FREQUENCY,
    DEFAULT_HIERARCHY_VALUE,
)
from ..logger import get_logger
from .base import BaseFactorModel
from ..utils.errors import (
    ModelNotTrainedError,
    ModelNotInitializedError,
    ConfigurationError,
    DataError,
    PredictionError,
    NumericalError
)

# Import EM config from functional module
from ..functional.em import _DEFAULT_EM_CONFIG as _EM_CONFIG
from ..functional.dfm_block import (
    build_lag_matrix,
    initialize_block_loadings,
    initialize_block_transition,
    build_slower_freq_observation_matrix,
    build_slower_freq_idiosyncratic_chain
)
from ..numeric.stability import rem_nans_spline
from ..numeric.stability import ensure_covariance_stable
from ..numeric.estimator import (
    estimate_ar1_unified,
    estimate_variance_unified,
)

if TYPE_CHECKING:
    from ..datamodule import DFMDataModule

_logger = get_logger(__name__)


# sort_data moved to datamodule.base._sort_data_by_config
# No longer needed in DFM model (handled by DataModule)


@dataclass
class DFMTrainingState:
    """State tracking for DFM training."""
    A: np.ndarray
    C: np.ndarray
    Q: np.ndarray
    R: np.ndarray
    Z_0: np.ndarray
    V_0: np.ndarray
    loglik: float
    num_iter: int
    converged: bool


class DFM(BaseFactorModel):
    """High-level API for Linear Dynamic Factor Model.
    
    This class implements the EM algorithm for DFM estimation using NumPy and pykalman.
    It inherits from BaseFactorModel (not PyTorch Lightning) since all calculations
    are performed in NumPy.
    
    **Note**: All calculations are performed in NumPy (using pykalman) for better
    numerical stability. Parameters are stored as NumPy arrays (no PyTorch dependencies).
    
    **Block Structure**: The model supports block-structured factors (factors organized
    in blocks). Block structure is established during initialization and is preserved
    during EM updates. pykalman handles the E-step (Kalman filter/smoother), while
    the M-step uses custom code that maintains block structure, mixed-frequency handling,
    and idiosyncratic components.
    
    Example (Standard Lightning Pattern):
        >>> from dfm_python import DFM, DFMDataModule, DFMTrainer
        >>> import pandas as pd
        >>> 
        >>> # Step 1: Load and preprocess data
        >>> df = pd.read_csv('data/finance.csv')
        >>> df_processed = df[[col for col in df.columns if col != 'date']]
        >>> 
        >>> # Step 2: Create DataModule
        >>> dm = DFMDataModule(config_path='config/dfm_config.yaml', data=df_processed)
        >>> dm.setup()
        >>> 
        >>> # Step 3: Create model and load config
        >>> model = DFM()
        >>> model.load_config('config/dfm_config.yaml')
        >>> 
        >>> # Step 4: Fit model
        >>> model.fit(X_torch, Mx=Mx, Wx=Wx)
        >>> 
        >>> # Step 5: Predict
        >>> Xf, Zf = model.predict(horizon=6)
    """
    
    def __init__(
        self,
        config: Optional[DFMConfig] = None,
        num_factors: Optional[int] = None,
        threshold: Optional[float] = None,
        max_iter: Optional[int] = None,
        nan_method: Optional[int] = None,
        nan_k: Optional[int] = None,
        mixed_freq: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        """Initialize DFM instance.
        
        Parameters
        ----------
        config : DFMConfig, optional
            DFM configuration. Can be loaded later via load_config().
        num_factors : int, optional
            Number of factors. If None, inferred from config.
        threshold : float, optional
            EM convergence threshold. Defaults to DEFAULT_CONVERGENCE_THRESHOLD.
        max_iter : int, optional
            Maximum EM iterations. Defaults to DEFAULT_MAX_ITER.
        nan_method : int, optional
            Missing data handling method (internal, defaults to DEFAULT_NAN_METHOD).
        nan_k : int, optional
            Spline interpolation order (internal, defaults to DEFAULT_NAN_K).
        mixed_freq : bool, optional
            Deprecated. Mixed frequency is now auto-detected from DataModule or config.
            If provided, overrides auto-detection. If None, auto-detects from DataModule during fit().
        **kwargs : Any
            Additional arguments passed to BaseFactorModel (for API consistency with KDFM/DDFM).
            
        Returns
        -------
        None
            Initializes DFM instance in-place.
            
        Raises
        ------
        ConfigurationError
            If config validation fails or required parameters are missing.
        ValueError
            If mixed_freq=True and frequency pairs are not in TENT_WEIGHTS_LOOKUP.
        """
        super().__init__()
        
        # Initialize config using consolidated helper method
        config = self._initialize_config(config)
        
        # Resolve parameters using consolidated helper
        from ..utils.misc import resolve_param
        self.threshold = resolve_param(threshold, default=DEFAULT_CONVERGENCE_THRESHOLD)
        self.max_iter = resolve_param(max_iter, default=DEFAULT_MAX_ITER)
        self.nan_method = resolve_param(nan_method, default=DEFAULT_NAN_METHOD)
        self.nan_k = resolve_param(nan_k, default=DEFAULT_NAN_K)
        # Mixed frequency: None means auto-detect from DataModule during fit()
        # If provided, use it (for backward compatibility)
        self._mixed_freq = mixed_freq  # Internal property, can be None
        
        # Mixed frequency parameters (set during fit)
        self._constraint_matrix = None  # R_mat: constraint matrix for tent kernel aggregation
        self._constraint_vector = None  # q: constraint vector for tent kernel aggregation
        self._n_slower_freq = 0  # Number of slower-frequency series
        self._tent_weights_dict = None
        self._frequencies = None
        self._idio_indicator = None  # i_idio: indicator for idiosyncratic components
        
        # Determine number of factors
        if num_factors is None:
            if get_config_attr(config, 'factors_per_block'):
                self.num_factors = int(np.sum(config.factors_per_block))
            else:
                blocks = config.get_blocks_array()
                if blocks.shape[1] > 0:
                    self.num_factors = int(np.sum(blocks[:, 0]))
                else:
                    self.num_factors = 1
        else:
            self.num_factors = num_factors
        
        # Get model structure (stored as NumPy arrays)
        self.r = np.array(
            config.factors_per_block if config.factors_per_block is not None
            else np.ones(config.get_blocks_array().shape[1]),
            dtype=DEFAULT_DTYPE
        )
        self.p = get_config_attr(config, 'ar_lag', default=1)
        self.blocks = np.array(config.get_blocks_array(), dtype=DEFAULT_DTYPE)
        
        # Parameters stored as NumPy arrays (no PyTorch dependencies)
        # Set during fit() and required for prediction
        self.A: Optional[np.ndarray] = None
        self.C: Optional[np.ndarray] = None
        self.Q: Optional[np.ndarray] = None
        self.R: Optional[np.ndarray] = None
        self.Z_0: Optional[np.ndarray] = None
        self.V_0: Optional[np.ndarray] = None
        
        
        # Training state
        self.Mx: Optional[np.ndarray] = None
        self.Wx: Optional[np.ndarray] = None
        self.data_processed: Optional[np.ndarray] = None
    
    def _check_parameters_initialized(self) -> None:
        """Check if model parameters are initialized (required for prediction).
        
        Raises
        ------
        ModelNotInitializedError
            If parameters are not initialized
        """
        from ..utils.validation import check_condition
        from ..utils.errors import ModelNotInitializedError
        
        check_condition(
            not any(p is None for p in [self.A, self.C, self.Q, self.R, self.Z_0, self.V_0]),
            ModelNotInitializedError,
            f"{self.__class__.__name__}: Model parameters not initialized",
            details="Parameters (A, C, Q, R, Z_0, V_0) are required but are None. Please call fit() first to initialize parameters"
        )
    
    def _update_parameters(self, A: np.ndarray, C: np.ndarray, Q: np.ndarray,
                          R: np.ndarray, Z_0: np.ndarray, V_0: np.ndarray) -> None:
        """Update model parameters from NumPy arrays.
        
        Parameters
        ----------
        A, C, Q, R, Z_0, V_0 : np.ndarray
            Parameter arrays
        """
        # Only convert dtype if necessary (avoid redundant conversions)
        def _ensure_dtype(arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
            if arr is None:
                return None
            return arr.astype(DEFAULT_DTYPE) if arr.dtype != DEFAULT_DTYPE else arr
        
        self.A = _ensure_dtype(A)
        self.C = _ensure_dtype(C)
        self.Q = _ensure_dtype(Q)
        self.R = _ensure_dtype(R)
        self.Z_0 = _ensure_dtype(Z_0)
        self.V_0 = _ensure_dtype(V_0)
    
    def _initialize_clock_freq_idio(
        self,
        res: np.ndarray,
        data_with_nans: np.ndarray,
        n_clock_freq: int,
        idio_indicator: Optional[np.ndarray],
        T: int,
        dtype: type = DEFAULT_DTYPE
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Initialize clock frequency idiosyncratic components (AR(1) for each series).
        
        Returns
        -------
        BM, SM, initViM
        """
        n_idio_clock = n_clock_freq if idio_indicator is None else int(np.sum(idio_indicator))
        BM = np.zeros((n_idio_clock, n_idio_clock), dtype=dtype)
        SM = np.zeros((n_idio_clock, n_idio_clock), dtype=dtype)
        
        idio_indices = np.where(idio_indicator > 0)[0] if idio_indicator is not None else np.arange(n_clock_freq, dtype=np.int32)
        default_ar_coef = _EM_CONFIG.slower_freq_ar_coef
        default_noise = _EM_CONFIG.default_process_noise
        
        for i, idx in enumerate(idio_indices):
            res_i = data_with_nans[:, idx]
            non_nan_mask = ~np.isnan(res_i)
            if np.sum(non_nan_mask) > 1:
                first_non_nan = np.where(non_nan_mask)[0][0]
                last_non_nan = np.where(non_nan_mask)[0][-1]
                res_i_clean = res[first_non_nan:last_non_nan + 1, idx]
                
                if len(res_i_clean) > 1:
                    try:
                        # Use unified AR(1) estimation with raw data
                        y_ar = res_i_clean[1:]
                        x_ar = res_i_clean[:-1].reshape(-1, 1)
                        A_diag, Q_diag = estimate_ar1_unified(
                            y=y_ar.reshape(-1, 1),  # (T-1 x 1)
                            x=x_ar,  # (T-1 x 1)
                            V_smooth=None,  # Raw data mode
                            regularization=_EM_CONFIG.matrix_regularization,
                            min_variance=default_noise,
                            default_ar_coef=default_ar_coef,
                            default_noise=default_noise,
                            dtype=dtype
                        )
                        BM[i, i] = A_diag[0] if len(A_diag) > 0 else default_ar_coef
                        SM[i, i] = Q_diag[0] if len(Q_diag) > 0 else default_noise
                    except (np.linalg.LinAlgError, ValueError):
                        BM[i, i] = default_ar_coef
                        SM[i, i] = default_noise
                else:
                    BM[i, i] = default_ar_coef
                    SM[i, i] = default_noise
            else:
                BM[i, i] = default_ar_coef
                SM[i, i] = default_noise
        
        # Initial covariance for clock frequency idio
        try:
            eye_BM = np.eye(n_idio_clock, dtype=dtype)
            BM_sq = BM ** 2
            diag_inv = 1.0 / np.diag(eye_BM - BM_sq)
            diag_inv = np.where(np.isfinite(diag_inv), diag_inv, np.ones_like(diag_inv))
            initViM = np.diag(diag_inv) @ SM
        except (np.linalg.LinAlgError, ValueError):
            initViM = SM.copy()
        
        return BM, SM, initViM
    
    def _initialize_block_factors(
        self,
        data_for_extraction: np.ndarray,
        data_with_nans: np.ndarray,
        blocks: np.ndarray,
        r: np.ndarray,
        n_blocks: int,
        n_clock_freq: int,
        tent_kernel_size: int,
        p: int,
        R_mat: Optional[np.ndarray],
        q: Optional[np.ndarray],
        N: int,
        T: int,
        indNaN: np.ndarray,
        max_lag_size: int,
        dtype: type = DEFAULT_DTYPE
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Initialize factors and transition matrices block-by-block using sequential PCA.
        
        **Block-by-block extraction process:**
        - Block 1: Extracts factors from original data (data_for_extraction starts as original data)
        - Block 2+: Extracts factors from residuals (data_for_extraction becomes residuals after each block)
        
        This ensures each block captures different variance components, with factors orthogonal across blocks.
        
        Parameters
        ----------
        data_for_extraction : np.ndarray
            Data matrix (T x N). For Block 1, this is the original data (after cleaning).
            For subsequent blocks, this becomes residuals after removing previous blocks' contributions.
        data_with_nans : np.ndarray
            Data matrix with NaNs preserved (T x N)
        blocks : np.ndarray
            Block structure array (N x n_blocks)
        r : np.ndarray
            Number of factors per block (n_blocks,)
        n_blocks : int
            Number of blocks
        n_clock_freq : int
            Number of clock frequency series
        tent_kernel_size : int
            Tent kernel size for mixed-frequency aggregation
        p : int
            VAR lag order
        R_mat : np.ndarray, optional
            Constraint matrix for tent kernel aggregation
        q : np.ndarray, optional
            Constraint vector for tent kernel aggregation
        N : int
            Total number of series
        T : int
            Number of time steps
        indNaN : np.ndarray
            Boolean array indicating missing values
        max_lag_size : int
            Maximum lag size for loading matrix
        dtype : type
            Data type
            
        Returns
        -------
        A_factors : np.ndarray
            Block-diagonal transition matrix for factors
        Q_factors : np.ndarray
            Block-diagonal process noise covariance for factors
        V_0_factors : np.ndarray
            Block-diagonal initial state covariance for factors
        C : np.ndarray
            Observation/loading matrix (N x total_factor_dim)
        """
        C_list = []
        A_list = []
        Q_list = []
        V_0_list = []
        
        # Process each block sequentially
        # Block 1: data_for_extraction = original data
        # Block 2+: data_for_extraction = residuals after previous blocks
        for block_idx in range(n_blocks):
            num_factors_block = int(r[block_idx])
            block_series_indices = np.where(blocks[:, block_idx] > 0)[0]
            clock_freq_indices = block_series_indices[block_series_indices < n_clock_freq]
            slower_freq_indices = block_series_indices[block_series_indices >= n_clock_freq]
            
            # Extract factors and loadings for this block
            # Block 1: Uses original data (data_for_extraction = original data)
            # Block 2+: Uses residuals (data_for_extraction = residuals after previous blocks)
            C_i, factors = initialize_block_loadings(
                data_for_extraction, data_with_nans, clock_freq_indices, slower_freq_indices,
                num_factors_block, tent_kernel_size, R_mat, q,
                N, max_lag_size, _EM_CONFIG.matrix_regularization, dtype
            )
            
            # Build lag matrix for transition equation
            lag_matrix = build_lag_matrix(factors, T, num_factors_block, tent_kernel_size, p, dtype)
            slower_freq_factors = lag_matrix[:, :num_factors_block * tent_kernel_size]
            
            # Pad and align factors
            if tent_kernel_size > 1 and slower_freq_factors.shape[0] < T:
                padding = np.zeros((tent_kernel_size - 1, slower_freq_factors.shape[1]), dtype=dtype)
                slower_freq_factors = np.vstack([padding, slower_freq_factors])
                if slower_freq_factors.shape[0] < T:
                    additional_padding = np.zeros((T - slower_freq_factors.shape[0], slower_freq_factors.shape[1]), dtype=dtype)
                    slower_freq_factors = np.vstack([slower_freq_factors, additional_padding])
                slower_freq_factors = slower_freq_factors[:T, :]
            
            # Update data_for_extraction: remove this block's contribution to get residuals for next block
            # After Block 1: data_for_extraction becomes residuals (original_data - Block1_contribution)
            # After Block 2: data_for_extraction becomes residuals (original_data - Block1 - Block2)
            if data_for_extraction.shape[0] != slower_freq_factors.shape[0]:
                slower_freq_factors = slower_freq_factors[:data_for_extraction.shape[0], :]
            data_for_extraction = data_for_extraction - slower_freq_factors @ C_i[:, :num_factors_block * tent_kernel_size].T
            data_with_nans = data_for_extraction.copy()
            data_with_nans[indNaN] = np.nan
            
            C_list.append(C_i)
            
            # Initialize transition matrices
            A_i, Q_i, V_0_i = initialize_block_transition(
                lag_matrix, factors, num_factors_block, max_lag_size, p, T,
                _EM_CONFIG.regularization, _EM_CONFIG.default_transition_coef,
                _EM_CONFIG.default_process_noise, _EM_CONFIG.matrix_regularization,
                _EM_CONFIG.eigenval_floor, dtype
            )
            
            A_list.append(A_i)
            Q_list.append(Q_i)
            V_0_list.append(V_0_i)
        
        # Concatenate loadings
        C = np.hstack(C_list) if C_list else np.zeros((N, 0), dtype=dtype)
        
        # Build block-diagonal matrices
        if A_list:
            A_factors = block_diag(*A_list)
            Q_factors = block_diag(*Q_list)
            V_0_factors = block_diag(*V_0_list)
        else:
            empty_matrix = np.zeros((0, 0), dtype=dtype)
            A_factors = Q_factors = V_0_factors = empty_matrix
        
        return A_factors, Q_factors, V_0_factors, C
    
    def _initialize_slower_freq_idio(
        self,
        R: np.ndarray,
        n_clock_freq: int,
        n_slower_freq: int,
        tent_kernel_size: int,
        dtype: type = DEFAULT_DTYPE
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Initialize slower frequency idiosyncratic components (tent kernel chain).
        
        Returns
        -------
        BQ, SQ, initViQ
        """
        if n_slower_freq == 0:
            empty_matrix = np.zeros((0, 0), dtype=dtype)
            return empty_matrix, empty_matrix, empty_matrix
        
        rho0 = _EM_CONFIG.slower_freq_ar_coef
        sig_e = np.diag(R[n_clock_freq:, n_clock_freq:]) / _EM_CONFIG.slower_freq_variance_denominator
        sig_e = np.where(np.isfinite(sig_e), sig_e, _EM_CONFIG.default_observation_noise)
        
        return build_slower_freq_idiosyncratic_chain(n_slower_freq, tent_kernel_size, rho0, sig_e, dtype)
    
    def _add_idiosyncratic_observation_matrix(
        self,
        C: np.ndarray,
        N: int,
        n_clock_freq: int,
        n_slower_freq: int,
        idio_indicator: Optional[np.ndarray],
        clock: str,
        tent_kernel_size: int,
        tent_weights_dict: Optional[Dict[str, np.ndarray]] = None,
        dtype: type = DEFAULT_DTYPE
    ) -> np.ndarray:
        """Add idiosyncratic components to observation matrix C.
        
        Returns
        -------
        C : np.ndarray
            Updated observation matrix with idiosyncratic components
        """
        # Clock frequency: identity matrix for each series
        if idio_indicator is not None:
            eyeN = np.eye(N, dtype=dtype)
            idio_indicator_bool = idio_indicator.astype(bool)
            C = np.hstack([C, eyeN[:, idio_indicator_bool]])
        else:
            # Default: all clock frequency series have idiosyncratic components
            if n_clock_freq > 0:
                C = np.hstack([C, np.eye(N, dtype=dtype)[:, :n_clock_freq]])
        
        # Slower frequency: tent kernel chain observation matrix
        if n_slower_freq > 0:
            # Determine slower frequency from tent_weights_dict or use first available
            slower_freq = None
            if tent_weights_dict:
                slower_freq = next((freq for freq in tent_weights_dict.keys() if freq != clock), None)
            
            # If not found, try slower frequencies from hierarchy (sorted by hierarchy value)
            if slower_freq is None:
                clock_hierarchy = FREQUENCY_HIERARCHY.get(clock, DEFAULT_HIERARCHY_VALUE)
                # Get all slower frequencies sorted by hierarchy (ascending)
                slower_freqs = sorted(
                    [freq for freq in FREQUENCY_HIERARCHY if FREQUENCY_HIERARCHY[freq] > clock_hierarchy],
                    key=lambda f: FREQUENCY_HIERARCHY[f]
                )
                for freq in slower_freqs:
                    if get_tent_weights(freq, clock) is not None:
                        slower_freq = freq
                        break
            
            # Fallback: use first available slower frequency from hierarchy
            if slower_freq is None:
                clock_hierarchy = FREQUENCY_HIERARCHY.get(clock, DEFAULT_HIERARCHY_VALUE)
                for freq in FREQUENCY_HIERARCHY:
                    if FREQUENCY_HIERARCHY[freq] > clock_hierarchy and get_tent_weights(freq, clock) is not None:
                        slower_freq = freq
                        break
            
            # Get tent weights
            if tent_weights_dict and slower_freq in tent_weights_dict:
                tent_weights = tent_weights_dict[slower_freq].astype(dtype)
            else:
                tent_weights = get_slower_freq_tent_weights(slower_freq or 'q', clock, tent_kernel_size, dtype)
            
            C_slower_freq = build_slower_freq_observation_matrix(N, n_clock_freq, n_slower_freq, tent_weights, dtype)
            C = np.hstack([C, C_slower_freq])
        
        return C
    
    def _initialize_observation_noise(
        self,
        data_with_nans: np.ndarray,
        N: int,
        idio_indicator: Optional[np.ndarray],
        n_clock_freq: int,
        dtype: type = DEFAULT_DTYPE
    ) -> np.ndarray:
        """Initialize observation noise covariance R from residuals.
        
        Returns
        -------
        R : np.ndarray
            Observation noise covariance (N x N, diagonal)
        """
        # Ensure 2D
        if data_with_nans.ndim != 2:
            data_with_nans = data_with_nans.reshape(-1, N) if data_with_nans.size > 0 else np.zeros((1, N), dtype=dtype)
        
        T_res, N_res = data_with_nans.shape
        default_obs_noise = _EM_CONFIG.default_observation_noise
        
        # Use unified variance estimation with raw residuals
        if T_res <= 1:
            from ..numeric.stability import create_scaled_identity
            R = create_scaled_identity(N_res, default_obs_noise, dtype)
        else:
            # Compute residuals (data itself, since we're initializing from raw data)
            R = estimate_variance_unified(
                residuals=data_with_nans,  # Raw data as "residuals" for initialization
                X=None,  # Not using smoothed expectations mode
                EZ=None,
                C=None,
                V_smooth=None,
                min_variance=default_obs_noise,
                default_variance=default_obs_noise,
                dtype=dtype
            )
        
        # Set variances for idiosyncratic series to default
        idio_indices = np.where(idio_indicator > 0)[0] if idio_indicator is not None else np.arange(n_clock_freq, dtype=np.int32)
        all_indices = np.unique(np.concatenate([idio_indices, np.arange(n_clock_freq, N, dtype=np.int32)]))
        R[np.ix_(all_indices, all_indices)] = np.diag(np.full(len(all_indices), default_obs_noise, dtype=dtype))
        
        return R
    
    def _initialize_parameters(
        self,
        x: np.ndarray,
        r: np.ndarray,
        p: int,
        blocks: np.ndarray,
        opt_nan: Dict[str, Any],
        R_mat: Optional[np.ndarray] = None,
        q: Optional[np.ndarray] = None,
        n_slower_freq: int = 0,
        idio_indicator: Optional[np.ndarray] = None,
        clock: str = DEFAULT_CLOCK_FREQUENCY,
        tent_weights_dict: Optional[Dict[str, np.ndarray]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Initialize DFM state-space parameters (A, C, Q, R, Z_0, V_0).
        
        Note: pykalman handles the E-step (Kalman filtering), but we still need to initialize
        the state-space structure because:
        1. Block structure must be established (factors organized by blocks)
        2. Mixed-frequency constraints need tent kernel setup
        3. Idiosyncratic components require initialization
        4. Initial parameter estimates are needed for EM algorithm
        
        This uses a sequential residual-based PCA approach:
        1. Handle missing data (spline interpolation)
        2. Extract factors block-by-block:
           - Block 1: PCA on original data (after cleaning)
           - Block 2+: PCA on residuals (after removing previous blocks' contributions)
        3. Build transition matrices for each block (VAR regression on extracted factors)
        4. Initialize idiosyncratic components (AR(1) for clock freq, tent chain for slower freq)
        
        **Key insight**: The first block extracts factors from original data. Subsequent blocks
        extract factors from residuals, ensuring each block captures different variance components
        and factors are orthogonal across blocks.
        
        Parameters
        ----------
        x : np.ndarray
            Standardized data matrix (T x N)
        r : np.ndarray
            Number of factors per block (n_blocks,)
        p : int
            AR lag order (typically 1)
        blocks : np.ndarray
            Block structure array (N x n_blocks)
        opt_nan : dict
            Missing data handling options {'method': int, 'k': int}
        R_mat : np.ndarray, optional
            Constraint matrix for tent kernel aggregation
        q : np.ndarray, optional
            Constraint vector for tent kernel aggregation
        n_slower_freq : int
            Number of slower-frequency series
        idio_indicator : np.ndarray, optional
            Indicator array (1 for clock frequency, 0 for slower frequencies)
        clock : str
            Clock frequency ('d', 'w', 'm', 'q', 'sa', 'a')
        tent_weights_dict : dict, optional
            Dictionary mapping frequency pairs to tent weights
            
        Returns
        -------
        A : np.ndarray
            Initial transition matrix (m x m)
        C : np.ndarray
            Initial observation/loading matrix (N x m)
        Q : np.ndarray
            Initial process noise covariance (m x m)
        R : np.ndarray
            Initial observation noise covariance (N x N)
        Z_0 : np.ndarray
            Initial state vector (m,)
        V_0 : np.ndarray
            Initial state covariance (m x m)
        """
        T, N = x.shape
        dtype = DEFAULT_DTYPE
        
        n_blocks = blocks.shape[1]
        n_clock_freq = N - n_slower_freq  # Number of clock frequency series
        
        # Handle missing data for initialization
        x_clean, indNaN = rem_nans_spline(x, method=opt_nan.get('method', 2), k=opt_nan.get('k', 3))
        
        # Remove any remaining NaN/inf
        x_clean = np.where(np.isfinite(x_clean), x_clean, 0.0)
        
        # Initialize data for factor extraction
        # NOTE: For Block 1, this is the original data (after cleaning).
        # For subsequent blocks, this becomes residuals after removing previous blocks' contributions.
        data_for_extraction = x_clean.copy()  # T x N - starts as original data
        data_with_nans = data_for_extraction.copy()
        data_with_nans[indNaN] = np.nan
        
        # Determine tent kernel size
        if R_mat is not None:
            tent_kernel_size = R_mat.shape[1]
        elif tent_weights_dict:
            # Use first available tent weights
            first_weights = next(iter(tent_weights_dict.values()))
            tent_kernel_size = len(first_weights)
        else:
            tent_kernel_size = _EM_CONFIG.tent_kernel_size
        max_lag_size = max(p, tent_kernel_size)
        
        # Set initial observations as NaN for slower-frequency aggregation
        if tent_kernel_size > 1:
            data_with_nans[:tent_kernel_size-1, :] = np.nan
        
        # Initialize factors and loadings block-by-block
        # Block 1 uses original data, subsequent blocks use residuals
        A_factors, Q_factors, V_0_factors, C = self._initialize_block_factors(
            data_for_extraction, data_with_nans, blocks, r, n_blocks, n_clock_freq, tent_kernel_size,
            p, R_mat, q, N, T, indNaN, max_lag_size, dtype
        )
        
        # === IDIOSYNCRATIC COMPONENTS ===
        C = self._add_idiosyncratic_observation_matrix(
            C, N, n_clock_freq, n_slower_freq, idio_indicator, clock, tent_kernel_size, tent_weights_dict, dtype
        )
        
        # Initialize R (observation noise covariance) from final residuals
        R = self._initialize_observation_noise(data_with_nans, N, idio_indicator, n_clock_freq, dtype)
        
        # === IDIOSYNCRATIC TRANSITION MATRICES ===
        # Clock frequency: AR(1) for each series
        # Use final residuals (after all blocks) for idiosyncratic component initialization
        BM, SM, initViM = self._initialize_clock_freq_idio(
            data_for_extraction, data_with_nans, n_clock_freq, idio_indicator, T, dtype=dtype
        )
        
        # Slower frequency: tent kernel chain
        BQ, SQ, initViQ = self._initialize_slower_freq_idio(
            R, n_clock_freq, n_slower_freq, tent_kernel_size, dtype=dtype
        )
        
        # Combine all transition matrices
        try:
            A = block_diag(A_factors, BM, BQ)
            Q = block_diag(Q_factors, SM, SQ)
            V_0 = block_diag(V_0_factors, initViM, initViQ)
        except (ValueError, np.linalg.LinAlgError) as e:
            error_msg = f"Failed to construct block-diagonal matrices: {e}. Check matrix dimensions and ensure all blocks are valid."
            _logger.error(error_msg)
            raise NumericalError(error_msg) from e
        
        # Initial state: Z_0 = zeros
        m = int(A.shape[0]) if A.size > 0 and len(A.shape) > 0 else 0
        Z_0 = np.zeros(m, dtype=DEFAULT_DTYPE)
        
        # Ensure V_0 is positive definite
        V_0 = ensure_covariance_stable(V_0, min_eigenval=_EM_CONFIG.eigenval_floor)
        
        # All arrays use DEFAULT_DTYPE, redundant conversions avoided in _update_parameters
        return A, C, Q, R, Z_0, V_0
    
    def fit(
        self,
        X: Union[np.ndarray, Any],
        Mx: Optional[np.ndarray] = None,
        Wx: Optional[np.ndarray] = None,
        datamodule: Optional[Any] = None
    ) -> DFMTrainingState:
        """Fit model using EM algorithm (wrapper around pykalman).
        
        Uses pykalman for E-step (Kalman filter/smoother) and custom M-step
        that preserves block structure and mixed-frequency constraints.
        
        Parameters
        ----------
        X : np.ndarray or torch.Tensor, optional
            Standardized data (T x N). If datamodule is provided, X can be None.
        Mx : np.ndarray, optional
            Mean values for unstandardization (N,). If datamodule is provided, Mx can be None.
        Wx : np.ndarray, optional
            Standard deviation values for unstandardization (N,). If datamodule is provided, Wx can be None.
        datamodule : DFMDataModule, optional
            Custom DFMDataModule instance. If provided, initialization parameters will be
            extracted from the datamodule instead of computing them directly.
            
        Returns
        -------
        DFMTrainingState
            Final training state with parameters and convergence info
        """
        # Use datamodule if provided
        if datamodule is not None:
            self._data_module = datamodule  # Store for later use in predict()
            init_params = datamodule.get_initialization_params()
            X_np = init_params['X']
            Mx = init_params['Mx'] if Mx is None else Mx
            Wx = init_params['Wx'] if Wx is None else Wx
            R_mat = init_params['R_mat']
            q = init_params['q']
            n_slower_freq = init_params['n_slower_freq']
            tent_weights_dict = init_params['tent_weights_dict']
            frequencies_np = init_params['frequencies']
            idio_indicator = init_params['idio_indicator']
            opt_nan = init_params['opt_nan']
            clock = init_params['clock']
            # Auto-detect mixed_freq from DataModule if not explicitly set
            is_mixed_freq = init_params.get('is_mixed_freq', False)
            if self._mixed_freq is None:
                self._mixed_freq = is_mixed_freq
        else:
            # Convert to NumPy using utility function
            from ..utils.common import ensure_numpy
            X_np = ensure_numpy(X, dtype=DEFAULT_DTYPE)
            
            # Setup mixed-frequency parameters (fallback if no datamodule)
            # Auto-detect from config if not explicitly set
            clock = getattr(self.config, 'clock', DEFAULT_CLOCK_FREQUENCY)
            
            # Auto-detect mixed frequency from config if not set
            if self._mixed_freq is None:
                # Try to detect from config frequencies
                frequencies = self.config.get_frequencies()
                clock_hierarchy = FREQUENCY_HIERARCHY.get(clock, DEFAULT_HIERARCHY_VALUE)
                self._mixed_freq = any(
                    FREQUENCY_HIERARCHY.get(freq, DEFAULT_HIERARCHY_VALUE) > clock_hierarchy
                    for freq in frequencies
                )
            
            mixed_freq = self._mixed_freq
            
            if not mixed_freq:
                R_mat = None
                q = None
                n_slower_freq = 0
                n_clock_freq = X_np.shape[1]  # All series are at clock frequency
                tent_weights_dict = None
                frequencies_np = None
                idio_indicator = np.ones(X_np.shape[1], dtype=DEFAULT_DTYPE)
            else:
                # Get frequencies using new API
                frequencies_list = self.config.get_frequencies()
                frequencies_set = set(frequencies_list) if frequencies_list else set()
                clock_hierarchy = FREQUENCY_HIERARCHY.get(clock, DEFAULT_HIERARCHY_VALUE)
                
                # Validate frequency pairs
                missing_pairs = [
                    (freq, clock) for freq in frequencies_set
                    if FREQUENCY_HIERARCHY.get(freq, DEFAULT_HIERARCHY_VALUE) > clock_hierarchy and get_tent_weights(freq, clock) is None
                ]
                if missing_pairs:
                    raise ConfigurationError(
                        f"Mixed-frequency data detected but the following frequency pairs are not in TENT_WEIGHTS_LOOKUP: {missing_pairs}",
                        details=f"Available pairs: {list(TENT_WEIGHTS_LOOKUP.keys())}"
                        f"Either add the missing pairs to TENT_WEIGHTS_LOOKUP or ensure all series use clock frequency."
                    )
                
                # Get aggregation structure
                agg_structure = get_agg_structure(self.config, clock=clock)
                tent_weights_dict = {k: np.array(v, dtype=DEFAULT_DTYPE) for k, v in agg_structure['tent_weights'].items()}
                
                R_mat = None
                q = None
                if agg_structure['structures']:
                    first_structure = list(agg_structure['structures'].values())[0]
                    R_mat = np.array(first_structure[0], dtype=DEFAULT_DTYPE)
                    q = np.array(first_structure[1], dtype=DEFAULT_DTYPE)
                
                # Compute frequency statistics
                clock_hierarchy = FREQUENCY_HIERARCHY.get(clock, DEFAULT_HIERARCHY_VALUE)
                frequencies_np = np.array([
                    FREQUENCY_HIERARCHY.get(f, FREQUENCY_HIERARCHY.get(DEFAULT_CLOCK_FREQUENCY, DEFAULT_HIERARCHY_VALUE))
                    for f in frequencies_list
                ], dtype=np.int32) if frequencies_list else None
                
                n_slower_freq = sum(1 for freq in frequencies_list if FREQUENCY_HIERARCHY.get(freq, DEFAULT_HIERARCHY_VALUE) > clock_hierarchy)
                n_clock_freq = len(frequencies_list) - n_slower_freq if frequencies_list else 0
                idio_indicator = np.array([1 if freq == clock else 0 for freq in frequencies_list], dtype=DEFAULT_DTYPE)
            
            opt_nan = {'method': self.nan_method, 'k': self.nan_k}
        
        self.Mx = Mx
        self.Wx = Wx
        self.data_processed = X_np
        
        # Store for reuse in EM steps
        self._constraint_matrix = R_mat
        self._constraint_vector = q
        self._n_slower_freq = n_slower_freq
        self._n_clock_freq = n_clock_freq if 'n_clock_freq' in locals() else (X_np.shape[1] - n_slower_freq if n_slower_freq is not None else None)
        self._tent_weights_dict = tent_weights_dict
        self._frequencies = frequencies_np
        self._idio_indicator = idio_indicator
        
        # Initialize parameters (required for EM algorithm)
        # Note: pykalman handles E-step, but we still need to initialize state-space structure
        A_np, C_np, Q_np, R_np, Z_0_np, V_0_np = self._initialize_parameters(
            X_np, self.r, self.p, self.blocks, opt_nan, R_mat, q, n_slower_freq, idio_indicator,
            clock, tent_weights_dict
        )
        self._update_parameters(A_np, C_np, Q_np, R_np, Z_0_np, V_0_np)
        
        # Validate initialization succeeded
        self._check_parameters_initialized()
        
        # Run EM algorithm using DFMKalmanFilter.em() method
        # Use stored n_clock_freq (already computed above)
        n_clock_freq = self._n_clock_freq
        
        # Create Kalman filter and run EM algorithm
        kalman_filter = DFMKalmanFilter(
            transition_matrices=self.A,
            observation_matrices=self.C,
            transition_covariance=self.Q,
            observation_covariance=self.R,
            initial_state_mean=self.Z_0,
            initial_state_covariance=self.V_0
        )
        
        final_state = kalman_filter.em(
            X=X_np,
            initial_params={
                'A': self.A, 'C': self.C, 'Q': self.Q,
                'R': self.R, 'Z_0': self.Z_0, 'V_0': self.V_0
            },
            max_iter=self.max_iter,
            threshold=self.threshold,
            config=_EM_CONFIG,
            blocks=self.blocks,
            r=self.r,
            p=self.p,
            p_plus_one=self.p + 1,
            R_mat=self._constraint_matrix,
            q=self._constraint_vector,
            n_clock_freq=n_clock_freq,
            n_slower_freq=n_slower_freq,
            idio_indicator=self._idio_indicator,
            tent_weights_dict=self._tent_weights_dict
        )
        
        # Update model parameters from final state
        self._update_parameters(
            final_state['A'], final_state['C'], final_state['Q'],
            final_state['R'], final_state['Z_0'], final_state['V_0']
        )
        
        self.training_state = DFMTrainingState(
            A=final_state['A'], C=final_state['C'], Q=final_state['Q'],
            R=final_state['R'], Z_0=final_state['Z_0'], V_0=final_state['V_0'],
            loglik=final_state['loglik'], num_iter=final_state['num_iter'],
            converged=final_state['converged']
        )
        
        return self.training_state
    
    def _compute_smoothed_factors(self) -> np.ndarray:
        """Compute smoothed factors using Kalman filter.
        
        Returns
        -------
        np.ndarray
            Smoothed factors (T x m)
        """
        if self.training_state is None or self.data_processed is None:
            raise ModelNotTrainedError(
                "Model not fitted or data not available",
                details="Please call fit() method before computing smoothed factors"
            )
        
        kalman_final = DFMKalmanFilter(
            transition_matrices=self.training_state.A,
            observation_matrices=self.training_state.C,
            transition_covariance=self.training_state.Q,
            observation_covariance=self.training_state.R,
            initial_state_mean=self.training_state.Z_0,
            initial_state_covariance=self.training_state.V_0
        )
        
        y_masked = np.ma.masked_invalid(self.data_processed)
        smoothed_state_means, _ = kalman_final.smooth(y_masked)
        return smoothed_state_means
    
    def get_result(self) -> DFMResult:
        """Extract DFMResult from trained model.
        
        Returns
        -------
        DFMResult
            Estimation results with parameters, factors, and diagnostics
        """
        if self.training_state is None:
            raise ModelNotTrainedError(
                "DFM get_result failed: model has not been fitted yet",
                details="Please call fit() method first"
            )
        if self.data_processed is None:
            raise ModelNotTrainedError(
                "DFM get_result failed: data not available",
                details="Please ensure fit() was called with data"
            )
        
        # Compute smoothed factors
        Z = self._compute_smoothed_factors()
        
        # Get parameters
        A = self.training_state.A
        C = self.training_state.C
        Q = self.training_state.Q
        R = self.training_state.R
        Z_0 = self.training_state.Z_0
        V_0 = self.training_state.V_0
        
        # Compute smoothed data
        x_sm = Z @ C.T
        
        # Get target scaler from datamodule if available
        target_scaler = getattr(self, 'target_scaler', None)
        
        return DFMResult(
            x_sm=x_sm, Z=Z, C=C, R=R, A=A, Q=Q,
            target_scaler=target_scaler,
            Z_0=Z_0, V_0=V_0, r=self.r, p=self.p,
            converged=self.training_state.converged,
            num_iter=self.training_state.num_iter,
            loglik=self.training_state.loglik
        )
    
    
    def load_config(
        self,
        source: Optional[Union[str, Path, Dict[str, Any], DFMConfig, ConfigSource]] = None,
        *,
        yaml: Optional[Union[str, Path]] = None,
        mapping: Optional[Dict[str, Any]] = None,
        hydra: Optional[Union[Dict[str, Any], Any]] = None,
        base: Optional[Union[str, Path, Dict[str, Any], ConfigSource]] = None,
        override: Optional[Union[str, Path, Dict[str, Any], ConfigSource]] = None,
    ) -> 'DFM':
        """Load configuration from various sources.
        
        After loading config, the model needs to be re-initialized with the new config.
        For standard Lightning pattern, pass config directly to __init__.
        """
        # Use common config loading logic
        new_config = self._load_config_common(
            source=source,
            yaml=yaml,
            mapping=mapping,
            hydra=hydra,
            base=base,
            override=override,
        )
        
        # DFM-specific: Initialize r and blocks arrays
        self.r = np.array(
            new_config.factors_per_block if new_config.factors_per_block is not None
            else np.ones(new_config.get_blocks_array().shape[1]),
            dtype=DEFAULT_DTYPE
        )
        self.blocks = np.array(new_config.get_blocks_array(), dtype=DEFAULT_DTYPE)
        
        return self
    
    
    
    def predict(
        self,
        horizon: Optional[int] = None,
        *,
        return_series: bool = True,
        return_factors: bool = True
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Forecast future values.
        
        This method can be called after training. It uses the training state
        from the Lightning module to generate forecasts.
        
        Target series are determined from the DataModule's target_series attribute,
        which should be set during DataModule initialization.
        
        Parameters
        ----------
        horizon : int, optional
            Number of periods ahead to forecast. If None, defaults to 1 year
            of periods based on clock frequency.
        return_series : bool, optional
            Whether to return forecasted series (default: True)
        return_factors : bool, optional
            Whether to return forecasted factors (default: True)
            
        Returns
        -------
        np.ndarray or Tuple[np.ndarray, np.ndarray]
            If both return_series and return_factors are True:
                (X_forecast, Z_forecast) tuple
            If only return_series is True:
                X_forecast (horizon x len(target_series))
            If only return_factors is True:
                Z_forecast (horizon x m)
            
        Raises
        ------
        ValueError
            If DataModule has no target_series set
        """
        if self.training_state is None:
            raise ModelNotTrainedError(
                f"{self.__class__.__name__} prediction failed: model has not been trained yet",
                details="Please call fit() first"
            )
        
        # Validate parameters are initialized
        self._check_parameters_initialized()
        
        # Get result (only call get_result() if _result is None)
        if not hasattr(self, '_result') or self._result is None:
            self._result = self.get_result()
        
        result = self._result
        
        if result.Z is None:
            raise ModelNotTrainedError(
                "DFM prediction failed: result.Z is not available",
                details="This may indicate the model was not properly trained or result object is corrupted"
            )
        
        # Compute default horizon using consolidated helper
        if horizon is None:
            horizon = self._compute_default_horizon()
        
        # Validate horizon
        if horizon <= 0:
            raise PredictionError(
                f"horizon must be positive, got {horizon}",
                details="Forecast horizon must be a positive integer"
            )
        
        # Extract model parameters
        A = result.A
        C = result.C
        Wx = result.Wx
        Mx = result.Mx
        p = result.p  # VAR order (always available after training)
        
        # Use training state for initial factor state
        # For DFM, we use the last smoothed state from training
        # History-based updates can be added later if needed
        Z_last = result.Z[-1, :] if result.Z.shape[0] > 0 else np.zeros(result.A.shape[0], dtype=DEFAULT_DTYPE)
        
        # Validate factor state
        if np.any(np.isnan(Z_last)):
            nan_count = np.sum(np.isnan(Z_last))
            nan_ratio = nan_count / len(Z_last)
            raise NumericalError(
                f"DFM prediction failed: {nan_count}/{len(Z_last)} factors contain NaN ({nan_ratio:.1%})",
                details="Model may not have converged. Try increasing max_iter or checking data quality"
            )
        
        # Validate parameters are finite
        if np.any(~np.isfinite(A)) or np.any(~np.isfinite(C)):
            raise NumericalError(
                "DFM prediction failed: model parameters (A or C) contain NaN/Inf",
                details="Check training convergence and data quality"
            )
        
        # Resolve target series from DataModule (target_series should be set at initialization)
        series_ids = self._config.get_series_ids() if self._config is not None else result.series_ids
        target_series, target_indices = self._resolve_target_series(None, series_ids, result)
        
        if target_series is None or len(target_series) == 0:
            raise ValueError(
                "DFM prediction failed: no target_series found in DataModule. "
                "Please set target_series when creating the DataModule (e.g., DFMDataModule(..., target_series=['series_id']))."
            )
        
        if target_indices is None or len(target_indices) == 0:
            raise DataError(
                f"DFM prediction failed: none of the target series found in available series",
                details=f"Target: {target_series}, Available: {series_ids}"
            )
        
        # Forecast factors using VAR dynamics (common helper)
        Z_prev = result.Z[-2, :] if result.Z.shape[0] >= 2 and p == 2 else None
        Z_forecast = self._forecast_var_factors(
            Z_last=Z_last,
            A=A,
            p=p,
            horizon=horizon,
            Z_prev=Z_prev
        )
        
        # Optimized: Transform only target series (not all series)
        # Use only target indices for C, Mx, Wx
        C_target = C[target_indices, :]  # (len(target) x m)
        Mx_target = Mx[target_indices] if Mx is not None else None
        Wx_target = Wx[target_indices] if Wx is not None else None
        
        # Transform factors to target observations only
        X_forecast_std = Z_forecast @ C_target.T  # (horizon x len(target))
        X_forecast = X_forecast_std * Wx_target + Mx_target  # (horizon x len(target))
        
        # Validate forecast results are finite
        if np.any(~np.isfinite(X_forecast)):
            nan_count = np.sum(~np.isfinite(X_forecast))
            raise NumericalError(
                f"DFM prediction failed: produced {nan_count} NaN/Inf values in forecast",
                details="Possible numerical instability. Check model parameters, training convergence, and data quality."
            )
        
        # Ensure X_forecast is numpy array (handles torch inputs if present)
        from ..utils.common import ensure_numpy
        X_forecast = ensure_numpy(X_forecast, dtype=DEFAULT_DTYPE)
        
        # Validate forecast values are within reasonable bounds (only for target series now)
        if Wx_target is not None and Mx_target is not None and len(Wx_target) > 0 and len(Mx_target) > 0:
            # Check each target series individually
            extreme_threshold_std = _EM_CONFIG.extreme_forecast_threshold
            for i in range(X_forecast.shape[1] if X_forecast.ndim > 1 else 1):
                if i < len(Wx_target) and i < len(Mx_target) and Wx_target[i] > 0:
                    series_forecast = X_forecast[:, i] if X_forecast.ndim > 1 else X_forecast
                    series_mean = Mx_target[i]
                    series_std = Wx_target[i]
                    # Calculate how many standard deviations each forecast is from the mean
                    abs_deviations = np.abs(series_forecast - series_mean) / series_std
                    max_deviation = np.max(abs_deviations) if len(abs_deviations) > 0 else 0.0
                    if max_deviation > extreme_threshold_std:
                        extreme_count = np.sum(abs_deviations > extreme_threshold_std)
                        _logger.warning(
                            f"DFM prediction: Extreme forecast for target series {i} "
                            f"(max deviation: {max_deviation:.1f} std devs). "
                            f"Possible numerical instability."
                        )
        
        if return_factors:
            from ..utils.helper import validate_finite_array, get_config_attr
            validate_finite_array(Z_forecast, "factor forecast", context="DFM prediction")
        
        if return_series and return_factors:
            return X_forecast, Z_forecast
        if return_series:
            return X_forecast
        return Z_forecast
    
    @property
    def result(self) -> DFMResult:
        """Get model result from training state.
        
        Raises
        ------
        ValueError
            If model has not been trained yet
        """
        # Check if trained and extract result from training state if needed
        self._check_trained()
        if self._result is None:
            # Generate result from training state if not already computed
            self._result = self.get_result()
        if not isinstance(self._result, DFMResult):
            raise ModelNotTrainedError(
                f"Expected DFMResult but got {type(self._result)}",
                details="Model result type mismatch. Please ensure model was properly trained"
            )
        return self._result
    
    
    
    def reset(self) -> 'DFM':
        """Reset model state."""
        super().reset()
        return self

