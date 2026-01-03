"""
FWADF - Fourier Wavelet Augmented Dickey-Fuller Unit Root Test

A Python library implementing the Fourier Wavelet Augmented Dickey-Fuller (FWADF) 
and Wavelet Augmented Dickey-Fuller (WADF) unit root tests.

This implementation is based on:
    1. Aydin, M. & Pata, U.K. (2020). "Are Shocks to Disaggregated Renewable Energy 
       Consumption Permanent or Temporary for the USA? Wavelet Based Unit Root Test 
       with Smooth Structural Shifts." Energy, 207, 118245.
    
    2. Sephton, P.S. (2024). "Finite Sample Lag Adjusted Critical Values and 
       Probability Values for the Fourier Wavelet Unit Root Test." 
       Computational Economics, 64, 693-705.
    
    3. Eroglu, B. & Soybilgen, B. (2018). "On the Performance of Wavelet Based 
       Unit Root Tests." Journal of Risk and Financial Management, 11(3), 47.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/fwadf
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .wadf import wadf_test, WADFResult
from .fwadf import fwadf_test, FWADFResult
from .wavelet import haar_dwt, haar_scaling_coefficients
from .critical_values import (
    get_fwadf_critical_values,
    get_wadf_critical_values,
    get_fwadf_pvalue,
    get_wadf_pvalue,
    get_fourier_t_critical_values,
    get_fourier_t_pvalue
)
from .simulation import (
    simulate_fwadf_critical_values,
    simulate_wadf_critical_values,
    simulate_fourier_t_critical_values
)

__all__ = [
    # Main test functions
    "fwadf_test",
    "wadf_test",
    # Result classes
    "FWADFResult",
    "WADFResult",
    # Wavelet functions
    "haar_dwt",
    "haar_scaling_coefficients",
    # Critical values and p-values
    "get_fwadf_critical_values",
    "get_wadf_critical_values",
    "get_fwadf_pvalue",
    "get_wadf_pvalue",
    "get_fourier_t_critical_values",
    "get_fourier_t_pvalue",
    # Simulation functions
    "simulate_fwadf_critical_values",
    "simulate_wadf_critical_values",
    "simulate_fourier_t_critical_values",
]
