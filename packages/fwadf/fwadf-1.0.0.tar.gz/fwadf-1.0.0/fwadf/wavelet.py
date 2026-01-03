"""
Haar Wavelet Transformation Module

Implements the Haar discrete wavelet transform (DWT) for extracting 
low-frequency (scaling) and high-frequency (wavelet) coefficients.

The Haar wavelet is used following Aydin & Pata (2020), who demonstrated 
that it provides the greatest test power for the FWADF test.

References:
    Aydin, M. & Pata, U.K. (2020). Energy, 207, 118245.
    Eroglu, B. & Soybilgen, B. (2018). JRFM, 11(3), 47.
"""

import numpy as np
from typing import Tuple, Optional


def haar_dwt(data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform Haar Discrete Wavelet Transform (DWT) on input data.
    
    The Haar DWT decomposes the signal into:
    - Scaling coefficients (V): Low-frequency components (approximation)
    - Wavelet coefficients (W): High-frequency components (detail)
    
    The transformation follows the equations from Aydin & Pata (2020):
        V[n] = (x[2n] + x[2n+1]) / sqrt(2)  (scaling/approximation)
        W[n] = (x[2n+1] - x[2n]) / sqrt(2)  (wavelet/detail)
    
    Note: The original GAUSS code uses a slightly different formulation:
        V[n] = (x[t+1] + x[t]) / sqrt(2)
        W[n] = (x[t+1] - x[t]) / sqrt(2)
    where t increments by 2 each iteration.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series data (1-dimensional array).
        Length should ideally be even for exact decomposition.
    
    Returns
    -------
    scaling_coeffs : np.ndarray
        Low-frequency scaling coefficients (approximation coefficients).
        Length is approximately half of input length.
    wavelet_coeffs : np.ndarray
        High-frequency wavelet coefficients (detail coefficients).
        Length is approximately half of input length.
    
    Examples
    --------
    >>> import numpy as np
    >>> from fwadf import haar_dwt
    >>> data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    >>> scaling, wavelet = haar_dwt(data)
    >>> print(f"Scaling coefficients: {scaling}")
    >>> print(f"Wavelet coefficients: {wavelet}")
    
    Notes
    -----
    The Haar wavelet is the simplest wavelet transform and is particularly 
    effective for unit root testing because:
    1. It efficiently separates high and low frequency components
    2. Unit root processes have power concentrated at low frequencies
    3. Testing on low-frequency components improves test power
    
    References
    ----------
    Gençay, R., Selçuk, F., & Whitcher, B.J. (2001). An Introduction to 
    Wavelets and Other Filtering Methods in Finance and Economics.
    """
    data = np.asarray(data).flatten()
    n = len(data)
    
    # Check for NaN values
    if np.any(np.isnan(data)):
        raise ValueError("Input data contains NaN values.")
    
    # Check for infinite values
    if np.any(np.isinf(data)):
        raise ValueError("Input data contains infinite values.")
    
    # Ensure we have enough data points
    if n < 2:
        raise ValueError("Input data must have at least 2 observations.")
    
    # Number of coefficient pairs (handles odd-length data)
    n_coeffs = n // 2
    
    # Initialize coefficient arrays
    scaling_coeffs = np.zeros(n_coeffs)
    wavelet_coeffs = np.zeros(n_coeffs)
    
    # Apply Haar DWT following the original GAUSS code
    # The original code: 
    # d1[n1]=(y[t2+1,.]-y[t2,.])/sqrt(2);  (wavelet)
    # yt[n1]=(y[t2+1,.]+y[t2,.])/sqrt(2);  (scaling)
    t2 = 0
    for i in range(n_coeffs):
        scaling_coeffs[i] = (data[t2 + 1] + data[t2]) / np.sqrt(2)
        wavelet_coeffs[i] = (data[t2 + 1] - data[t2]) / np.sqrt(2)
        t2 += 2
    
    return scaling_coeffs, wavelet_coeffs


def haar_scaling_coefficients(data: np.ndarray) -> np.ndarray:
    """
    Extract only the Haar scaling (low-frequency) coefficients.
    
    This is a convenience function that returns only the scaling coefficients
    used in the WADF and FWADF unit root tests.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series data (1-dimensional array).
    
    Returns
    -------
    np.ndarray
        Low-frequency scaling coefficients.
    
    Examples
    --------
    >>> import numpy as np
    >>> from fwadf import haar_scaling_coefficients
    >>> data = np.random.randn(100)
    >>> V = haar_scaling_coefficients(data)
    >>> print(f"Length of scaling coefficients: {len(V)}")
    """
    scaling_coeffs, _ = haar_dwt(data)
    return scaling_coeffs


def inverse_haar_dwt(scaling_coeffs: np.ndarray, 
                     wavelet_coeffs: np.ndarray) -> np.ndarray:
    """
    Perform inverse Haar Discrete Wavelet Transform.
    
    Reconstructs the original signal from scaling and wavelet coefficients.
    
    Parameters
    ----------
    scaling_coeffs : np.ndarray
        Low-frequency scaling coefficients.
    wavelet_coeffs : np.ndarray
        High-frequency wavelet coefficients.
    
    Returns
    -------
    np.ndarray
        Reconstructed signal.
    
    Notes
    -----
    The inverse transform uses:
        x[2n] = (V[n] - W[n]) / sqrt(2)
        x[2n+1] = (V[n] + W[n]) / sqrt(2)
    """
    if len(scaling_coeffs) != len(wavelet_coeffs):
        raise ValueError("Scaling and wavelet coefficient arrays must have same length.")
    
    n_coeffs = len(scaling_coeffs)
    reconstructed = np.zeros(2 * n_coeffs)
    
    sqrt2 = np.sqrt(2)
    for i in range(n_coeffs):
        reconstructed[2 * i] = (scaling_coeffs[i] - wavelet_coeffs[i]) / sqrt2
        reconstructed[2 * i + 1] = (scaling_coeffs[i] + wavelet_coeffs[i]) / sqrt2
    
    return reconstructed


def multilevel_haar_dwt(data: np.ndarray, levels: int = 1) -> dict:
    """
    Perform multi-level Haar DWT decomposition.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series data.
    levels : int, optional
        Number of decomposition levels (default: 1).
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'approx': Final approximation coefficients
        - 'details': List of detail coefficients at each level
    
    Notes
    -----
    For unit root testing, only level-1 decomposition is typically used
    as recommended by Eroglu & Soybilgen (2018).
    """
    if levels < 1:
        raise ValueError("Number of levels must be at least 1.")
    
    details = []
    current_approx = np.asarray(data).flatten()
    
    for level in range(levels):
        if len(current_approx) < 2:
            raise ValueError(f"Data too short for {levels} levels of decomposition.")
        
        current_approx, detail = haar_dwt(current_approx)
        details.append(detail)
    
    return {
        'approx': current_approx,
        'details': details
    }


def _validate_input_data(data: np.ndarray, 
                         min_length: int = 10) -> np.ndarray:
    """
    Validate and prepare input data for wavelet transformation.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series.
    min_length : int
        Minimum required length.
    
    Returns
    -------
    np.ndarray
        Validated and flattened data array.
    
    Raises
    ------
    ValueError
        If data is too short or contains invalid values.
    """
    data = np.asarray(data).flatten()
    
    if len(data) < min_length:
        raise ValueError(f"Input data must have at least {min_length} observations. "
                        f"Got {len(data)}.")
    
    if np.any(np.isnan(data)):
        raise ValueError("Input data contains NaN values.")
    
    if np.any(np.isinf(data)):
        raise ValueError("Input data contains infinite values.")
    
    return data
