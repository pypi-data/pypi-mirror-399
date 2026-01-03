"""Estimation functions for state-space model parameters.

This module provides functions for estimating VAR dynamics, AR coefficients,
and idiosyncratic component parameters from data. Also includes AR coefficient
clipping utilities for numerical stability.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..functional.em import EMConfig

from ..logger import get_logger
from ..config.constants import (
    MIN_DIAGONAL_VARIANCE,
    MIN_FACTOR_VARIANCE,
    DEFAULT_REGULARIZATION,
    MIN_EIGENVALUE,
    VAR_STABILITY_THRESHOLD,
    AR_CLIP_MIN,
    AR_CLIP_MAX,
    MIN_Q_FLOOR,
    DEFAULT_CLEAN_NAN,
    DEFAULT_CLEAN_INF,
    DEFAULT_IDENTITY_SCALE,
    DEFAULT_ZERO_VALUE,
    DEFAULT_PROCESS_NOISE,
    DEFAULT_TRANSITION_COEF,
)
from .stability import (
    clean_matrix,
    cap_max_eigenval,
    compute_var_safe,
    compute_cov_safe,
    ensure_covariance_stable,
    solve_regularized_ols,
    stabilize_innovation_covariance,
    create_scaled_identity,
)
from ..utils.helper import handle_linear_algebra_error, get_config_attr

_logger = get_logger(__name__)

# Numerical stability constants
MIN_VARIANCE_COVARIANCE = MIN_FACTOR_VARIANCE
DEFAULT_VARIANCE_FALLBACK = 1.0


# ============================================================================
# AR Coefficient Clipping
# ============================================================================

def clip_ar(
    A: np.ndarray,
    min_val: float = AR_CLIP_MIN,
    max_val: float = AR_CLIP_MAX,
    warn: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Clip AR coefficients to stability bounds.
    
    Parameters
    ----------
    A : np.ndarray
        AR coefficients to clip
    min_val : float, default AR_CLIP_MIN
        Minimum allowed value
    max_val : float, default AR_CLIP_MAX
        Maximum allowed value
    warn : bool, default True
        Whether to log warnings
        
    Returns
    -------
    A_clipped : np.ndarray
        Clipped AR coefficients
    stats : dict
        Statistics about clipping
    """
    A_flat = A.flatten()
    n_total = len(A_flat)
    below_min = A_flat < min_val
    above_max = A_flat > max_val
    needs_clip = below_min | above_max
    n_clipped = np.sum(needs_clip)
    A_clipped = np.clip(A, min_val, max_val)
    stats = {
        'n_clipped': int(n_clipped),
        'n_total': int(n_total),
        'clipped_indices': np.where(needs_clip)[0].tolist() if n_clipped > 0 else [],
        'min_violations': int(np.sum(below_min)),
        'max_violations': int(np.sum(above_max))
    }
    if warn and n_clipped > 0:
        pct_clipped = 100.0 * n_clipped / n_total if n_total > 0 else 0.0
        _logger.warning(
            f"AR coefficient clipping applied: {n_clipped}/{n_total} ({pct_clipped:.1f}%) "
            f"coefficients clipped to [{min_val}, {max_val}]."
        )
    return A_clipped, stats


