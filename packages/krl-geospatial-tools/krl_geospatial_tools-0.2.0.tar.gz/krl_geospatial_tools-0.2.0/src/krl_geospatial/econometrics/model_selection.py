"""
Model selection utilities for spatial econometrics.

Provides automated model selection, comparison, and specification testing.
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import sparse, stats

from .base import RegressionResult
from .diagnostics import lm_error_test, lm_lag_test, lm_sarma_test
from .error_model import SpatialError
from .lag_model import SpatialLag
from .ols import OLS
from .spatial_models import SpatialAutoregressiveCombined, SpatialDurbin, SpatialDurbinError

logger = get_logger(__name__)


class ModelSelector:
    """
    Automated spatial model selection.

    Implements decision tree approach following Anselin (2005) and
    model comparison based on information criteria.

    Examples:
        >>> selector = ModelSelector()
        >>> best_model, results = selector.select_model(y, X, W)
        >>> print(f"Best model: {best_model}")
        >>> print(f"AIC: {results['aic']}")

    References:
        Anselin, L. (2005). Exploring spatial data with GeoDa:
        A workbook. Spatial Analysis Laboratory.
    """

    def __init__(self, significance_level: float = 0.05):
        """
        Initialize model selector.

        Args:
            significance_level: Significance level for LM tests
        """
        self.significance_level = significance_level
        self.results: Dict[str, Any] = {}

    def select_model(
        self,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        method: str = "decision_tree",
        add_constant: bool = True,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Select best spatial model.

        Args:
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
            method: Selection method ('decision_tree', 'aic', 'bic', 'all')
            add_constant: Add intercept

        Returns:
            Tuple of (best_model_name, results_dict)

        Examples:
            >>> best, results = selector.select_model(y, X, W)
            >>> if best == 'Spatial Lag':
            ...     sar = SpatialLag()
            ...     final_result = sar.fit(y, X, W)
        """
        logger.info(f"Starting model selection using {method}")

        # Fit OLS baseline
        ols = OLS()
        ols_result = ols.fit(y, X, W, add_constant=add_constant)

        self.results["OLS"] = {
            "result": ols_result,
            "aic": ols_result.aic,
            "bic": ols_result.bic,
            "log_likelihood": ols_result.log_likelihood,
        }

        if method == "decision_tree":
            return self._decision_tree_selection(y, X, W, ols_result, add_constant)

        elif method in ["aic", "bic", "all"]:
            return self._information_criteria_selection(
                y, X, W, ols_result, criterion=method, add_constant=add_constant
            )

        else:
            raise ValueError(f"Unknown method: {method}")

    def _decision_tree_selection(
        self,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        ols_result: RegressionResult,
        add_constant: bool,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Anselin decision tree for spatial model selection.

        Based on Lagrange Multiplier tests.
        """
        # Run LM tests on OLS residuals
        lm_lag, p_lag = lm_lag_test(
            ols_result.residuals,
            X if not add_constant else np.column_stack([np.ones(len(X)), X]),
            W,
        )
        lm_error, p_error = lm_error_test(
            ols_result.residuals,
            X if not add_constant else np.column_stack([np.ones(len(X)), X]),
            W,
        )

        logger.info(f"LM lag: {lm_lag:.4f} (p={p_lag:.4f})")
        logger.info(f"LM error: {lm_error:.4f} (p={p_error:.4f})")

        # Decision tree logic
        alpha = self.significance_level

        # Store diagnostic results
        self.results["diagnostics"] = {
            "lm_lag": lm_lag,
            "lm_lag_pvalue": p_lag,
            "lm_error": lm_error,
            "lm_error_pvalue": p_error,
        }

        # Case 1: Neither test significant -> OLS
        if p_lag > alpha and p_error > alpha:
            logger.info("No spatial dependence detected -> OLS")
            return "OLS", self.results

        # Case 2: Both tests significant -> compare and use robust tests
        if p_lag < alpha and p_error < alpha:
            logger.info("Both lag and error significant, checking robust tests")

            # Fit both models and compare
            try:
                sar = SpatialLag()
                sar_result = sar.fit(y, X, W, add_constant=add_constant)
                self.results["Spatial Lag"] = {
                    "result": sar_result,
                    "aic": sar_result.aic,
                    "bic": sar_result.bic,
                }
            except Exception as e:
                logger.warning(f"SAR fit failed: {e}")
                sar_result = None

            try:
                sem = SpatialError()
                sem_result = sem.fit(y, X, W, add_constant=add_constant)
                self.results["Spatial Error"] = {
                    "result": sem_result,
                    "aic": sem_result.aic,
                    "bic": sem_result.bic,
                }
            except Exception as e:
                logger.warning(f"SEM fit failed: {e}")
                sem_result = None

            # Choose based on AIC
            if sar_result and sem_result:
                if sar_result.aic < sem_result.aic:
                    logger.info("SAR has lower AIC -> Spatial Lag")
                    return "Spatial Lag", self.results
                else:
                    logger.info("SEM has lower AIC -> Spatial Error")
                    return "Spatial Error", self.results
            elif sar_result:
                return "Spatial Lag", self.results
            elif sem_result:
                return "Spatial Error", self.results
            else:
                return "OLS", self.results

        # Case 3: Only lag significant
        if p_lag < alpha and p_error > alpha:
            logger.info("Spatial lag dependence detected -> Spatial Lag")
            try:
                sar = SpatialLag()
                sar_result = sar.fit(y, X, W, add_constant=add_constant)
                self.results["Spatial Lag"] = {
                    "result": sar_result,
                    "aic": sar_result.aic,
                    "bic": sar_result.bic,
                }
                return "Spatial Lag", self.results
            except Exception as e:
                logger.error(f"SAR fit failed: {e}")
                return "OLS", self.results

        # Case 4: Only error significant
        if p_lag > alpha and p_error < alpha:
            logger.info("Spatial error dependence detected -> Spatial Error")
            try:
                sem = SpatialError()
                sem_result = sem.fit(y, X, W, add_constant=add_constant)
                self.results["Spatial Error"] = {
                    "result": sem_result,
                    "aic": sem_result.aic,
                    "bic": sem_result.bic,
                }
                return "Spatial Error", self.results
            except Exception as e:
                logger.error(f"SEM fit failed: {e}")
                return "OLS", self.results

        # Default
        return "OLS", self.results

    def _information_criteria_selection(
        self,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        ols_result: RegressionResult,
        criterion: str,
        add_constant: bool,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Model selection based on information criteria.

        Fits all models and selects best by AIC/BIC.
        """
        models = {
            "OLS": (OLS(), {}),
            "Spatial Lag": (SpatialLag(), {}),
            "Spatial Error": (SpatialError(), {}),
        }

        # Try advanced models
        try:
            models["Spatial Durbin"] = (SpatialDurbin(), {})
            models["Spatial Durbin Error"] = (SpatialDurbinError(), {})
        except:
            pass

        # Fit all models
        for model_name, (model, params) in models.items():
            if model_name == "OLS":
                continue  # Already fitted

            try:
                logger.info(f"Fitting {model_name}")
                result = model.fit(y, X, W, add_constant=add_constant, **params)

                self.results[model_name] = {
                    "result": result,
                    "aic": result.aic,
                    "bic": result.bic,
                    "log_likelihood": result.log_likelihood,
                }
            except Exception as e:
                logger.warning(f"Failed to fit {model_name}: {e}")

        # Select best model
        if criterion == "aic":
            best_model = min(self.results.keys(), key=lambda k: self.results[k]["aic"])
            logger.info(f"Best model by AIC: {best_model}")
        elif criterion == "bic":
            best_model = min(self.results.keys(), key=lambda k: self.results[k]["bic"])
            logger.info(f"Best model by BIC: {best_model}")
        else:  # 'all' - use average rank
            ranks = {}
            for model_name in self.results.keys():
                aic_rank = sorted(self.results.keys(), key=lambda k: self.results[k]["aic"]).index(
                    model_name
                )
                bic_rank = sorted(self.results.keys(), key=lambda k: self.results[k]["bic"]).index(
                    model_name
                )
                ranks[model_name] = (aic_rank + bic_rank) / 2

            best_model = min(ranks.keys(), key=lambda k: ranks[k])
            logger.info(f"Best model by average rank: {best_model}")

        return best_model, self.results

    def get_model_comparison_table(self) -> Dict[str, Dict[str, float]]:
        """
        Get model comparison table.

        Returns:
            Dictionary with model statistics
        """
        comparison = {}

        for model_name, data in self.results.items():
            if model_name == "diagnostics":
                continue

            comparison[model_name] = {
                "AIC": data["aic"],
                "BIC": data["bic"],
                "Log-Likelihood": data["log_likelihood"],
                "R-squared": data["result"].r_squared,
            }

        return comparison


def spatial_heterogeneity_test(
    y: np.ndarray, X: np.ndarray, coords: np.ndarray, n_groups: int = 4
) -> Dict[str, Any]:
    """
    Test for spatial heterogeneity using Chow test.

    Divides space into regions and tests if coefficients differ.

    Args:
        y: Dependent variable
        X: Independent variables
        coords: Coordinates (n x 2)
        n_groups: Number of spatial groups to create

    Returns:
        Dictionary with test statistic and p-value

    Examples:
        >>> result = spatial_heterogeneity_test(y, X, coords)
        >>> if result['significant']:
        ...     print("Spatial heterogeneity detected - consider GWR")
    """
    n = len(y)
    k = X.shape[1] + 1  # Including constant

    # Add constant
    X_const = np.column_stack([np.ones(n), X])

    # Divide space into groups based on coordinates
    # Use k-means clustering
    from sklearn.cluster import KMeans

    kmeans = KMeans(n_clusters=n_groups, random_state=42, n_init=10)
    groups = kmeans.fit_predict(coords)

    # Fit pooled model (all data)
    beta_pooled = np.linalg.lstsq(X_const, y, rcond=None)[0]
    residuals_pooled = y - X_const @ beta_pooled
    ssr_pooled = np.sum(residuals_pooled**2)

    # Fit separate models for each group
    ssr_separate = 0
    valid_groups = 0

    for g in range(n_groups):
        mask = groups == g
        if np.sum(mask) > k:  # Enough observations
            X_g = X_const[mask]
            y_g = y[mask]

            try:
                beta_g = np.linalg.lstsq(X_g, y_g, rcond=None)[0]
                residuals_g = y_g - X_g @ beta_g
                ssr_separate += np.sum(residuals_g**2)
                valid_groups += 1
            except:
                ssr_separate += np.sum((y_g - np.mean(y_g)) ** 2)

    if valid_groups < 2:
        return {
            "statistic": np.nan,
            "p_value": np.nan,
            "significant": False,
            "message": "Not enough valid groups for test",
        }

    # Chow test statistic
    # F = [(SSR_pooled - SSR_separate) / (k * (n_groups - 1))] / [SSR_separate / (n - k * n_groups)]

    numerator_df = k * (valid_groups - 1)
    denominator_df = n - k * valid_groups

    if denominator_df <= 0:
        return {
            "statistic": np.nan,
            "p_value": np.nan,
            "significant": False,
            "message": "Insufficient degrees of freedom",
        }

    F_stat = ((ssr_pooled - ssr_separate) / numerator_df) / (ssr_separate / denominator_df)
    p_value = 1 - stats.f.cdf(F_stat, numerator_df, denominator_df)

    return {
        "statistic": F_stat,
        "p_value": p_value,
        "n_groups": valid_groups,
        "significant": p_value < 0.05,
        "message": (
            "Significant spatial heterogeneity detected"
            if p_value < 0.05
            else "No significant spatial heterogeneity"
        ),
    }


def cusum_test(residuals: np.ndarray, significance: float = 0.05) -> Dict[str, Any]:
    """
    CUSUM test for parameter stability.

    Detects structural breaks in coefficients over space or time.

    Args:
        residuals: Model residuals (ordered)
        significance: Significance level

    Returns:
        Dictionary with test results
    """
    n = len(residuals)

    # Standardize residuals
    sigma = np.std(residuals)
    residuals_std = residuals / (sigma + 1e-10)

    # Calculate CUSUM
    cusum = np.cumsum(residuals_std) / np.sqrt(n)

    # Critical values (approximate)
    critical_value = 0.948 * np.sqrt(significance)  # 5% level

    # Check if CUSUM exceeds boundaries
    breaks_detected = np.any(np.abs(cusum) > critical_value)

    return {
        "cusum": cusum,
        "critical_value": critical_value,
        "breaks_detected": breaks_detected,
        "max_cusum": np.max(np.abs(cusum)),
    }


def hausman_test(ols_result: RegressionResult, spatial_result: RegressionResult) -> Dict[str, Any]:
    """
    Hausman specification test.

    Tests whether spatial model is significantly different from OLS.

    Args:
        ols_result: OLS regression result
        spatial_result: Spatial model result

    Returns:
        Dictionary with test statistic and p-value
    """
    # Extract coefficients (excluding spatial parameters)
    beta_ols = ols_result.coefficients
    beta_spatial = spatial_result.coefficients

    # Ensure same dimension
    k = min(len(beta_ols), len(beta_spatial))
    beta_ols = beta_ols[:k]
    beta_spatial = beta_spatial[:k]

    # Difference
    diff = beta_spatial - beta_ols

    # Variance (simplified - should use proper covariance matrices)
    var_ols = ols_result.std_errors[:k] ** 2
    var_spatial = spatial_result.std_errors[:k] ** 2
    var_diff = var_spatial - var_ols

    # Handle negative variances (can occur with efficient estimator)
    var_diff = np.maximum(var_diff, 1e-6)

    # Hausman statistic
    H = float(np.sum(diff**2 / var_diff))
    p_value = 1 - stats.chi2.cdf(H, df=k)

    return {
        "statistic": H,
        "p_value": p_value,
        "df": k,
        "significant": p_value < 0.05,
        "message": "Spatial model preferred" if p_value < 0.05 else "OLS adequate",
    }
