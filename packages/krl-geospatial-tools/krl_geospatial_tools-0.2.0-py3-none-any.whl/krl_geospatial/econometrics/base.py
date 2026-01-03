"""
Base classes for spatial econometric models.

This module provides abstract base classes and result containers for
spatial econometric analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import sparse

logger = get_logger(__name__)


@dataclass
class RegressionResult:
    """
    Container for regression results.

    Stores coefficients, standard errors, statistics, and diagnostics
    from spatial econometric models.

    Attributes:
        model_name: Name of the model
        coefficients: Estimated coefficients
        std_errors: Standard errors
        t_stats: T-statistics
        p_values: P-values
        residuals: Model residuals
        fitted_values: Fitted values
        n_obs: Number of observations
        n_vars: Number of variables
        r_squared: R-squared
        adj_r_squared: Adjusted R-squared
        log_likelihood: Log-likelihood
        aic: Akaike Information Criterion
        bic: Bayesian Information Criterion
        spatial_params: Spatial parameters (rho, lambda, etc.)
        extra_info: Additional model-specific information
    """

    model_name: str
    coefficients: np.ndarray
    std_errors: np.ndarray
    t_stats: np.ndarray
    p_values: np.ndarray
    residuals: np.ndarray
    fitted_values: np.ndarray
    n_obs: int
    n_vars: int
    r_squared: float
    adj_r_squared: float
    log_likelihood: float
    aic: float
    bic: float
    spatial_params: Dict[str, float] = field(default_factory=dict)
    extra_info: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """
        Generate a summary of regression results.

        Returns:
            Formatted summary string
        """
        summary = []
        summary.append("=" * 78)
        summary.append(f"{self.model_name} Regression Results")
        summary.append("=" * 78)
        summary.append(f"Number of observations: {self.n_obs}")
        summary.append(f"Number of variables:    {self.n_vars}")
        summary.append(f"R-squared:              {self.r_squared:.4f}")
        summary.append(f"Adjusted R-squared:     {self.adj_r_squared:.4f}")
        summary.append(f"Log-likelihood:         {self.log_likelihood:.4f}")
        summary.append(f"AIC:                    {self.aic:.4f}")
        summary.append(f"BIC:                    {self.bic:.4f}")

        if self.spatial_params:
            summary.append("\nSpatial Parameters:")
            for key, value in self.spatial_params.items():
                summary.append(f"  {key:20s}: {value:.4f}")

        summary.append("\n" + "-" * 78)
        summary.append(
            f"{'Variable':<20} {'Coeff':>12} {'Std.Err':>12} {'t-stat':>10} {'P>|t|':>10}"
        )
        summary.append("-" * 78)

        for i in range(len(self.coefficients)):
            var_name = f"var_{i}" if i < len(self.coefficients) else "unknown"
            summary.append(
                f"{var_name:<20} {self.coefficients[i]:>12.4f} "
                f"{self.std_errors[i]:>12.4f} {self.t_stats[i]:>10.4f} "
                f"{self.p_values[i]:>10.4f}"
            )

        summary.append("=" * 78)

        return "\n".join(summary)

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return {
            "model_name": self.model_name,
            "coefficients": self.coefficients.tolist(),
            "std_errors": self.std_errors.tolist(),
            "t_stats": self.t_stats.tolist(),
            "p_values": self.p_values.tolist(),
            "n_obs": self.n_obs,
            "n_vars": self.n_vars,
            "r_squared": self.r_squared,
            "adj_r_squared": self.adj_r_squared,
            "log_likelihood": self.log_likelihood,
            "aic": self.aic,
            "bic": self.bic,
            "spatial_params": self.spatial_params,
            "extra_info": self.extra_info,
        }


class BaseEconometricModel(ABC):
    """
    Abstract base class for econometric models.

    Provides common interface and utilities for spatial econometric models.
    """

    def __init__(self, name: str = "BaseModel"):
        """
        Initialize model.

        Args:
            name: Model name
        """
        self.name = name
        self.result: Optional[RegressionResult] = None
        self._is_fitted = False

        logger.debug(f"Initialized {name}")

    @abstractmethod
    def fit(
        self, y: np.ndarray, X: np.ndarray, W: Optional[sparse.csr_matrix] = None, **kwargs
    ) -> RegressionResult:
        """
        Fit the model.

        Args:
            y: Dependent variable (n x 1)
            X: Independent variables (n x k)
            W: Spatial weights matrix (optional)
            **kwargs: Additional model-specific parameters

        Returns:
            RegressionResult object
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Generate predictions.

        Args:
            X: Independent variables

        Returns:
            Predicted values
        """
        pass

    def _validate_inputs(
        self, y: np.ndarray, X: np.ndarray, W: Optional[sparse.csr_matrix] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Validate and prepare inputs.

        Args:
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix

        Returns:
            Validated (y, X) arrays

        Raises:
            ValueError: If inputs are invalid
        """
        # Convert to numpy arrays
        y = np.asarray(y).flatten()
        X = np.asarray(X)

        # Check dimensions
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if len(y) != X.shape[0]:
            raise ValueError(
                f"y and X must have same number of observations. "
                f"Got y: {len(y)}, X: {X.shape[0]}"
            )

        # Check for NaN/Inf
        if np.any(np.isnan(y)) or np.any(np.isinf(y)):
            raise ValueError("y contains NaN or Inf values")

        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ValueError("X contains NaN or Inf values")

        # Validate weights matrix if provided
        if W is not None:
            if not sparse.issparse(W):
                W = sparse.csr_matrix(W)

            if W.shape[0] != W.shape[1]:
                raise ValueError("W must be square matrix")

            if W.shape[0] != len(y):
                raise ValueError(
                    f"W dimensions must match number of observations. "
                    f"Got W: {W.shape[0]}, y: {len(y)}"
                )

        return y, X

    def _calculate_fit_statistics(
        self, y: np.ndarray, y_pred: np.ndarray, n_params: int
    ) -> Tuple[float, float]:
        """
        Calculate R-squared and adjusted R-squared.

        Args:
            y: Observed values
            y_pred: Predicted values
            n_params: Number of parameters

        Returns:
            (r_squared, adj_r_squared)
        """
        # R-squared
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Adjusted R-squared
        n = len(y)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - n_params - 1)

        return r_squared, adj_r_squared

    def _calculate_information_criteria(
        self, log_likelihood: float, n_obs: int, n_params: int
    ) -> Tuple[float, float]:
        """
        Calculate AIC and BIC.

        Args:
            log_likelihood: Log-likelihood
            n_obs: Number of observations
            n_params: Number of parameters

        Returns:
            (aic, bic)
        """
        aic = -2 * log_likelihood + 2 * n_params
        bic = -2 * log_likelihood + n_params * np.log(n_obs)

        return aic, bic

    def __repr__(self) -> str:
        """String representation."""
        fitted = "fitted" if self._is_fitted else "not fitted"
        return f"{self.name}({fitted})"