def apply_ar_clipping(
    A: np.ndarray,
    config: Optional["EMConfig"] = None
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Apply AR coefficient clipping based on configuration.
    
    Parameters
    ----------
    A : np.ndarray
        AR coefficients
    config : object, optional
        Configuration object with clipping parameters
        
    Returns
    -------
    A_clipped : np.ndarray
        Clipped AR coefficients
    stats : dict
        Statistics about clipping
    """
    if config is None:
        return clip_ar(A, AR_CLIP_MIN, AR_CLIP_MAX, True)
    
    clip_enabled = get_config_attr(config, 'clip_ar_coefficients', True)
    if not clip_enabled:
        return A, {'n_clipped': 0, 'n_total': A.size, 'clipped_indices': []}
    
    min_val = get_config_attr(config, 'ar_clip_min', AR_CLIP_MIN)
    max_val = get_config_attr(config, 'ar_clip_max', AR_CLIP_MAX)
    warn = get_config_attr(config, 'warn_on_ar_clip', True)
    return clip_ar(A, min_val, max_val, warn)


def estimate_ar(
    EZZ_FB: np.ndarray,
    EZZ_BB: np.ndarray,
    vsmooth_sum: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Estimate AR coefficients and innovation variances from expectations.
    
    Parameters
    ----------
    EZZ_FB : np.ndarray
        Forward-backward expectation E[z_t z_{t-1}']
    EZZ_BB : np.ndarray
        Backward-backward expectation E[z_{t-1} z_{t-1}']
    vsmooth_sum : np.ndarray, optional
        Sum of smoothing variances
        
    Returns
    -------
    A_diag : np.ndarray
        AR coefficients (diagonal)
    Q_diag : np.ndarray or None
        Innovation variances (diagonal, currently None)
    """
    if np.isscalar(EZZ_FB):
        EZZ_FB = np.array([EZZ_FB])
        EZZ_BB = np.array([EZZ_BB])
    if EZZ_FB.ndim > 1:
        EZZ_FB_diag = np.diag(EZZ_FB).copy()
        EZZ_BB_diag = np.diag(EZZ_BB).copy()
    else:
        EZZ_FB_diag = EZZ_FB.copy()
        EZZ_BB_diag = EZZ_BB.copy()
    if vsmooth_sum is not None:
        if vsmooth_sum.ndim > 1:
            vsmooth_diag = np.diag(vsmooth_sum)
        else:
            vsmooth_diag = vsmooth_sum
        EZZ_BB_diag = EZZ_BB_diag + vsmooth_diag
    min_denom = np.maximum(np.abs(EZZ_BB_diag) * MIN_DIAGONAL_VARIANCE, MIN_VARIANCE_COVARIANCE)
    EZZ_BB_diag = np.where(
        (np.isnan(EZZ_BB_diag) | np.isinf(EZZ_BB_diag) | (np.abs(EZZ_BB_diag) < min_denom)),
        min_denom, EZZ_BB_diag
    )
    # Use clean_matrix for consistency
    if EZZ_FB_diag.ndim == 0:
        EZZ_FB_diag_clean = clean_matrix(np.array([EZZ_FB_diag]), 'general', default_nan=DEFAULT_CLEAN_NAN, default_inf=DEFAULT_CLEAN_INF)
        EZZ_FB_diag = EZZ_FB_diag_clean[0] if EZZ_FB_diag_clean.size > 0 else DEFAULT_ZERO_VALUE
    else:
        EZZ_FB_diag = clean_matrix(EZZ_FB_diag, 'general', default_nan=DEFAULT_CLEAN_NAN, default_inf=DEFAULT_CLEAN_INF)
    A_diag = EZZ_FB_diag / EZZ_BB_diag
    # Q_diag is not computed here (returns None for compatibility)
    Q_diag: Optional[np.ndarray] = None
    return A_diag, Q_diag


def estimate_var(factors: np.ndarray, order: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """Estimate VAR dynamics for factors.
    
    Supports VAR(1) and VAR(2) estimation. VAR(2) is the maximum supported order.
    
    Parameters
    ----------
    factors : np.ndarray
        Extracted factors (T x m)
    order : int, default 1
        VAR order (1 or 2)
        
    Returns
    -------
    A : np.ndarray
        Transition matrix (m x m) for order=1, or (m x 2m) = [A1, A2] for order=2
    Q : np.ndarray
        Innovation covariance (m x m)
        
    Raises
    ------
    ValueError
        If order is not 1 or 2
    """
    if order not in (1, 2):
        raise ValueError(f"VAR order must be 1 or 2, got {order}")
    
    T, m = factors.shape
    
    if order == 1:
        if T < 2:
            # Not enough data, use identity
            A = create_scaled_identity(m, DEFAULT_IDENTITY_SCALE)
            Q = create_scaled_identity(m, DEFAULT_PROCESS_NOISE)
            return A, Q
        
        # Prepare data for OLS: f_t = A @ f_{t-1}
        Y = factors[1:, :]  # T-1 x m (dependent)
        X = factors[:-1, :]  # T-1 x m (independent)
        
        # OLS: A = (X'X)^{-1} X'Y
        A = solve_regularized_ols(X, Y, regularization=DEFAULT_REGULARIZATION).T
        
        # Ensure stability: clip eigenvalues
        eigenvals = np.linalg.eigvals(A)
        max_eigenval = np.max(np.abs(eigenvals))
        if max_eigenval >= VAR_STABILITY_THRESHOLD:
            A = A * (VAR_STABILITY_THRESHOLD / max_eigenval)
        
        # Estimate innovation covariance
        residuals = Y - X @ A.T
        Q = compute_cov_safe(residuals.T, rowvar=True, pairwise_complete=False)
        
        # Stabilize Q: symmetrize, ensure positive definite, apply floor
        Q = stabilize_innovation_covariance(Q, min_eigenval=MIN_EIGENVALUE, min_floor=MIN_Q_FLOOR, dtype=np.float32)
        
        return A, Q
    
    else:  # order == 2
        if T < 3:
            # Not enough data, use VAR(1) fallback
            _logger.warning(
                f"Insufficient data (T={T}) for VAR(2). Falling back to VAR(1)."
            )
            A1, Q = estimate_var(factors, order=1)
            # Pad A to VAR(2) format: [A1, A2] where A2 = 0
            A = np.hstack([A1, np.zeros((A1.shape[0], A1.shape[1]))])
            return A, Q
        
        # Prepare data for VAR(2): f_t = A1 @ f_{t-1} + A2 @ f_{t-2}
        Y = factors[2:, :]  # T-2 x m (dependent)
        X = np.hstack((factors[1:-1, :], factors[:-2, :]))  # T-2 x 2m (independent)
        
        # OLS: A = (X'X)^{-1} X'Y, where A = [A1, A2]
        A = solve_regularized_ols(X, Y, regularization=DEFAULT_REGULARIZATION).T
        
        # Split into A1 and A2
        A1 = A[:, :m]
        A2 = A[:, m:]
        
        # Ensure stability: check eigenvalues of companion form
        companion = np.block([
            [A1, A2],
            [create_scaled_identity(m, DEFAULT_IDENTITY_SCALE), np.zeros((m, m))]
        ])
        eigenvals = np.linalg.eigvals(companion)
        max_eigenval = np.max(np.abs(eigenvals))
        if max_eigenval >= VAR_STABILITY_THRESHOLD:
            scale = VAR_STABILITY_THRESHOLD / max_eigenval
            A1 = A1 * scale
            A2 = A2 * scale
            A = np.hstack((A1, A2))
        
        # Estimate innovation covariance
        residuals = Y - X @ A.T
        Q = compute_cov_safe(residuals.T, rowvar=True, pairwise_complete=False)
        
        # Stabilize Q: symmetrize, ensure positive definite, apply floor
        Q = stabilize_innovation_covariance(Q, min_eigenval=MIN_EIGENVALUE, min_floor=MIN_Q_FLOOR, dtype=np.float32)
        
        return A, Q



def estimate_idio_dynamics(
    residuals: np.ndarray,
    missing_mask: np.ndarray,
    min_obs: int = 5,
) -> Tuple[np.ndarray, np.ndarray]:
    """Estimate AR(1) dynamics for idiosyncratic components.
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals from observation equation (T x N)
    missing_mask : np.ndarray
        Missing data mask (T x N), True where data is missing
    min_obs : int, default 5
        Minimum number of observations required for estimation
        
    Returns
    -------
    A_eps : np.ndarray
        AR(1) coefficients (N x N), diagonal matrix
    Q_eps : np.ndarray
        Innovation covariance (N x N), diagonal matrix
    """
    T, N = residuals.shape
    A_eps = np.zeros((N, N))
    Q_eps = np.zeros((N, N))
    
    for j in range(N):
        # Find valid consecutive pairs (both t-1 and t must be non-missing)
        valid = ~missing_mask[:, j]
        valid_pairs = valid[:-1] & valid[1:]
        
        if np.sum(valid_pairs) < min_obs:
            # Insufficient data: use zero AR(1) coefficient
            _logger.warning(
                f"Insufficient observations ({np.sum(valid_pairs)}) for idio AR(1) "
                f"estimation for series {j}. Using zero AR(1) coefficient."
            )
            A_eps[j, j] = DEFAULT_ZERO_VALUE
            # Use variance of available residuals
            if np.sum(valid) > 0:
                Q_eps[j, j] = compute_var_safe(residuals[valid, j], ddof=0, min_variance=MIN_DIAGONAL_VARIANCE)
            else:
                Q_eps[j, j] = MIN_DIAGONAL_VARIANCE
        else:
            # Extract valid consecutive pairs
            eps_t = residuals[1:, j][valid_pairs]
            eps_t_1 = residuals[:-1, j][valid_pairs]
            
            # Estimate AR(1) coefficient using covariance
            var_eps_t_1 = compute_var_safe(eps_t_1, ddof=0, min_variance=MIN_FACTOR_VARIANCE)
            if var_eps_t_1 > MIN_FACTOR_VARIANCE:
                cov_matrix = compute_cov_safe(np.vstack([eps_t, eps_t_1]), rowvar=True, pairwise_complete=False)
                cov_eps = cov_matrix[0, 1]
                A_eps[j, j] = cov_eps / var_eps_t_1
                
                # Ensure stability: clip AR(1) coefficient
                if abs(A_eps[j, j]) >= VAR_STABILITY_THRESHOLD:
                    sign = np.sign(A_eps[j, j])
                    A_eps[j, j] = sign * VAR_STABILITY_THRESHOLD
                    _logger.debug(
                        f"AR(1) coefficient for series {j} clipped to {A_eps[j, j]:.4f} for stability"
                    )
            else:
                A_eps[j, j] = 0.0
            
            # Estimate innovation covariance
            residuals_ar = eps_t - A_eps[j, j] * eps_t_1
            Q_eps[j, j] = compute_var_safe(residuals_ar, ddof=0, min_variance=MIN_DIAGONAL_VARIANCE)
    
    return A_eps, Q_eps


def estimate_idio_params(
    eps: np.ndarray,
    idx_no_missings: Optional[np.ndarray] = None,
    min_obs: int = 5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Estimate AR(1) parameters for idiosyncratic components.
    
    Falls back to zero-coefficient models when insufficient observations are
    available instead of raising errors, ensuring downstream pipelines remain
    robust.
    
    Parameters
    ----------
    eps : np.ndarray
        Idiosyncratic residuals (T x N)
    idx_no_missings : np.ndarray, optional
        Boolean mask (T x N) indicating non-missing values
    min_obs : int, default 5
        Minimum number of observations required
        
    Returns
    -------
    phi : np.ndarray
        AR(1) coefficients (N x N), diagonal
    mu_eps : np.ndarray
        Mean of idiosyncratic components (N,)
    std_eps : np.ndarray
        Standard deviation of idiosyncratic components (N,)
    """
    T, N = eps.shape
    phi = np.zeros((N, N))
    mu_eps = np.zeros(N)
    std_eps = np.zeros(N)
    
    if idx_no_missings is None:
        idx_no_missings = np.ones((T, N), dtype=bool)
    
    insufficient_series = []
    
    for j in range(N):
        mask = idx_no_missings[:, j]
        observed = eps[mask, j]
        
        if observed.size == 0:
            mu_eps[j] = DEFAULT_ZERO_VALUE
            std_eps[j] = MIN_DIAGONAL_VARIANCE
            insufficient_series.append((j, 0))
            continue
        
        mu_eps[j] = float(np.mean(observed))
        std_eps_j = float(np.std(observed))
        std_eps[j] = max(std_eps_j, 1e-8)
        
        valid_pairs = mask[:-1] & mask[1:]
        pair_count = int(np.sum(valid_pairs))
        
        if pair_count < max(min_obs, 1):
            insufficient_series.append((j, pair_count))
            continue
        
        eps_t = eps[1:, j][valid_pairs]
        eps_t_1 = eps[:-1, j][valid_pairs]
        var_prev = compute_var_safe(eps_t_1, ddof=0, min_variance=MIN_FACTOR_VARIANCE)
        
        if var_prev < MIN_FACTOR_VARIANCE:
            insufficient_series.append((j, pair_count))
            continue
        
        cov_matrix = compute_cov_safe(np.vstack([eps_t, eps_t_1]), rowvar=True, pairwise_complete=False)
        cov_eps = cov_matrix[0, 1]
        coeff = cov_eps / var_prev
        # Use clip_ar for consistency
        coeff_clipped, _ = clip_ar(np.array([[coeff]]), warn=False)
        phi[j, j] = float(coeff_clipped[0, 0])
    
    if insufficient_series:
        from ..config.constants import MAX_WARNING_ITEMS
        preview = ", ".join(f"{idx}:{cnt}" for idx, cnt in insufficient_series[:MAX_WARNING_ITEMS])
        more = ""
        if len(insufficient_series) > 5:
            more = f", ... (+{len(insufficient_series) - 5} more)"
        _logger.warning(
            "Falling back to zero AR coefficients for %d series (insufficient observations). "
            "Series indices and available pairs: %s%s",
            len(insufficient_series),
            preview,
            more,
        )
    
    return phi, mu_eps, std_eps


def estimate_state_space_params(
    f_t: np.ndarray,
    eps_t: np.ndarray,
    factor_order: int,
    bool_no_miss: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Estimate state-space transition parameters from factors and residuals.
    
    Estimates the transition matrix A, innovation covariance W, initial mean mu_0,
    initial covariance Σ_0, and latent states x_t for the companion form state-space
    representation.
    
    Parameters
    ----------
    f_t : np.ndarray
        Common factors (T x m)
    eps_t : np.ndarray
        Idiosyncratic terms (T x N)
    factor_order : int
        Lag order for common factors. Only VAR(1) and VAR(2) are supported.
    bool_no_miss : np.ndarray, optional
        Boolean array (T x N) indicating non-missing values.
        If None, assumes no missing values.
        
    Returns
    -------
    A : np.ndarray
        Transition matrix (state_dim x state_dim) in companion form
    W : np.ndarray
        Innovation covariance matrix (state_dim x state_dim), diagonal
    mu_0 : np.ndarray
        Unconditional mean of initial state (state_dim,)
    Σ_0 : np.ndarray
        Unconditional covariance of initial state (state_dim x state_dim)
    x_t : np.ndarray
        Latent states (state_dim x T) in companion form
    """
    T, m = f_t.shape
    T_eps, N = eps_t.shape
    
    if T != T_eps:
        raise ValueError(f"Time dimension mismatch: f_t has {T} timesteps, eps_t has {T_eps}")
    
    # Estimate factor dynamics (VAR)
    if factor_order == 2:
        if T < 3:
            raise ValueError("Insufficient data for VAR(2). Need at least 3 timesteps.")
        f_past = np.hstack((f_t[1:-1, :], f_t[:-2, :]))  # (T-2) x 2m
        f_future = f_t[2:, :]  # (T-2) x m
        # OLS: A_f = (f_past' @ f_past)^{-1} @ f_past' @ f_future
        A_f = solve_regularized_ols(f_past, f_future, regularization=DEFAULT_REGULARIZATION).T
        # Split into A1 and A2
        A1 = A_f[:, :m]  # m x m
        A2 = A_f[:, m:]  # m x m
    elif factor_order == 1:
        if T < 2:
            raise ValueError("Insufficient data for VAR(1). Need at least 2 timesteps.")
        f_past = f_t[:-1, :]  # (T-1) x m
        f_future = f_t[1:, :]  # (T-1) x m
        # OLS: A_f = (f_past' @ f_past)^{-1} @ f_past' @ f_future
        A_f = solve_regularized_ols(f_past, f_future, regularization=DEFAULT_REGULARIZATION).T
        A1 = A_f
        A2 = np.zeros((m, m))  # VAR(1) doesn't use A2, but set to zeros for consistency
    else:
        raise NotImplementedError(
            f"Only VAR(1) or VAR(2) for common factors are supported (maximum supported order is VAR(2)). "
            f"Got factor_order={factor_order}. Please use factor_order=1 (VAR(1)) or factor_order=2 (VAR(2))"
        )
    
    # Estimate idiosyncratic AR(1) dynamics
    A_eps, _, _ = estimate_idio_params(eps_t, bool_no_miss, min_obs=5)
    
    # Construct companion form state vector and transition matrix
    if factor_order == 2:
        # x_t = [f_t, f_{t-1}, eps_t]
        x_t = np.vstack([
            f_t[1:, :].T,  # m x (T-1)
            f_t[:-1, :].T,  # m x (T-1)
            eps_t[1:, :].T  # N x (T-1)
        ])  # (2m + N) x (T-1)
        
        # Transition matrix in companion form
        A = np.vstack([
            np.hstack([A1, A2, np.zeros((m, N))]),  # f_t = A1 @ f_{t-1} + A2 @ f_{t-2}
            np.hstack([np.eye(m), np.zeros((m, m)), np.zeros((m, N))]),  # f_{t-1} = f_{t-1}
            np.hstack([np.zeros((N, m)), np.zeros((N, m)), A_eps])  # eps_t = A_eps @ eps_{t-1}
        ])
    else:  # factor_order == 1
        # x_t = [f_t, eps_t]
        x_t = np.vstack([
            f_t.T,  # m x T
            eps_t.T  # N x T
        ])  # (m + N) x T
        
        # Transition matrix
        A = np.vstack([
            np.hstack([A1, np.zeros((m, N))]),  # f_t = A1 @ f_{t-1}
            np.hstack([np.zeros((N, m)), A_eps])  # eps_t = A_eps @ eps_{t-1}
        ])
    
    # Estimate innovation covariance (diagonal)
    # w_t = x_t[:, 1:] - A @ x_t[:, :-1]
    w_t = x_t[:, 1:] - A @ x_t[:, :-1]
    W_cov = compute_cov_safe(w_t, rowvar=False, pairwise_complete=False)
    W = np.diag(np.diag(W_cov))
    # Ensure positive diagonal
    W = np.maximum(W, np.eye(W.shape[0]) * MIN_DIAGONAL_VARIANCE)
    
    # Unconditional moments of initial state
    mu_0 = np.mean(x_t, axis=1)
    Σ_0 = compute_cov_safe(x_t, rowvar=False, pairwise_complete=False)
    
    # Enforce zero correlation between factors and idiosyncratic components
    if factor_order == 2:
        factor_dim = 2 * m
    else:
        factor_dim = m
    
    Σ_0[:factor_dim, factor_dim:] = 0
    Σ_0[factor_dim:, :factor_dim] = 0
    # Ensure diagonal covariance for idiosyncratic components
    Σ_0[factor_dim:, factor_dim:] = np.diag(np.diag(Σ_0[factor_dim:, factor_dim:]))
    
    # Ensure positive semidefinite
    from .stability import ensure_positive_definite
    eigenvals = np.linalg.eigvals(Σ_0)
    if np.any(eigenvals < 0):
        Σ_0 = Σ_0 + np.eye(Σ_0.shape[0]) * (MIN_DIAGONAL_VARIANCE - np.min(eigenvals))
    
    return A, W, mu_0, Σ_0, x_t


# ============================================================================
# Unified Estimation Functions (work with raw data or smoothed expectations)
# ============================================================================

def estimate_var_unified(
    y: np.ndarray,
    x: np.ndarray,
    V_smooth: Optional[np.ndarray] = None,
    VVsmooth: Optional[np.ndarray] = None,
    regularization: float = DEFAULT_REGULARIZATION,
    min_variance: float = MIN_EIGENVALUE,
    dtype: type = np.float32
) -> Tuple[np.ndarray, np.ndarray]:
    """Unified VAR estimation that works with raw data or smoothed expectations.
    
    Parameters
    ----------
    y : np.ndarray
        Current state (T x m) or (T-1 x m) for raw data, or smoothed expectations E[z_t]
    x : np.ndarray
        Lagged state (T-1 x p) for raw data, or smoothed expectations E[z_{t-1}]
    V_smooth : np.ndarray, optional
        Smoothed state covariances (T x m x m) or (T-1 x m x m). Required for smoothed expectations.
    VVsmooth : np.ndarray, optional
        Lag-1 cross-covariances (T x m x m). Required for smoothed expectations.
    regularization : float, default DEFAULT_REGULARIZATION
        Regularization parameter for OLS
    min_variance : float, default MIN_EIGENVALUE
        Minimum variance floor
    dtype : type, default np.float32
        Data type
        
    Returns
    -------
    A : np.ndarray
        Transition matrix (m x p)
    Q : np.ndarray
        Process noise covariance (m x m)
    """
    if V_smooth is not None:
        # Smoothed expectations mode
        # E[z_t z_t'] = EZ @ EZ' + V_smooth
        # E[z_{t-1} z_{t-1}'] = EZ_lag @ EZ_lag' + V_smooth_lag
        # E[z_t z_{t-1}'] = EZ @ EZ_lag' + VVsmooth
        
        T = y.shape[0]
        m = y.shape[1]
        p = x.shape[1]
        
        # Compute expectations
        EZZ = y.T @ y
        if V_smooth.ndim == 3:
            EZZ = EZZ + np.sum(V_smooth, axis=0)
        elif V_smooth.ndim == 2:
            EZZ = EZZ + V_smooth
        
        EZZ_BB = x.T @ x
        if V_smooth.ndim == 3:
            V_smooth_lag = V_smooth[:-1] if V_smooth.shape[0] == T + 1 else V_smooth
            EZZ_BB = EZZ_BB + np.sum(V_smooth_lag, axis=0)
        elif V_smooth.ndim == 2:
            EZZ_BB = EZZ_BB + V_smooth
        
        EZZ_FB = y[1:].T @ x if y.shape[0] > x.shape[0] else y.T @ x
        if VVsmooth is not None:
            if VVsmooth.ndim == 3:
                VVsmooth_sum = np.sum(VVsmooth[1:], axis=0) if VVsmooth.shape[0] == T + 1 else np.sum(VVsmooth, axis=0)
                EZZ_FB = EZZ_FB + VVsmooth_sum
            elif VVsmooth.ndim == 2:
                EZZ_FB = EZZ_FB + VVsmooth
        
        # Regularize
        EZZ_BB_reg = EZZ_BB + np.eye(p, dtype=dtype) * regularization
        
        def _compute_A_Q():
            # OLS: A = (EZZ_BB)^(-1) @ EZZ_FB'
            # Note: EZZ_BB_reg is already regularized, so use use_XTX=False
            A = solve_regularized_ols(EZZ_BB_reg, EZZ_FB.T, regularization=DEFAULT_ZERO_VALUE, use_XTX=False, dtype=dtype).T  # (m x p)
            
            # Q = (EZZ - A @ EZZ_FB') / T
            Q = (EZZ - A @ EZZ_FB.T) / T
            Q = ensure_covariance_stable(Q, min_eigenval=min_variance)
            return A, Q
        
        def _fallback_A_Q():
            # Fallback: use identity
            A = create_scaled_identity(m, DEFAULT_TRANSITION_COEF, dtype)
            if p > m:
                # Pad A to match p columns
                A = np.hstack([A, np.zeros((m, p - m), dtype=dtype)])
            Q = create_scaled_identity(m, DEFAULT_PROCESS_NOISE, dtype)
            return A, Q
        
        A, Q = handle_linear_algebra_error(
            _compute_A_Q, "VAR estimation",
            fallback_func=_fallback_A_Q
        )
    else:
        # Raw data mode
        T = y.shape[0]
        m = y.shape[1]
        p = x.shape[1]
        
        if T < 2:
            A = np.eye(m, p, dtype=dtype) * DEFAULT_TRANSITION_COEF
            Q = np.eye(m, dtype=dtype) * DEFAULT_PROCESS_NOISE
            return A, Q
        
        # OLS: A = (X'X + reg*I)^(-1) X'Y
        A = solve_regularized_ols(x, y, regularization=regularization, dtype=dtype).T  # (m x p)
        
        # Estimate Q from residuals
        residuals = y - x @ A.T
        if m == 1:
            var_val = compute_var_safe(residuals.flatten(), ddof=0, min_variance=min_variance)
            Q = np.atleast_2d(var_val)
        else:
            Q = compute_cov_safe(residuals.T, rowvar=True, pairwise_complete=False, min_eigenval=min_variance)
        
        Q = stabilize_innovation_covariance(Q, min_eigenval=min_variance, min_floor=MIN_Q_FLOOR, dtype=dtype)
    
    return A.astype(dtype), Q.astype(dtype)


def estimate_ar1_unified(
    y: np.ndarray,
    x: Optional[np.ndarray] = None,
    V_smooth: Optional[np.ndarray] = None,
    regularization: float = DEFAULT_REGULARIZATION,
    min_variance: float = MIN_EIGENVALUE,
    default_ar_coef: float = DEFAULT_TRANSITION_COEF,
    default_noise: float = DEFAULT_PROCESS_NOISE,
    dtype: type = np.float32
) -> Tuple[np.ndarray, np.ndarray]:
    """Unified AR(1) estimation that works with raw data or smoothed expectations.
    
    Parameters
    ----------
    y : np.ndarray
        Current state (T x n) or (T-1 x n) for raw data, or smoothed expectations E[z_t]
    x : np.ndarray, optional
        Lagged state (T-1 x n) for raw data, or smoothed expectations E[z_{t-1}].
        If None, uses y[:-1] for raw data mode.
    V_smooth : np.ndarray, optional
        Smoothed state covariances. Required for smoothed expectations mode.
    regularization : float, default DEFAULT_REGULARIZATION
        Regularization parameter
    min_variance : float, default MIN_EIGENVALUE
        Minimum variance floor
    default_ar_coef : float, default DEFAULT_TRANSITION_COEF
        Default AR coefficient if estimation fails
    default_noise : float, default DEFAULT_PROCESS_NOISE
        Default noise variance if estimation fails
    dtype : type, default np.float32
        Data type
        
    Returns
    -------
    A_diag : np.ndarray
        AR(1) coefficients (n,) - diagonal
    Q_diag : np.ndarray
        Innovation variances (n,) - diagonal
    """
    if V_smooth is not None:
        # Smoothed expectations mode
        T = y.shape[0]
        n = y.shape[1]
        
        if x is None:
            x = y[:-1]
            y = y[1:]
            T = T - 1
        
        # Compute diagonal expectations
        EZZ = np.diag(y.T @ y)
        if V_smooth.ndim == 3:
            EZZ = EZZ + np.diag(np.sum(V_smooth[1:], axis=0))
        elif V_smooth.ndim == 2:
            EZZ = EZZ + np.diag(V_smooth)
        
        EZZ_BB = np.diag(x.T @ x)
        if V_smooth.ndim == 3:
            V_smooth_lag = V_smooth[:-1] if V_smooth.shape[0] == T + 1 else V_smooth
            EZZ_BB = EZZ_BB + np.diag(np.sum(V_smooth_lag, axis=0))
        elif V_smooth.ndim == 2:
            EZZ_BB = EZZ_BB + np.diag(V_smooth)
        
        EZZ_FB = np.diag(y.T @ x)
        # Note: VVsmooth handling would go here if needed
        
        # Regularize
        EZZ_BB_reg = EZZ_BB + regularization
        
        # AR(1) coefficients: A = EZZ_FB / EZZ_BB
        A_diag = EZZ_FB / np.maximum(EZZ_BB_reg, min_variance)
        A_diag = np.where(np.isfinite(A_diag), A_diag, default_ar_coef)
        
        # Q = (EZZ - A * EZZ_FB) / T
        Q_diag = (EZZ - A_diag * EZZ_FB) / T
        Q_diag = np.maximum(Q_diag, min_variance)
        Q_diag = np.where(np.isfinite(Q_diag), Q_diag, default_noise)
    else:
        # Raw data mode
        if x is None:
            x = y[:-1]
            y = y[1:]
        
        T, n = y.shape
        
        if T < 2:
            A_diag = np.full(n, default_ar_coef, dtype=dtype)
            Q_diag = np.full(n, default_noise, dtype=dtype)
            return A_diag, Q_diag
        
        A_diag = np.zeros(n, dtype=dtype)
        Q_diag = np.zeros(n, dtype=dtype)
        
        for i in range(n):
            y_i = y[:, i]
            x_i = x[:, i].reshape(-1, 1)
            
            # Skip if insufficient data
            valid = np.isfinite(y_i) & np.isfinite(x_i.squeeze())
            if np.sum(valid) < 2:
                A_diag[i] = default_ar_coef
                Q_diag[i] = default_noise
                continue
            
            y_i_clean = y_i[valid]
            x_i_clean = x_i[valid]
            
            try:
                # OLS: A = (x'x + reg)^(-1) x'y
                XTX = x_i_clean.T @ x_i_clean
                XTX_reg = XTX + np.eye(1, dtype=dtype) * regularization
                A_i = np.linalg.solve(XTX_reg, x_i_clean.T @ y_i_clean).item()
                
                # Estimate Q from residuals
                residuals = y_i_clean - x_i_clean.squeeze() * A_i
                Q_i = compute_var_safe(residuals, ddof=0, min_variance=min_variance, default_variance=default_noise) if len(residuals) > 1 else default_noise
                
                A_diag[i] = A_i if np.isfinite(A_i) else default_ar_coef
                Q_diag[i] = max(Q_i, min_variance) if np.isfinite(Q_i) else default_noise
            except (np.linalg.LinAlgError, ValueError):
                A_diag[i] = default_ar_coef
                Q_diag[i] = default_noise
    
    return A_diag.astype(dtype), Q_diag.astype(dtype)


def estimate_constrained_ols_unified(
    y: np.ndarray,
    X: np.ndarray,
    R: np.ndarray,
    q: np.ndarray,
    V_smooth: Optional[np.ndarray] = None,
    regularization: float = DEFAULT_REGULARIZATION,
    dtype: type = np.float32
) -> np.ndarray:
    """Unified constrained OLS estimation that works with raw data or smoothed expectations.
    
    Solves: min ||y - X*beta||^2 subject to R @ beta = q
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x n) for raw data, or E[y_t * f_t'] for smoothed expectations
    X : np.ndarray
        Independent variables (T x p) for raw data, or E[f_t * f_t'] for smoothed expectations
    R : np.ndarray
        Constraint matrix (n_constraints x p)
    q : np.ndarray
        Constraint vector (n_constraints,)
    V_smooth : np.ndarray, optional
        Smoothed state covariances. Required for smoothed expectations mode.
    regularization : float, default DEFAULT_REGULARIZATION
        Regularization parameter
    dtype : type, default np.float32
        Data type
        
    Returns
    -------
    beta : np.ndarray
        Constrained OLS coefficients (p,)
    """
    if V_smooth is not None:
        # Smoothed expectations mode
        # y is E[y_t * f_t'], X is E[f_t * f_t']
        # Need to handle V_smooth if it affects the computation
        
        # Unconstrained OLS: beta = X^(-1) @ y
        # X is already a covariance matrix, so use use_XTX=False
        beta_unconstrained = solve_regularized_ols(X, y, regularization=regularization, use_XTX=False, dtype=dtype)
        
        # Apply constraints: beta_constrained = beta_unconstrained - X^(-1) @ R' @ (R @ X^(-1) @ R')^(-1) @ (R @ beta_unconstrained - q)
        try:
            X_reg = X + np.eye(X.shape[0], dtype=dtype) * regularization
            X_inv = np.linalg.inv(X_reg)
            R_X_inv_RT = R @ X_inv @ R.T
            R_X_inv_RT_reg = R_X_inv_RT + np.eye(R_X_inv_RT.shape[0], dtype=dtype) * regularization
            constraint_term = R @ beta_unconstrained - q
            beta_constrained = beta_unconstrained - X_inv @ R.T @ np.linalg.solve(R_X_inv_RT_reg, constraint_term)
        except (np.linalg.LinAlgError, ValueError):
            beta_constrained = beta_unconstrained
    else:
        # Raw data mode
        # Unconstrained OLS: beta = (X'X)^(-1) X'y
        beta_unconstrained = solve_regularized_ols(X, y, regularization=regularization, dtype=dtype)
        
        # Apply constraints
        try:
            XTX = X.T @ X
            XTX_reg = XTX + np.eye(XTX.shape[0], dtype=dtype) * regularization
            XTX_inv = np.linalg.inv(XTX_reg)
            R_XTX_inv_RT = R @ XTX_inv @ R.T
            R_XTX_inv_RT_reg = R_XTX_inv_RT + np.eye(R_XTX_inv_RT.shape[0], dtype=dtype) * regularization
            constraint_term = R @ beta_unconstrained - q
            beta_constrained = beta_unconstrained - XTX_inv @ R.T @ np.linalg.solve(R_XTX_inv_RT_reg, constraint_term)
        except (np.linalg.LinAlgError, ValueError):
            beta_constrained = beta_unconstrained
    
    return beta_constrained.astype(dtype)


def estimate_variance_unified(
    residuals: Optional[np.ndarray] = None,
    X: Optional[np.ndarray] = None,
    EZ: Optional[np.ndarray] = None,
    C: Optional[np.ndarray] = None,
    V_smooth: Optional[np.ndarray] = None,
    min_variance: float = MIN_EIGENVALUE,
    default_variance: float = DEFAULT_PROCESS_NOISE,
    dtype: type = np.float32
) -> np.ndarray:
    """Unified variance estimation that works with raw residuals or smoothed expectations.
    
    Parameters
    ----------
    residuals : np.ndarray, optional
        Raw residuals (T x N). Required for raw data mode.
    X : np.ndarray, optional
        Data array (T x N). Required for smoothed expectations mode.
    EZ : np.ndarray, optional
        Smoothed state means (T+1 x m). Required for smoothed expectations mode.
    C : np.ndarray, optional
        Observation matrix (N x m). Required for smoothed expectations mode.
    V_smooth : np.ndarray, optional
        Smoothed state covariances (T+1 x m x m). Required for smoothed expectations mode.
    min_variance : float, default MIN_EIGENVALUE
        Minimum variance floor
    default_variance : float, default DEFAULT_PROCESS_NOISE
        Default variance if estimation fails
    dtype : type, default np.float32
        Data type
        
    Returns
    -------
    R : np.ndarray
        Variance/covariance matrix (N x N), diagonal
    """
    if residuals is not None:
        # Raw data mode
        T, N = residuals.shape
        
        if T <= 1:
            R = np.eye(N, dtype=dtype) * default_variance
            return R
        
        # Compute variance for each series
        var_res = np.array([
            compute_var_safe(
                residuals[:, i][np.isfinite(residuals[:, i])],
                ddof=0,
                min_variance=min_variance,
                default_variance=default_variance
            )
            if np.sum(np.isfinite(residuals[:, i])) > 1 else default_variance
            for i in range(N)
        ], dtype=dtype)
        var_res = np.where(np.isfinite(var_res), var_res, default_variance)
        var_res = np.maximum(var_res, min_variance)
        
        R = np.diag(var_res)
    else:
        # Smoothed expectations mode
        if X is None or EZ is None or C is None:
            raise ValueError("X, EZ, and C are required for smoothed expectations mode")
        
        T, N = X.shape
        m = EZ.shape[1]
        
        # Compute residuals from smoothed expectations
        # R = E[(y_t - C @ z_t) (y_t - C @ z_t)'] = E[y_t y_t'] - C @ E[z_t y_t'] - E[y_t z_t'] @ C' + C @ E[z_t z_t'] @ C'
        # For diagonal R, we only need diagonal elements
        
        R = np.zeros((N, N), dtype=dtype)
        
        for t in range(T):
            # Residual: y_t - C @ z_{t+1}
            z_t = EZ[t+1, :]  # (m,)
            residual = X[t, :] - C @ z_t  # (N,)
            
            # Add contribution: residual @ residual' + C @ V_{t+1} @ C'
            R += np.outer(residual, residual)
            if V_smooth is not None:
                V_t = V_smooth[t+1]  # (m x m)
                R += C @ V_t @ C.T
        
        R = R / T
        
        # Extract diagonal and apply floors
        R_diag = np.diag(R)
        R_diag = np.maximum(R_diag, min_variance)
        R_diag = np.where(np.isfinite(R_diag), R_diag, default_variance)
        R = np.diag(R_diag)
    
    return R.astype(dtype)


def compute_initial_covariance_from_transition(
    A: np.ndarray,
    Q: np.ndarray,
    regularization: float = DEFAULT_REGULARIZATION,
    dtype: type = np.float32
) -> np.ndarray:
    """Compute initial covariance V_0 from transition matrix A and process noise Q.
    
    Solves the Lyapunov equation: (I - A ⊗ A) vec(V_0) = vec(Q)
    This is used to compute the steady-state covariance for the initial state.
    
    Parameters
    ----------
    A : np.ndarray
        Transition matrix (n x n)
    Q : np.ndarray
        Process noise covariance (n x n)
    regularization : float, default DEFAULT_REGULARIZATION
        Regularization parameter for numerical stability
    dtype : type, default np.float32
        Data type
        
    Returns
    -------
    V_0 : np.ndarray
        Initial covariance matrix (n x n)
    """
    n = A.shape[0]
    try:
        kron_AA = np.kron(A, A)
        eye_kron = np.eye(n ** 2, dtype=dtype)
        V_0_flat = np.linalg.solve(
            eye_kron - kron_AA + eye_kron * regularization,
            Q.flatten()
        )
        V_0 = V_0_flat.reshape(n, n).astype(dtype)
        return V_0
    except (np.linalg.LinAlgError, ValueError):
        # Fallback: use Q as initial covariance
        _logger.warning(
            f"Initial covariance computation failed for transition matrix of size {n}x{n}. "
            f"Using process noise Q as fallback."
        )
        return Q.copy().astype(dtype)


__all__ = [
    # AR clipping
    'clip_ar',
    'apply_ar_clipping',
    # Estimation functions
    'estimate_ar',
    'estimate_var',
    'estimate_idio_dynamics',
    'estimate_idio_params',
    'estimate_state_space_params',
    # Unified estimation functions
    'estimate_var_unified',
    'estimate_ar1_unified',
    'estimate_constrained_ols_unified',
    'estimate_variance_unified',
    'compute_initial_covariance_from_transition',
    'stabilize_innovation_covariance',
]

