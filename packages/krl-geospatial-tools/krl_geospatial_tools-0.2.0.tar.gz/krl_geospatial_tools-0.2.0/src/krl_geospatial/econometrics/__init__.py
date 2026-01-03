"""
Spatial econometrics module for KRL Geospatial Tools.

This module provides spatial econometric models including spatial regression,
autocorrelation tests, and model diagnostics.
"""

from .autocorrelation import gearys_c, getis_ord_g, getis_ord_gi_star, local_morans_i, morans_i
from .base import BaseEconometricModel, RegressionResult
from .diagnostics import (
    aic,
    bic,
    compare_models,
    likelihood_ratio_test,
    lm_error_test,
    lm_lag_test,
    lm_sarma_test,
    pseudo_r2,
    residual_diagnostics,
    robust_lm_error_test,
    robust_lm_lag_test,
)
from .error_model import SpatialError
from .gwr import GeographicallyWeightedRegression
from .lag_model import SpatialLag
from .model_selection import ModelSelector, cusum_test, hausman_test, spatial_heterogeneity_test
from .ols import OLS
from .parallel_gwr import (
    ParallelGWR,
    ParallelGWRConfig,
    ParallelGWRResult,
    ParallelBackend,
    KernelType,
    BandwidthMethod,
    create_parallel_gwr,
)
from .spatial_models import SpatialAutoregressiveCombined, SpatialDurbin, SpatialDurbinError

__all__ = [
    # Base classes
    "BaseEconometricModel",
    "RegressionResult",
    # Regression models
    "OLS",
    "SpatialLag",
    "SpatialError",
    "GeographicallyWeightedRegression",
    "SpatialDurbin",
    "SpatialDurbinError",
    "SpatialAutoregressiveCombined",
    # Autocorrelation tests
    "morans_i",
    "gearys_c",
    "local_morans_i",
    "getis_ord_g",
    "getis_ord_gi_star",
    # Diagnostics
    "lm_lag_test",
    "lm_error_test",
    "lm_sarma_test",
    "robust_lm_lag_test",
    "robust_lm_error_test",
    "aic",
    "bic",
    "pseudo_r2",
    "likelihood_ratio_test",
    "residual_diagnostics",
    "compare_models",
    # Model selection
    "ModelSelector",
    "spatial_heterogeneity_test",
    "cusum_test",
    "hausman_test",
    # Parallel GWR
    "ParallelGWR",
    "ParallelGWRConfig",
    "ParallelGWRResult",
    "ParallelBackend",
    "KernelType",
    "BandwidthMethod",
    "create_parallel_gwr",
]
