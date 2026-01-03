"""
Fourier Wavelet Augmented Dickey-Fuller (FWADF) Unit Root Test

Implementation of the FWADF unit root test following Aydin & Pata (2020).

The FWADF test extends the WADF test by including a Fourier term to capture
smooth structural breaks and nonlinearities in the series.

References:
    Aydin, M. & Pata, U.K. (2020). "Are Shocks to Disaggregated Renewable Energy 
    Consumption Permanent or Temporary for the USA? Wavelet Based Unit Root Test 
    with Smooth Structural Shifts." Energy, 207, 118245.
    
    Sephton, P.S. (2024). "Finite Sample Lag Adjusted Critical Values and 
    Probability Values for the Fourier Wavelet Unit Root Test." 
    Computational Economics, 64, 693-705.
    
    Enders, W. & Lee, J. (2012). Economics Letters, 117(1), 196-199.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Literal, Union, Tuple, List

from .wavelet import haar_scaling_coefficients
from .utils import (lag, diff, create_lag_matrix, trimr, ols_estimate,
                    aic, bic, calculate_max_lag, create_fourier_term)


@dataclass
class FWADFResult:
    """
    Results from FWADF unit root test.
    
    Attributes
    ----------
    statistic : float
        FWADF test statistic (t-statistic on delta).
    pvalue : float
        Approximate p-value for unit root test.
    k : float
        Selected Fourier frequency.
    lag : int
        Selected lag length.
    model : int
        Model specification (0: none, 1: constant, 2: constant+trend).
    ic_criterion : str
        Information criterion used for lag selection.
    sample_size : int
        Original sample size.
    wavelet_sample_size : int
        Sample size after wavelet transformation.
    critical_values : dict
        Critical values at common significance levels.
    fourier_t_stat : float
        t-statistic on the Fourier term coefficient.
    fourier_t_pvalue : float
        P-value for testing significance of Fourier term.
    fourier_significant : bool
        Whether Fourier term is significant at 5% level.
    delta : float
        Estimated coefficient on lagged level.
    beta : float
        Estimated coefficient on Fourier term.
    se_delta : float
        Standard error of delta.
    se_beta : float
        Standard error of beta.
    ssr : float
        Sum of squared residuals.
    regression_results : dict
        Full OLS regression results.
    all_k_results : dict
        Results for all tested frequencies.
    """
    statistic: float
    pvalue: float
    k: float
    lag: int
    model: int
    ic_criterion: str
    sample_size: int
    wavelet_sample_size: int
    critical_values: dict
    fourier_t_stat: float
    fourier_t_pvalue: float
    fourier_significant: bool
    delta: float
    beta: float
    se_delta: float
    se_beta: float
    ssr: float
    regression_results: dict
    all_k_results: dict
    
    def __repr__(self) -> str:
        model_names = {0: "No Deterministics", 
                       1: "Constant", 
                       2: "Constant and Trend"}
        
        lines = [
            "=" * 65,
            "Fourier Wavelet Augmented Dickey-Fuller (FWADF) Test Results",
            "=" * 65,
            f"Model:                    {model_names.get(self.model, 'Unknown')}",
            f"Original Sample Size:     {self.sample_size}",
            f"Wavelet Sample Size:      {self.wavelet_sample_size}",
            f"Lag Selection:            {self.ic_criterion.upper()}",
            f"Selected Fourier Freq:    k = {self.k:.1f}",
            f"Selected Lag Length:      {self.lag}",
            "-" * 65,
            "Unit Root Test:",
            f"  FWADF Statistic:        {self.statistic:.4f}",
            f"  P-value:                {self.pvalue:.4f}",
            "-" * 65,
            "Fourier Term Significance:",
            f"  t-statistic:            {self.fourier_t_stat:.4f}",
            f"  P-value:                {self.fourier_t_pvalue:.4f}",
        ]
        
        if self.fourier_significant:
            lines.append("  Conclusion:             Significant (use FWADF test)")
        else:
            lines.append("  Conclusion:             Not significant (use WADF test instead)")
        
        lines.append("-" * 65)
        lines.append("Critical Values (FWADF):")
        
        for level, cv in sorted(self.critical_values.items()):
            lines.append(f"  {level*100:.0f}%:                     {cv:.4f}")
        
        lines.append("-" * 65)
        
        # Unit root conclusion
        if self.fourier_significant:
            if self.pvalue < 0.01:
                conclusion = "Reject H0 at 1% level (Stationary)"
            elif self.pvalue < 0.05:
                conclusion = "Reject H0 at 5% level (Stationary)"
            elif self.pvalue < 0.10:
                conclusion = "Reject H0 at 10% level (Stationary)"
            else:
                conclusion = "Cannot reject H0 (Unit Root)"
            lines.append(f"Conclusion:               {conclusion}")
        else:
            lines.append("Note: Fourier term not significant. Consider WADF test results.")
        
        lines.append("=" * 65)
        
        return "\n".join(lines)
    
    def summary(self) -> str:
        """Return formatted summary string."""
        return self.__repr__()


def fwadf_test(
    data: np.ndarray,
    model: int = 1,
    max_lag: Optional[int] = None,
    max_freq: int = 5,
    freq_grid: Optional[List[float]] = None,
    ic: Literal['aic', 'bic'] = 'bic',
    verbose: bool = True
) -> FWADFResult:
    """
    Perform the Fourier Wavelet Augmented Dickey-Fuller (FWADF) unit root test.
    
    The FWADF test extends WADF by including a Fourier term to capture smooth
    structural breaks and nonlinearities. The test searches over a grid of
    Fourier frequencies to find the optimal k that minimizes SSR.
    
    Test Equation:
        ΔV_t = δ*V_{t-1} + β*sin(2πkt/T) + Σ(ρ_j * ΔV_{t-j}) + deterministics + ε_t
    
    where V_t are the Haar scaling coefficients.
    
    Null Hypothesis: δ = 0 (series has unit root)
    Alternative Hypothesis: δ < 0 (series is stationary)
    
    The test follows Enders & Lee (2012) two-step procedure:
    1. Search for optimal k by minimizing SSR
    2. Test significance of Fourier term using t-statistic
       (if not significant, use WADF test instead)
    
    Parameters
    ----------
    data : np.ndarray
        Input time series data (1-dimensional array).
    model : int, optional
        Model specification (default: 1):
        - 0: No deterministic terms (only Fourier)
        - 1: Constant
        - 2: Constant and linear trend
    max_lag : int, optional
        Maximum lag length to consider. If None, uses int(0.75*T^(1/3))
        following Sephton (2024).
    max_freq : int, optional
        Maximum Fourier frequency to consider (default: 5).
        Grid search is performed over k = 1, 2, ..., max_freq.
    freq_grid : list, optional
        Custom frequency grid. If provided, overrides max_freq.
        Following Sephton (2024), can use values from 0.1 to 5.9 in 0.1 increments.
    ic : str, optional
        Information criterion for lag selection (default: 'bic'):
        - 'aic': Akaike Information Criterion
        - 'bic': Bayesian/Schwarz Information Criterion
    verbose : bool, optional
        If True, print results summary (default: True).
    
    Returns
    -------
    FWADFResult
        Object containing test results, including:
        - statistic: FWADF test statistic
        - pvalue: Approximate p-value
        - k: Selected Fourier frequency
        - lag: Selected lag length
        - fourier_t_stat: t-statistic on Fourier term
        - fourier_significant: Whether Fourier term is significant
        - critical_values: Critical values at 1%, 5%, 10%
    
    Examples
    --------
    >>> import numpy as np
    >>> from fwadf import fwadf_test
    >>> # Generate random walk with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> data = np.cumsum(np.random.randn(T))
    >>> data[100:] += 5  # Add level shift
    >>> result = fwadf_test(data, model=1)
    >>> print(f"Test statistic: {result.statistic:.4f}")
    >>> print(f"Selected frequency: {result.k}")
    
    Notes
    -----
    1. The FWADF test is a lower-tailed test.
    2. If the Fourier term is not significant, Aydin & Pata (2020) recommend
       using the standard WADF test instead.
    3. The test searches for k that minimizes SSR following Enders & Lee (2012).
    4. Fractional frequencies (e.g., k=1.5) can better capture smooth breaks
       following Omay (2015).
    
    References
    ----------
    Aydin, M. & Pata, U.K. (2020). Energy, 207, 118245.
    Sephton, P.S. (2024). Computational Economics, 64, 693-705.
    Enders, W. & Lee, J. (2012). Economics Letters, 117(1), 196-199.
    """
    # Validate input
    data = np.asarray(data).flatten()
    original_n = len(data)
    
    if original_n < 20:
        raise ValueError("Input data must have at least 20 observations.")
    
    if model not in [0, 1, 2]:
        raise ValueError("Model must be 0 (none), 1 (constant), or 2 (constant+trend).")
    
    # Apply Haar wavelet transformation to get scaling coefficients
    V = haar_scaling_coefficients(data)
    T = len(V)
    
    if T < 10:
        raise ValueError("Wavelet-transformed series too short. Need more observations.")
    
    # Set maximum lag if not specified
    if max_lag is None:
        max_lag = calculate_max_lag(T, method='sephton')
    
    max_lag = min(max_lag, T // 4)
    
    # Set frequency grid
    if freq_grid is None:
        # Following original GAUSS code: k = 1, 2, ..., max_freq (integer grid)
        # Or following Sephton (2024): k = 0.1, 0.2, ..., 5.9 (fractional grid)
        freq_grid = list(range(1, max_freq + 1))
    
    # Prepare data
    dV = diff(V)
    V_lag1 = V[:-1]
    
    # Build lagged differences matrix
    dV_lags = np.zeros((len(dV), max_lag))
    for j in range(1, max_lag + 1):
        dV_lags[j:, j-1] = dV[:-j]
        dV_lags[:j, j-1] = np.nan
    
    # Information criterion function
    ic_func = aic if ic.lower() == 'aic' else bic
    
    # Store results for each frequency
    all_k_results = {}
    
    for k in freq_grid:
        # Create Fourier term for the wavelet-transformed series
        T_wave = len(V)
        fourier_term = np.sin(2 * np.pi * k * np.arange(1, T_wave + 1) / T_wave)
        
        # Align Fourier term with dV (remove first observation)
        fourier_trimmed = fourier_term[1:]
        
        # Results for each lag at this frequency
        ic_values_lag = np.full(max_lag + 1, np.inf)
        test_stats_lag = np.zeros(max_lag + 1)
        fourier_t_stats_lag = np.zeros(max_lag + 1)
        ssr_values_lag = np.zeros(max_lag + 1)
        results_lag = {}
        
        for p in range(max_lag + 1):
            start_idx = p + 1
            
            if start_idx >= len(dV):
                continue
            
            dep = dV[start_idx:]
            V_lag1_trim = V_lag1[start_idx:]
            fourier_trim = fourier_trimmed[start_idx:]
            
            # Build regressor matrix following original GAUSS code order:
            # V_{t-1}, sin(2πkt/T), constant, [trend], [lagged diffs]
            if model == 0:
                X = np.column_stack([V_lag1_trim, fourier_trim])
            elif model == 1:
                ones = np.ones(len(dep))
                X = np.column_stack([V_lag1_trim, fourier_trim, ones])
            else:  # model == 2
                ones = np.ones(len(dep))
                trend = np.arange(1, len(dep) + 1)
                X = np.column_stack([V_lag1_trim, fourier_trim, ones, trend])
            
            # Add lagged differences
            if p > 0:
                ldy = dV_lags[start_idx:, :p]
                X = np.column_stack([X, ldy])
            
            # Check for valid observations
            valid_idx = ~np.any(np.isnan(X), axis=1)
            if np.sum(valid_idx) < X.shape[1] + 1:
                continue
            
            dep_valid = dep[valid_idx]
            X_valid = X[valid_idx, :]
            
            # OLS estimation
            result = ols_estimate(dep_valid, X_valid)
            
            # Store results
            # In X: col 0 = V_{t-1}, col 1 = Fourier term
            test_stats_lag[p] = result['t_stats'][0]  # t-stat on V_{t-1}
            fourier_t_stats_lag[p] = result['t_stats'][1]  # t-stat on Fourier
            ssr_values_lag[p] = result['ssr']
            ic_values_lag[p] = ic_func(result['residuals'], X_valid.shape[1])
            results_lag[p] = result
        
        # Select optimal lag for this frequency
        if np.all(np.isinf(ic_values_lag)):
            continue
            
        optimal_lag = int(np.argmin(ic_values_lag))
        
        all_k_results[k] = {
            'optimal_lag': optimal_lag,
            'ssr': ssr_values_lag[optimal_lag],
            'test_stat': test_stats_lag[optimal_lag],
            'fourier_t_stat': fourier_t_stats_lag[optimal_lag],
            'ic_value': ic_values_lag[optimal_lag],
            'regression_result': results_lag.get(optimal_lag, None)
        }
    
    if not all_k_results:
        raise ValueError("Could not estimate FWADF test. Check data quality.")
    
    # Select optimal k by minimizing SSR (following Enders & Lee 2012)
    optimal_k = min(all_k_results.keys(), 
                    key=lambda k: all_k_results[k]['ssr'])
    
    best_result = all_k_results[optimal_k]
    optimal_lag = best_result['optimal_lag']
    test_statistic = best_result['test_stat']
    fourier_t_stat = best_result['fourier_t_stat']
    ssr = best_result['ssr']
    reg_result = best_result['regression_result']
    
    # Get critical values and p-values
    from .critical_values import (get_fwadf_critical_values, get_fwadf_pvalue,
                                   get_fourier_t_critical_values, get_fourier_t_pvalue)
    
    critical_values = get_fwadf_critical_values(T, optimal_lag, model, optimal_k)
    pvalue = get_fwadf_pvalue(test_statistic, T, optimal_lag, model, optimal_k)
    
    # Get p-value for Fourier term significance
    fourier_t_pvalue = get_fourier_t_pvalue(fourier_t_stat, T, optimal_lag, model, optimal_k)
    
    # Determine if Fourier term is significant at 5% level
    # The Fourier t-test is two-tailed, so check both tails
    fourier_significant = fourier_t_pvalue < 0.05
    
    # Extract coefficients
    delta = float(reg_result['beta'][0])
    beta = float(reg_result['beta'][1])
    se_delta = float(reg_result['se'][0])
    se_beta = float(reg_result['se'][1])
    
    # Create result object
    result = FWADFResult(
        statistic=float(test_statistic),
        pvalue=float(pvalue),
        k=float(optimal_k),
        lag=optimal_lag,
        model=model,
        ic_criterion=ic,
        sample_size=original_n,
        wavelet_sample_size=T,
        critical_values=critical_values,
        fourier_t_stat=float(fourier_t_stat),
        fourier_t_pvalue=float(fourier_t_pvalue),
        fourier_significant=fourier_significant,
        delta=delta,
        beta=beta,
        se_delta=se_delta,
        se_beta=se_beta,
        ssr=float(ssr),
        regression_results=reg_result,
        all_k_results=all_k_results
    )
    
    if verbose:
        print(result)
    
    return result


def fwadf_test_fractional_freq(
    data: np.ndarray,
    model: int = 1,
    max_lag: Optional[int] = None,
    ic: Literal['aic', 'bic'] = 'bic',
    verbose: bool = True
) -> FWADFResult:
    """
    FWADF test with fractional frequency grid following Sephton (2024).
    
    Uses frequency grid from 0.1 to 5.9 in 0.1 increments as recommended
    by Sephton (2024) for more precise detection of smooth breaks.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    model : int
        Model specification (0, 1, or 2).
    max_lag : int, optional
        Maximum lag length.
    ic : str
        Information criterion ('aic' or 'bic').
    verbose : bool
        Print results summary.
    
    Returns
    -------
    FWADFResult
        Test results.
    
    See Also
    --------
    fwadf_test : Standard FWADF test with integer frequencies.
    """
    # Create fractional frequency grid: 0.1, 0.2, ..., 5.9
    freq_grid = [round(x * 0.1, 1) for x in range(1, 60)]
    
    return fwadf_test(
        data=data,
        model=model,
        max_lag=max_lag,
        freq_grid=freq_grid,
        ic=ic,
        verbose=verbose
    )


def _fwadf_statistic_fixed(V: np.ndarray, lag: int, k: float, 
                           model: int) -> Tuple[float, float, dict]:
    """
    Calculate FWADF statistics for fixed lag and frequency.
    
    Internal function used for simulation.
    
    Parameters
    ----------
    V : np.ndarray
        Scaling coefficients.
    lag : int
        Fixed lag length.
    k : float
        Fourier frequency.
    model : int
        Model specification.
    
    Returns
    -------
    test_stat : float
        FWADF test statistic.
    fourier_t : float
        t-statistic on Fourier term.
    result : dict
        OLS regression results.
    """
    T = len(V)
    
    # First difference
    dV = diff(V)
    
    # Lagged level
    V_lag1 = V[:-1]
    
    # Fourier term
    fourier = np.sin(2 * np.pi * k * np.arange(1, T + 1) / T)
    fourier_trimmed = fourier[1:]
    
    # Trim for lag
    start_idx = lag + 1
    
    dep = dV[start_idx:]
    V_lag1_trim = V_lag1[start_idx:]
    fourier_trim = fourier_trimmed[start_idx:]
    
    # Build regressor matrix
    if model == 0:
        X = np.column_stack([V_lag1_trim, fourier_trim])
    elif model == 1:
        ones = np.ones(len(dep))
        X = np.column_stack([V_lag1_trim, fourier_trim, ones])
    else:  # model == 2
        ones = np.ones(len(dep))
        trend = np.arange(1, len(dep) + 1)
        X = np.column_stack([V_lag1_trim, fourier_trim, ones, trend])
    
    # Add lagged differences
    if lag > 0:
        dV_lags = np.zeros((len(dV), lag))
        for j in range(1, lag + 1):
            dV_lags[j:, j-1] = dV[:-j]
            dV_lags[:j, j-1] = np.nan
        
        ldy = dV_lags[start_idx:, :lag]
        X = np.column_stack([X, ldy])
    
    # Remove NaN rows
    valid_idx = ~np.any(np.isnan(X), axis=1)
    dep_valid = dep[valid_idx]
    X_valid = X[valid_idx, :]
    
    # OLS estimation
    result = ols_estimate(dep_valid, X_valid)
    
    return float(result['t_stats'][0]), float(result['t_stats'][1]), result
