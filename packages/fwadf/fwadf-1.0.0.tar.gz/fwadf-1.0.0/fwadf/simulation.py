"""
Monte Carlo Simulation Module for Critical Value Generation

Implements Monte Carlo simulation procedures for generating critical values
of the WADF, FWADF, and Fourier t-statistics following Sephton (2024).

The simulations use the data generating process (DGP):
    y_t = y_{t-1} + epsilon_t, epsilon_t ~ N(0, 1)

which represents a unit root process (random walk).

References:
    Sephton, P.S. (2024). "Finite Sample Lag Adjusted Critical Values and 
    Probability Values for the Fourier Wavelet Unit Root Test." 
    Computational Economics, 64, 693-705.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import warnings

from .wavelet import haar_scaling_coefficients
from .utils import diff, ols_estimate


@dataclass
class SimulationResult:
    """Results from Monte Carlo simulation."""
    sample_size: int
    replications: int
    lag: int
    model: int
    k: Optional[float]
    quantiles: Dict[float, float]
    mean: float
    std: float


def generate_unit_root_series(T: int, burn: int = 100) -> np.ndarray:
    """
    Generate a unit root process for Monte Carlo simulation.
    
    DGP: y_t = y_{t-1} + epsilon_t, epsilon_t ~ N(0, 1)
    
    Parameters
    ----------
    T : int
        Sample size.
    burn : int
        Burn-in period.
    
    Returns
    -------
    np.ndarray
        Unit root series of length T.
    """
    total = T + burn
    epsilon = np.random.standard_normal(total)
    y = np.cumsum(epsilon)
    return y[burn:]


def _compute_wadf_statistic(V: np.ndarray, lag: int, model: int) -> float:
    """Compute WADF test statistic for simulation."""
    T = len(V)
    
    # First difference
    dV = np.diff(V)
    
    # Lagged level
    V_lag1 = V[:-1]
    
    # Trim for lag
    start_idx = lag + 1
    
    if start_idx >= len(dV):
        return np.nan
    
    dep = dV[start_idx:]
    V_lag1_trim = V_lag1[start_idx:]
    
    # Build regressor matrix
    n = len(dep)
    if model == 0:
        X = V_lag1_trim.reshape(-1, 1)
    elif model == 1:
        X = np.column_stack([V_lag1_trim, np.ones(n)])
    else:  # model == 2
        X = np.column_stack([V_lag1_trim, np.ones(n), np.arange(1, n + 1)])
    
    # Add lagged differences
    if lag > 0:
        for j in range(1, lag + 1):
            if start_idx - j >= 0 and len(dV) > start_idx:
                lag_diff = dV[start_idx - j:len(dV) - j]
                if len(lag_diff) == n:
                    X = np.column_stack([X, lag_diff])
    
    # Check dimensions
    if X.shape[0] < X.shape[1] + 1:
        return np.nan
    
    try:
        # OLS
        inv_xx = np.linalg.inv(X.T @ X)
        beta = inv_xx @ X.T @ dep
        residuals = dep - X @ beta
        s2 = (residuals.T @ residuals) / (len(dep) - X.shape[1])
        se = np.sqrt(s2 * inv_xx[0, 0])
        t_stat = beta[0] / se
        return float(t_stat)
    except:
        return np.nan


def _compute_fwadf_statistic(V: np.ndarray, lag: int, k: float, 
                            model: int) -> Tuple[float, float]:
    """
    Compute FWADF test statistic and Fourier t-statistic for simulation.
    
    Returns (fwadf_stat, fourier_t_stat).
    """
    T = len(V)
    
    # First difference
    dV = np.diff(V)
    
    # Lagged level
    V_lag1 = V[:-1]
    
    # Fourier term (aligned with V)
    fourier = np.sin(2 * np.pi * k * np.arange(1, T + 1) / T)
    fourier_trimmed = fourier[1:]  # Align with dV
    
    # Trim for lag
    start_idx = lag + 1
    
    if start_idx >= len(dV):
        return np.nan, np.nan
    
    dep = dV[start_idx:]
    V_lag1_trim = V_lag1[start_idx:]
    fourier_trim = fourier_trimmed[start_idx:]
    
    n = len(dep)
    
    # Build regressor matrix: V_{t-1}, Fourier, constant, [trend]
    if model == 0:
        X = np.column_stack([V_lag1_trim, fourier_trim])
    elif model == 1:
        X = np.column_stack([V_lag1_trim, fourier_trim, np.ones(n)])
    else:  # model == 2
        X = np.column_stack([V_lag1_trim, fourier_trim, np.ones(n), np.arange(1, n + 1)])
    
    # Add lagged differences
    if lag > 0:
        for j in range(1, lag + 1):
            if start_idx - j >= 0 and len(dV) > start_idx:
                lag_diff = dV[start_idx - j:len(dV) - j]
                if len(lag_diff) == n:
                    X = np.column_stack([X, lag_diff])
    
    # Check dimensions
    if X.shape[0] < X.shape[1] + 1:
        return np.nan, np.nan
    
    try:
        # OLS
        inv_xx = np.linalg.inv(X.T @ X)
        beta = inv_xx @ X.T @ dep
        residuals = dep - X @ beta
        s2 = (residuals.T @ residuals) / (len(dep) - X.shape[1])
        
        # t-stat on V_{t-1} (FWADF statistic)
        se_delta = np.sqrt(s2 * inv_xx[0, 0])
        fwadf_stat = beta[0] / se_delta
        
        # t-stat on Fourier term
        se_beta = np.sqrt(s2 * inv_xx[1, 1])
        fourier_t_stat = beta[1] / se_beta
        
        return float(fwadf_stat), float(fourier_t_stat)
    except:
        return np.nan, np.nan


def simulate_wadf_critical_values(
    T: int,
    lag: int = 0,
    model: int = 1,
    replications: int = 10000,
    quantiles: List[float] = None,
    seed: Optional[int] = None,
    verbose: bool = False
) -> Dict[float, float]:
    """
    Simulate critical values for the WADF test.
    
    Parameters
    ----------
    T : int
        Original sample size (before wavelet transformation).
    lag : int
        Fixed lag length in the testing equation.
    model : int
        Model specification (0, 1, or 2).
    replications : int
        Number of Monte Carlo replications.
    quantiles : list
        Quantiles to compute (default: [0.01, 0.025, 0.05, 0.10]).
    seed : int, optional
        Random seed for reproducibility.
    verbose : bool
        Print progress information.
    
    Returns
    -------
    dict
        Dictionary mapping quantiles to critical values.
    
    Notes
    -----
    The wavelet transformation reduces sample size by half, so the
    effective sample size for the test is T/2.
    """
    if quantiles is None:
        quantiles = [0.01, 0.025, 0.05, 0.10]
    
    if seed is not None:
        np.random.seed(seed)
    
    test_stats = []
    
    for i in range(replications):
        # Generate unit root process
        y = generate_unit_root_series(T, burn=100)
        
        # Apply wavelet transform
        V = haar_scaling_coefficients(y)
        
        # Compute test statistic
        stat = _compute_wadf_statistic(V, lag, model)
        
        if not np.isnan(stat):
            test_stats.append(stat)
        
        if verbose and (i + 1) % 1000 == 0:
            print(f"Completed {i + 1}/{replications} replications")
    
    test_stats = np.array(test_stats)
    
    if len(test_stats) < replications * 0.9:
        warnings.warn(f"Only {len(test_stats)}/{replications} valid statistics computed.")
    
    # Compute quantiles
    cv = {}
    for q in quantiles:
        cv[q] = float(np.quantile(test_stats, q))
    
    return cv


def simulate_fwadf_critical_values(
    T: int,
    lag: int = 0,
    k: float = 1.0,
    model: int = 1,
    replications: int = 10000,
    quantiles: List[float] = None,
    seed: Optional[int] = None,
    verbose: bool = False
) -> Dict[float, float]:
    """
    Simulate critical values for the FWADF test.
    
    Parameters
    ----------
    T : int
        Original sample size.
    lag : int
        Fixed lag length.
    k : float
        Fourier frequency.
    model : int
        Model specification (0, 1, or 2).
    replications : int
        Number of Monte Carlo replications.
    quantiles : list
        Quantiles to compute.
    seed : int, optional
        Random seed.
    verbose : bool
        Print progress.
    
    Returns
    -------
    dict
        Dictionary mapping quantiles to critical values.
    """
    if quantiles is None:
        quantiles = [0.01, 0.025, 0.05, 0.10]
    
    if seed is not None:
        np.random.seed(seed)
    
    test_stats = []
    
    for i in range(replications):
        # Generate unit root process
        y = generate_unit_root_series(T, burn=100)
        
        # Apply wavelet transform
        V = haar_scaling_coefficients(y)
        
        # Compute test statistic
        fwadf_stat, _ = _compute_fwadf_statistic(V, lag, k, model)
        
        if not np.isnan(fwadf_stat):
            test_stats.append(fwadf_stat)
        
        if verbose and (i + 1) % 1000 == 0:
            print(f"Completed {i + 1}/{replications} replications")
    
    test_stats = np.array(test_stats)
    
    # Compute quantiles
    cv = {}
    for q in quantiles:
        cv[q] = float(np.quantile(test_stats, q))
    
    return cv


def simulate_fourier_t_critical_values(
    T: int,
    lag: int = 0,
    k: float = 1.0,
    model: int = 1,
    replications: int = 10000,
    quantiles: List[float] = None,
    seed: Optional[int] = None,
    verbose: bool = False
) -> Dict[str, Dict[float, float]]:
    """
    Simulate critical values for the Fourier term t-statistic.
    
    The t-statistic on the Fourier term is used to test whether
    the Fourier term is significant. If not significant, WADF
    should be used instead of FWADF.
    
    Parameters
    ----------
    T : int
        Original sample size.
    lag : int
        Fixed lag length.
    k : float
        Fourier frequency.
    model : int
        Model specification.
    replications : int
        Number of Monte Carlo replications.
    quantiles : list
        Quantiles to compute (for both tails).
    seed : int, optional
        Random seed.
    verbose : bool
        Print progress.
    
    Returns
    -------
    dict
        Dictionary with 'lower' and 'upper' tail critical values.
    """
    if quantiles is None:
        # For two-tailed test
        quantiles = [0.005, 0.01, 0.025, 0.05, 0.10]
    
    if seed is not None:
        np.random.seed(seed)
    
    fourier_t_stats = []
    
    for i in range(replications):
        # Generate unit root process
        y = generate_unit_root_series(T, burn=100)
        
        # Apply wavelet transform
        V = haar_scaling_coefficients(y)
        
        # Compute Fourier t-statistic
        _, fourier_t = _compute_fwadf_statistic(V, lag, k, model)
        
        if not np.isnan(fourier_t):
            fourier_t_stats.append(fourier_t)
        
        if verbose and (i + 1) % 1000 == 0:
            print(f"Completed {i + 1}/{replications} replications")
    
    fourier_t_stats = np.array(fourier_t_stats)
    
    # Compute quantiles for both tails
    lower_cv = {}
    upper_cv = {}
    
    for q in quantiles:
        lower_cv[q] = float(np.quantile(fourier_t_stats, q))
        upper_cv[q] = float(np.quantile(fourier_t_stats, 1 - q))
    
    return {'lower': lower_cv, 'upper': upper_cv}


def generate_response_surface_data(
    sample_sizes: List[int],
    lags: List[int],
    k_values: List[float],
    model: int = 1,
    replications: int = 10000,
    quantiles: List[float] = None,
    seed: Optional[int] = None,
    test_type: str = 'fwadf'
) -> Dict:
    """
    Generate data for response surface estimation following Sephton (2024).
    
    This function simulates critical values across different sample sizes,
    lag lengths, and Fourier frequencies to create data for response
    surface regression.
    
    Parameters
    ----------
    sample_sizes : list
        List of sample sizes to simulate.
    lags : list
        List of lag lengths.
    k_values : list
        List of Fourier frequencies.
    model : int
        Model specification.
    replications : int
        Number of replications per combination.
    quantiles : list
        Quantiles to compute.
    seed : int, optional
        Random seed.
    test_type : str
        'fwadf' or 'wadf'.
    
    Returns
    -------
    dict
        Dictionary containing simulation results for response surface estimation.
    """
    if quantiles is None:
        quantiles = [0.01, 0.025, 0.05, 0.10]
    
    if seed is not None:
        np.random.seed(seed)
    
    results = {
        'sample_sizes': [],
        'lags': [],
        'k_values': [],
        'model': model,
        'quantiles': {},
    }
    
    for q in quantiles:
        results['quantiles'][q] = []
    
    total_combos = len(sample_sizes) * len(lags) * (len(k_values) if test_type == 'fwadf' else 1)
    combo_count = 0
    
    for T in sample_sizes:
        for lag in lags:
            if test_type == 'fwadf':
                for k in k_values:
                    combo_count += 1
                    print(f"Simulating combination {combo_count}/{total_combos}: "
                          f"T={T}, lag={lag}, k={k}")
                    
                    cv = simulate_fwadf_critical_values(
                        T=T, lag=lag, k=k, model=model,
                        replications=replications, quantiles=quantiles
                    )
                    
                    results['sample_sizes'].append(T)
                    results['lags'].append(lag)
                    results['k_values'].append(k)
                    
                    for q in quantiles:
                        results['quantiles'][q].append(cv[q])
            else:
                combo_count += 1
                print(f"Simulating combination {combo_count}/{total_combos}: "
                      f"T={T}, lag={lag}")
                
                cv = simulate_wadf_critical_values(
                    T=T, lag=lag, model=model,
                    replications=replications, quantiles=quantiles
                )
                
                results['sample_sizes'].append(T)
                results['lags'].append(lag)
                results['k_values'].append(None)
                
                for q in quantiles:
                    results['quantiles'][q].append(cv[q])
    
    return results


def compute_response_surface_coefficients(
    simulation_data: Dict,
    quantile: float,
    include_k: bool = True
) -> Dict[str, float]:
    """
    Estimate response surface coefficients from simulation data.
    
    Response surface equation following Sephton (2024):
        CV_p = β_∞ + Σ β_i * (1/T)^i + Σ γ_j * (L/T)^j
    
    Parameters
    ----------
    simulation_data : dict
        Output from generate_response_surface_data().
    quantile : float
        Quantile for which to estimate coefficients.
    include_k : bool
        Whether to include Fourier frequency in response surface.
    
    Returns
    -------
    dict
        Response surface coefficients.
    """
    T = np.array(simulation_data['sample_sizes'])
    L = np.array(simulation_data['lags'])
    cv = np.array(simulation_data['quantiles'][quantile])
    
    # Build regressor matrix following Sephton (2024)
    # Powers of 1/T: 1, 2, 3
    # Powers of L/T: 0.5, 1, 1.5, 2, 2.5
    
    n = len(T)
    
    # Constant term
    X = np.ones((n, 1))
    
    # 1/T terms
    for i in range(1, 4):
        X = np.column_stack([X, (1/T)**i])
    
    # L/T terms
    for j in [0.5, 1, 1.5, 2, 2.5]:
        X = np.column_stack([X, (L/T)**j])
    
    # OLS estimation
    try:
        beta = np.linalg.lstsq(X, cv, rcond=None)[0]
    except:
        beta = np.linalg.pinv(X) @ cv
    
    coefficients = {
        'beta_inf': beta[0],
        'beta_1': beta[1],
        'beta_2': beta[2],
        'beta_3': beta[3],
        'gamma_0.5': beta[4],
        'gamma_1': beta[5],
        'gamma_1.5': beta[6],
        'gamma_2': beta[7],
        'gamma_2.5': beta[8]
    }
    
    return coefficients


def quick_simulate_critical_values(
    T: int,
    model: int = 1,
    test_type: str = 'fwadf',
    k: float = 1.0,
    replications: int = 5000,
    seed: Optional[int] = None
) -> Dict:
    """
    Quick simulation of critical values for a single configuration.
    
    This is useful for getting approximate critical values when
    the response surface approximation is not available.
    
    Parameters
    ----------
    T : int
        Sample size.
    model : int
        Model specification.
    test_type : str
        'fwadf' or 'wadf'.
    k : float
        Fourier frequency (for FWADF).
    replications : int
        Number of replications.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    dict
        Critical values at standard significance levels.
    """
    quantiles = [0.01, 0.025, 0.05, 0.10, 0.15]
    
    if test_type.lower() == 'fwadf':
        cv = simulate_fwadf_critical_values(
            T=T, lag=0, k=k, model=model,
            replications=replications, quantiles=quantiles, seed=seed
        )
    else:
        cv = simulate_wadf_critical_values(
            T=T, lag=0, model=model,
            replications=replications, quantiles=quantiles, seed=seed
        )
    
    return cv
