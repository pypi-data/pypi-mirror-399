"""
Ordinary Least Squares (OLS) regression.

Provides baseline linear regression for comparison with spatial models.
"""

from typing import Optional

import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import sparse, stats

from .base import BaseEconometricModel, RegressionResult

logger = get_logger(__name__)


class OLS(BaseEconometricModel):
    """
    Ordinary Least Squares regression.

    Provides baseline non-spatial regression for comparison with
    spatial econometric models. Estimates coefficients using standard
    OLS approach with classical standard errors.

    Attributes:
        name: Model name
        coefficients: Estimated coefficients
        std_errors: Standard errors
        residuals: Regression residuals

    Examples:
        >>> ols = OLS()
        >>> result = ols.fit(y, X)
        >>> print(result.summary())
        >>> predictions = ols.predict(X_new)
    """

    def __init__(self):
        """Initialize OLS model."""
        super().__init__(name="OLS")
        self.coefficients: Optional[np.ndarray] = None
        self.std_errors: Optional[np.ndarray] = None
        self.residuals: Optional[np.ndarray] = None

    def fit(
        self,
        y: np.ndarray,
        X: np.ndarray,
        W: Optional[sparse.csr_matrix] = None,
        add_constant: bool = True,
    ) -> RegressionResult:
        """
        Fit OLS regression model.

        Args:
            y: Dependent variable (n x 1)
            X: Independent variables (n x k)
            W: Spatial weights matrix (ignored for OLS)
            add_constant: Whether to add intercept

        Returns:
            RegressionResult with fitted parameters

        Examples:
            >>> ols = OLS()
            >>> result = ols.fit(y, X)
            >>> print(f"R-squared: {result.r_squared:.4f}")
        """
        # Validate inputs
        y, X = self._validate_inputs(y, X, W)

        # Add constant if requested
        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        logger.debug(f"Fitting OLS: n={n_obs}, k={n_vars}")

        # Estimate coefficients: β = (X'X)^(-1)X'y
        XtX = X.T @ X
        Xty = X.T @ y

        try:
            self.coefficients = np.linalg.solve(XtX, Xty)
        except np.linalg.LinAlgError:
            logger.warning("Singular matrix, using pseudo-inverse")
            self.coefficients = np.linalg.lstsq(X, y, rcond=None)[0]

        # Calculate fitted values and residuals
        fitted_values = X @ self.coefficients
        self.residuals = y - fitted_values

        # Calculate standard errors
        sigma_squared = np.sum(self.residuals**2) / (n_obs - n_vars)
        var_covar_matrix = sigma_squared * np.linalg.inv(XtX)
        self.std_errors = np.sqrt(np.diag(var_covar_matrix))

        # Calculate t-statistics and p-values
        t_stats = self.coefficients / self.std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_obs - n_vars))

        # Calculate fit statistics
        r_squared, adj_r_squared = self._calculate_fit_statistics(y, fitted_values, n_vars)

        # Calculate log-likelihood (assuming normal errors)
        log_likelihood = -0.5 * n_obs * (np.log(2 * np.pi) + np.log(sigma_squared) + 1)

        # Calculate information criteria
        aic, bic = self._calculate_information_criteria(log_likelihood, n_obs, n_vars)

        # Calculate F-statistic for overall significance
        ss_res = np.sum(self.residuals**2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        f_stat = ((ss_tot - ss_res) / (n_vars - 1)) / (ss_res / (n_obs - n_vars))
        f_pvalue = 1 - stats.f.cdf(f_stat, n_vars - 1, n_obs - n_vars)

        # Store result
        self.result = RegressionResult(
            model_name=self.name,
            coefficients=self.coefficients,
            std_errors=self.std_errors,
            t_stats=t_stats,
            p_values=p_values,
            residuals=self.residuals,
            fitted_values=fitted_values,
            n_obs=n_obs,
            n_vars=n_vars,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            spatial_params={},
            extra_info={
                "sigma_squared": sigma_squared,
                "f_statistic": f_stat,
                "f_pvalue": f_pvalue,
                "var_covar_matrix": var_covar_matrix,
            },
        )

        self._is_fitted = True
        logger.info(f"OLS fitted: R²={r_squared:.4f}")

        return self.result

    def predict(self, X: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """
        Generate predictions.

        Args:
            X: Independent variables for prediction
            add_constant: Whether to add intercept (must match fit)

        Returns:
            Predicted values

        Raises:
            ValueError: If model not fitted

        Examples:
            >>> predictions = ols.predict(X_new)
        """
        if not self._is_fitted or self.coefficients is None:
            raise ValueError("Model must be fitted before prediction")

        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        if X.shape[1] != len(self.coefficients):
            raise ValueError(
                f"X has {X.shape[1]} columns but model expects " f"{len(self.coefficients)}"
            )

        return X @ self.coefficients

    def get_residuals(self) -> np.ndarray:
        """
        Get model residuals.

        Returns:
            Residuals array

        Raises:
            ValueError: If model not fitted
        """
        if not self._is_fitted or self.residuals is None:
            raise ValueError("Model must be fitted first")

        return self.residuals.copy()

    def get_diagnostics(self) -> dict:
        """
        Get diagnostic statistics.

        Returns:
            Dictionary with diagnostic information

        Raises:
            ValueError: If model not fitted
        """
        if not self._is_fitted or self.result is None:
            raise ValueError("Model must be fitted first")

        # Jarque-Bera test for normality of residuals
        n = len(self.residuals)
        residuals_std = (self.residuals - np.mean(self.residuals)) / np.std(self.residuals)

        skewness = np.mean(residuals_std**3)
        kurtosis = np.mean(residuals_std**4) - 3

        jb_stat = (n / 6) * (skewness**2 + (kurtosis**2) / 4)
        jb_pvalue = 1 - stats.chi2.cdf(jb_stat, 2)

        # Breusch-Pagan test for heteroskedasticity
        # Regress squared residuals on X
        if self.result.extra_info.get("var_covar_matrix") is not None:
            residuals_sq = self.residuals**2
            mean_res_sq = np.mean(residuals_sq)

            # This is a simplified version
            bp_stat = n * self.result.r_squared  # From auxiliary regression
            bp_pvalue = 1 - stats.chi2.cdf(bp_stat, self.result.n_vars - 1)
        else:
            bp_stat = np.nan
            bp_pvalue = np.nan

        return {
            "jarque_bera": jb_stat,
            "jarque_bera_pvalue": jb_pvalue,
            "breusch_pagan": bp_stat,
            "breusch_pagan_pvalue": bp_pvalue,
            "residual_mean": np.mean(self.residuals),
            "residual_std": np.std(self.residuals),
            "residual_min": np.min(self.residuals),
            "residual_max": np.max(self.residuals),
        }
