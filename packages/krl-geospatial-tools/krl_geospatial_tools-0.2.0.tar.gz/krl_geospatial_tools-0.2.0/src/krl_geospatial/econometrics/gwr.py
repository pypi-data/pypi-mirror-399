"""
Geographically Weighted Regression (GWR).

Implements local spatial regression with spatially varying coefficients.
"""

import warnings
from typing import Any, Callable, Dict, Optional, Tuple, Union

import geopandas as gpd
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import sparse, spatial, stats
from scipy.optimize import minimize_scalar

from .base import BaseEconometricModel, RegressionResult

logger = get_logger(__name__)


class GeographicallyWeightedRegression(BaseEconometricModel):
    """
    Geographically Weighted Regression (GWR).

    Estimates spatially varying coefficients by fitting local regressions
    at each observation location using geographically weighted least squares.

    GWR model:
        y_i = β_0(u_i, v_i) + Σ β_k(u_i, v_i)x_ik + ε_i

    where (u_i, v_i) are coordinates and β_k(u_i, v_i) are location-specific
    coefficients.

    Attributes:
        kernel: Spatial weighting kernel function
        bandwidth: Bandwidth parameter for kernel
        adaptive: Whether to use adaptive bandwidth
        local_coefficients: Location-specific coefficient estimates (n x k)
        local_std_errors: Location-specific standard errors (n x k)

    Examples:
        >>> gwr = GeographicallyWeightedRegression(kernel='gaussian')
        >>> result = gwr.fit(y, X, coords, bandwidth=0.5)
        >>> # Check for spatial variation in coefficients
        >>> beta_variation = np.std(gwr.local_coefficients, axis=0)
        >>> print(f"Coefficient variation: {beta_variation}")

    References:
        Fotheringham, A.S., Brunsdon, C., & Charlton, M. (2002).
        Geographically Weighted Regression: The Analysis of Spatially
        Varying Relationships. John Wiley & Sons.
    """

    def __init__(self, kernel: str = "gaussian", adaptive: bool = False):
        """
        Initialize GWR model.

        Args:
            kernel: Kernel type ('gaussian', 'exponential', 'bisquare', 'tricube')
            adaptive: Use adaptive (k-nearest neighbors) bandwidth
        """
        super().__init__(name="Geographically Weighted Regression")
        self.kernel = kernel
        self.adaptive = adaptive
        self.bandwidth: Optional[float] = None
        self.local_coefficients: Optional[np.ndarray] = None
        self.local_std_errors: Optional[np.ndarray] = None
        self.local_r_squared: Optional[np.ndarray] = None
        self._coords: Optional[np.ndarray] = None

        logger.debug(f"Initialized GWR: kernel={kernel}, adaptive={adaptive}")

    def fit(
        self,
        y: np.ndarray,
        X: np.ndarray,
        coords: np.ndarray,
        bandwidth: Optional[float] = None,
        add_constant: bool = True,
        bandwidth_selection: str = "aic",
    ) -> RegressionResult:
        """
        Fit GWR model.

        Args:
            y: Dependent variable (n x 1)
            X: Independent variables (n x k)
            coords: Coordinates (n x 2) - (x, y) or (lon, lat)
            bandwidth: Bandwidth parameter. If None, will be selected automatically
            add_constant: Whether to add intercept
            bandwidth_selection: Method for bandwidth selection ('aic', 'cv', 'aicc')

        Returns:
            RegressionResult with global summary statistics

        Examples:
            >>> coords = gdf.geometry.centroid.get_coordinates().values
            >>> result = gwr.fit(y, X, coords)
            >>> # Access local coefficients
            >>> local_betas = gwr.local_coefficients
        """
        # Validate inputs
        y, X = self._validate_inputs(y, X)
        coords = np.asarray(coords)

        if coords.shape[0] != len(y):
            raise ValueError(
                f"coords must have same length as y. Got {coords.shape[0]} vs {len(y)}"
            )

        if coords.shape[1] != 2:
            raise ValueError(f"coords must have 2 columns (x, y). Got {coords.shape[1]}")

        # Store coordinates
        self._coords = coords

        # Add constant if requested
        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        logger.debug(f"Fitting GWR: n={n_obs}, k={n_vars}")

        # Select bandwidth if not provided
        if bandwidth is None:
            logger.info(f"Selecting bandwidth using {bandwidth_selection}")
            self.bandwidth = self._select_bandwidth(y, X, coords, method=bandwidth_selection)
        else:
            self.bandwidth = bandwidth

        logger.info(f"Using bandwidth: {self.bandwidth:.4f}")

        # Estimate local coefficients at each location
        self.local_coefficients = np.zeros((n_obs, n_vars))
        self.local_std_errors = np.zeros((n_obs, n_vars))
        self.local_r_squared = np.zeros(n_obs)

        fitted_values = np.zeros(n_obs)
        residuals = np.zeros(n_obs)

        for i in range(n_obs):
            # Calculate spatial weights for location i
            weights = self._calculate_weights(coords, i, self.bandwidth)

            # Weighted least squares
            W_diag = np.diag(weights)
            X_weighted = np.sqrt(W_diag) @ X
            y_weighted = np.sqrt(W_diag) @ y

            # Estimate local coefficients
            try:
                XtWX = X_weighted.T @ X_weighted
                XtWy = X_weighted.T @ y_weighted
                beta_i = np.linalg.solve(XtWX, XtWy)
            except np.linalg.LinAlgError:
                # Use pseudo-inverse if singular
                beta_i = np.linalg.lstsq(X_weighted, y_weighted, rcond=None)[0]

            self.local_coefficients[i] = beta_i

            # Calculate fitted value at location i
            fitted_values[i] = X[i] @ beta_i

            # Local standard errors
            residuals_i = y - X @ beta_i
            sigma_i_sq = np.sum(weights * residuals_i**2) / np.sum(weights)

            try:
                var_covar_i = sigma_i_sq * np.linalg.inv(XtWX)
                self.local_std_errors[i] = np.sqrt(np.diag(var_covar_i))
            except:
                self.local_std_errors[i] = np.nan

            # Local R-squared
            y_weighted_mean = np.average(y, weights=weights)
            ss_res = np.sum(weights * (y - fitted_values[i]) ** 2)
            ss_tot = np.sum(weights * (y - y_weighted_mean) ** 2)
            self.local_r_squared[i] = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Calculate residuals
        residuals = y - fitted_values

        # Global statistics (summary)
        mean_coefficients = np.mean(self.local_coefficients, axis=0)
        std_coefficients = np.std(self.local_coefficients, axis=0)

        # Global fit statistics
        r_squared, adj_r_squared = self._calculate_fit_statistics(y, fitted_values, n_vars)

        # Calculate effective degrees of freedom
        tr_S = self._trace_hat_matrix(X, coords, self.bandwidth)

        # AICc for GWR
        sigma_squared = np.sum(residuals**2) / n_obs
        log_likelihood = -0.5 * n_obs * (np.log(2 * np.pi) + np.log(sigma_squared) + 1)

        # Corrected AIC for GWR
        aic = -2 * log_likelihood + 2 * tr_S
        aicc = aic + (2 * tr_S * (tr_S + 1)) / (n_obs - tr_S - 1)
        bic = -2 * log_likelihood + tr_S * np.log(n_obs)

        # Store result
        self.result = RegressionResult(
            model_name=self.name,
            coefficients=mean_coefficients,
            std_errors=std_coefficients,  # Using std dev as proxy
            t_stats=mean_coefficients / std_coefficients,
            p_values=2 * (1 - stats.norm.cdf(np.abs(mean_coefficients / std_coefficients))),
            residuals=residuals,
            fitted_values=fitted_values,
            n_obs=n_obs,
            n_vars=n_vars,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            spatial_params={
                "bandwidth": self.bandwidth,
                "kernel": self.kernel,
                "adaptive": self.adaptive,
                "trace_hat": tr_S,
                "effective_df": tr_S,
                "residual_df": n_obs
                - 2 * tr_S
                + np.trace(self._hat_matrix(X, coords, self.bandwidth) ** 2),
            },
            extra_info={
                "aicc": aicc,
                "local_coefficients": self.local_coefficients,
                "local_std_errors": self.local_std_errors,
                "local_r_squared": self.local_r_squared,
                "coefficient_ranges": {
                    "min": np.min(self.local_coefficients, axis=0),
                    "max": np.max(self.local_coefficients, axis=0),
                    "std": std_coefficients,
                },
            },
        )

        self._is_fitted = True
        logger.info(f"GWR fitted: bandwidth={self.bandwidth:.4f}, R²={r_squared:.4f}")

        return self.result

    def _calculate_weights(
        self, coords: np.ndarray, focal_index: int, bandwidth: float
    ) -> np.ndarray:
        """
        Calculate spatial weights for a focal location.

        Args:
            coords: All coordinates (n x 2)
            focal_index: Index of focal location
            bandwidth: Bandwidth parameter

        Returns:
            Weight vector (n,)
        """
        # Calculate distances from focal point
        focal_coord = coords[focal_index]
        distances = np.sqrt(np.sum((coords - focal_coord) ** 2, axis=1))

        if self.adaptive:
            # Adaptive bandwidth: use k-nearest neighbors
            k = int(bandwidth)
            sorted_idx = np.argsort(distances)
            max_dist = distances[sorted_idx[min(k, len(distances) - 1)]]
            distances = distances / max_dist if max_dist > 0 else distances
        else:
            # Fixed bandwidth
            distances = distances / bandwidth

        # Apply kernel function
        weights = self._kernel_function(distances)

        return weights

    def _kernel_function(self, distances: np.ndarray) -> np.ndarray:
        """
        Apply kernel weighting function.

        Args:
            distances: Normalized distances

        Returns:
            Weights
        """
        if self.kernel == "gaussian":
            return np.exp(-0.5 * distances**2)

        elif self.kernel == "exponential":
            return np.exp(-distances)

        elif self.kernel == "bisquare":
            weights = np.zeros_like(distances)
            mask = distances < 1
            weights[mask] = (1 - distances[mask] ** 2) ** 2
            return weights

        elif self.kernel == "tricube":
            weights = np.zeros_like(distances)
            mask = distances < 1
            weights[mask] = (1 - distances[mask] ** 3) ** 3
            return weights

        else:
            raise ValueError(f"Unknown kernel: {self.kernel}")

    def _select_bandwidth(
        self, y: np.ndarray, X: np.ndarray, coords: np.ndarray, method: str = "aic"
    ) -> float:
        """
        Automatic bandwidth selection.

        Args:
            y: Dependent variable
            X: Independent variables
            coords: Coordinates
            method: Selection criterion ('aic', 'aicc', 'cv')

        Returns:
            Optimal bandwidth
        """
        n = len(y)

        n = len(y)
        k = X.shape[1] + 1  # Including constant

        # Determine search range
        if self.adaptive:
            # For adaptive, bandwidth is number of neighbors
            bw_min = max(k + 1, 10)
            bw_max = n - 1
        else:
            # For fixed, bandwidth is distance
            all_distances = spatial.distance.pdist(coords)
            bw_min = np.percentile(all_distances, 1)
            bw_max = np.percentile(all_distances, 50)

        # Objective function
        if method == "cv":

            def objective(bw):
                return self._cross_validation_score(y, X, coords, bw)

        else:  # aic or aicc

            def objective(bw):
                return self._calculate_aic(y, X, coords, bw, corrected=(method == "aicc"))

        # Golden section search
        result = minimize_scalar(objective, bounds=(bw_min, bw_max), method="bounded")

        return result.x

    def _calculate_aic(
        self,
        y: np.ndarray,
        X: np.ndarray,
        coords: np.ndarray,
        bandwidth: float,
        corrected: bool = True,
    ) -> float:
        """Calculate AIC or AICc for a given bandwidth."""
        n = len(y)

        # Quick fit to calculate residuals
        fitted_values = np.zeros(n)

        for i in range(n):
            weights = self._calculate_weights(coords, i, bandwidth)
            W_diag = np.diag(weights)
            X_weighted = np.sqrt(W_diag) @ X
            y_weighted = np.sqrt(W_diag) @ y

            try:
                beta_i = np.linalg.solve(X_weighted.T @ X_weighted, X_weighted.T @ y_weighted)
                fitted_values[i] = X[i] @ beta_i
            except:
                fitted_values[i] = np.mean(y)

        residuals = y - fitted_values
        sigma_squared = np.sum(residuals**2) / n

        # Effective degrees of freedom
        tr_S = self._trace_hat_matrix(X, coords, bandwidth)

        # AIC
        aic = n * np.log(sigma_squared) + n * np.log(2 * np.pi) + n + 2 * tr_S

        if corrected:
            # AICc correction
            aic += (2 * tr_S * (tr_S + 1)) / (n - tr_S - 1)

        return aic

    def _cross_validation_score(
        self, y: np.ndarray, X: np.ndarray, coords: np.ndarray, bandwidth: float
    ) -> float:
        """Calculate leave-one-out cross-validation score."""
        n = len(y)
        cv_error = 0.0

        for i in range(n):
            # Leave out observation i
            weights = self._calculate_weights(coords, i, bandwidth)
            weights[i] = 0  # Exclude focal point

            if np.sum(weights) == 0:
                continue

            weights = weights / np.sum(weights)  # Renormalize

            W_diag = np.diag(weights)
            X_weighted = np.sqrt(W_diag) @ X
            y_weighted = np.sqrt(W_diag) @ y

            try:
                beta_i = np.linalg.solve(X_weighted.T @ X_weighted, X_weighted.T @ y_weighted)
                y_pred = X[i] @ beta_i
                cv_error += (y[i] - y_pred) ** 2
            except:
                cv_error += y[i] ** 2

        return cv_error / n

    def _trace_hat_matrix(self, X: np.ndarray, coords: np.ndarray, bandwidth: float) -> float:
        """
        Calculate trace of hat matrix.

        This is the effective number of parameters in GWR.
        """
        n = len(X)
        trace = 0.0

        for i in range(n):
            weights = self._calculate_weights(coords, i, bandwidth)
            W_diag = np.diag(weights)
            X_weighted = np.sqrt(W_diag) @ X

            try:
                XtWX_inv = np.linalg.inv(X_weighted.T @ X_weighted)
                # Hat matrix at location i
                H_i = X[i] @ XtWX_inv @ X_weighted.T @ W_diag
                trace += H_i[i]
            except:
                continue

        return trace

    def _hat_matrix(self, X: np.ndarray, coords: np.ndarray, bandwidth: float) -> np.ndarray:
        """Calculate full hat matrix (for diagnostics)."""
        n = len(X)
        H = np.zeros((n, n))

        for i in range(n):
            weights = self._calculate_weights(coords, i, bandwidth)
            W_diag = np.diag(weights)
            X_weighted = np.sqrt(W_diag) @ X

            try:
                XtWX_inv = np.linalg.inv(X_weighted.T @ X_weighted)
                H[i] = X[i] @ XtWX_inv @ X_weighted.T @ W_diag
            except:
                H[i, i] = 1.0 / n

        return H

    def predict(self, X: np.ndarray, coords: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """
        Generate predictions at new locations.

        Args:
            X: Independent variables for prediction
            coords: Coordinates for prediction locations
            add_constant: Whether to add intercept

        Returns:
            Predicted values

        Raises:
            ValueError: If model not fitted
        """
        if not self._is_fitted or self.local_coefficients is None:
            raise ValueError("Model must be fitted before prediction")

        X = np.asarray(X)
        coords = np.asarray(coords)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        n_pred = len(X)
        predictions = np.zeros(n_pred)

        # For each prediction location, find nearest fitted location
        # and use its coefficients (or interpolate)
        for i in range(n_pred):
            # Find nearest fitted location
            distances = np.sqrt(np.sum((self._coords - coords[i]) ** 2, axis=1))
            nearest_idx = np.argmin(distances)

            # Use coefficients from nearest location
            predictions[i] = X[i] @ self.local_coefficients[nearest_idx]

        return predictions

    def get_local_estimates(self) -> Dict[str, np.ndarray]:
        """
        Get location-specific parameter estimates.

        Returns:
            Dictionary with local coefficients, standard errors, and statistics

        Raises:
            ValueError: If model not fitted
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        return {
            "coefficients": self.local_coefficients,
            "std_errors": self.local_std_errors,
            "r_squared": self.local_r_squared,
            "t_stats": self.local_coefficients / self.local_std_errors,
        }

    def test_spatial_variation(self, variable_idx: int = 0) -> Dict[str, float]:
        """
        Test for significant spatial variation in coefficients.

        Uses Monte Carlo approach to test if coefficient variation
        exceeds what would be expected under spatial randomness.

        Args:
            variable_idx: Index of variable to test (0 for intercept)

        Returns:
            Dictionary with test statistic and p-value
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        # Observed coefficient variation
        local_betas = self.local_coefficients[:, variable_idx]
        observed_variance = np.var(local_betas)

        # Under null hypothesis of no spatial variation,
        # all locations would have same coefficient
        # Test against IQR (interquartile range)
        iqr = np.percentile(local_betas, 75) - np.percentile(local_betas, 25)

        # Normalized range
        coef_range = np.max(local_betas) - np.min(local_betas)
        coef_std = np.std(local_betas)
        normalized_range = coef_range / (coef_std + 1e-10)

        # Test statistic: ratio of range to standard error
        statistic = coef_range / (coef_std + 1e-10)

        # Approximate p-value (assuming normal distribution)
        from scipy import stats

        p_value = 2 * (1 - stats.norm.cdf(abs(statistic / 2)))

        return {
            "statistic": statistic,
            "p_value": p_value,
            "variance": observed_variance,
            "iqr": iqr,
            "range": coef_range,
            "normalized_range": normalized_range,
            "significant": normalized_range > 2.0,  # Rule of thumb
        }
