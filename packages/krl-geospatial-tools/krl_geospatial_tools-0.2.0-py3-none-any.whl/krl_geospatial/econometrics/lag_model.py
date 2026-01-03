"""
Spatial Lag Model (SAR).

Implements spatial autoregressive model with endogenous spatial lag.
"""

from typing import Optional, Tuple

import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import optimize, sparse, stats

from .base import BaseEconometricModel, RegressionResult

logger = get_logger(__name__)


class SpatialLag(BaseEconometricModel):
    """
    Spatial Lag Model (SAR).

    Estimates spatial autoregressive model:
        y = ρWy + Xβ + ε

    where:
        y: dependent variable
        W: spatial weights matrix
        ρ: spatial autoregressive parameter
        X: independent variables
        β: regression coefficients
        ε: error term

    Uses maximum likelihood estimation with concentrated log-likelihood.

    Attributes:
        name: Model name
        rho: Spatial autoregressive parameter
        coefficients: Regression coefficients
        std_errors: Standard errors
        residuals: Model residuals

    Examples:
        >>> from krl_geospatial.weights import QueenWeights
        >>> W = QueenWeights().from_dataframe(gdf).matrix
        >>> sar = SpatialLag()
        >>> result = sar.fit(y, X, W)
        >>> print(f"Spatial lag (rho): {result.spatial_params['rho']:.4f}")
    """

    def __init__(self):
        """Initialize Spatial Lag model."""
        super().__init__(name="Spatial Lag")
        self.rho: Optional[float] = None
        self.coefficients: Optional[np.ndarray] = None
        self.std_errors: Optional[np.ndarray] = None
        self.residuals: Optional[np.ndarray] = None
        self._W: Optional[sparse.csr_matrix] = None

    def fit(
        self,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        add_constant: bool = True,
        method: str = "ml",
    ) -> RegressionResult:
        """
        Fit Spatial Lag model using maximum likelihood.

        Args:
            y: Dependent variable (n x 1)
            X: Independent variables (n x k)
            W: Row-standardized spatial weights matrix (n x n)
            add_constant: Whether to add intercept
            method: Estimation method ('ml' for maximum likelihood)

        Returns:
            RegressionResult with fitted parameters

        Raises:
            ValueError: If W is not provided or inputs invalid

        Examples:
            >>> result = sar.fit(y, X, W)
            >>> impacts = result.extra_info['impacts']
            >>> print(f"Direct effect: {impacts['direct']:.4f}")
        """
        if W is None:
            raise ValueError("Spatial weights matrix W is required for SAR model")

        # Validate inputs
        y, X = self._validate_inputs(y, X, W)

        # Store weights matrix
        self._W = W

        # Add constant if requested
        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        logger.debug(f"Fitting SAR: n={n_obs}, k={n_vars}")

        # Estimate using maximum likelihood
        if method == "ml":
            self._fit_ml(y, X, W)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Calculate fitted values and residuals
        Wy = W @ y
        fitted_values = self.rho * Wy + X @ self.coefficients
        self.residuals = y - fitted_values

        # Calculate standard errors
        sigma_squared = np.sum(self.residuals**2) / n_obs

        # Asymptotic variance-covariance matrix
        # This is simplified; full calculation requires Hessian
        var_covar = self._calculate_var_covar(y, X, W, sigma_squared)
        std_errors_all = np.sqrt(np.diag(var_covar))

        # Separate rho and beta standard errors
        rho_se = std_errors_all[0]
        self.std_errors = std_errors_all[1:]

        # Calculate statistics
        t_stats = self.coefficients / self.std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_obs - n_vars - 1))

        rho_t_stat = self.rho / rho_se
        rho_pvalue = 2 * (1 - stats.t.cdf(np.abs(rho_t_stat), n_obs - n_vars - 1))

        # Calculate fit statistics
        r_squared, adj_r_squared = self._calculate_fit_statistics(
            y, fitted_values, n_vars + 1  # +1 for rho
        )

        # Calculate log-likelihood
        log_likelihood = self._log_likelihood(self.rho, y, X, W)

        # Calculate information criteria
        aic, bic = self._calculate_information_criteria(log_likelihood, n_obs, n_vars + 1)

        # Calculate spatial multiplier effects
        impacts = self._calculate_impacts(X, W)

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
            spatial_params={
                "rho": self.rho,
                "rho_se": rho_se,
                "rho_t_stat": rho_t_stat,
                "rho_pvalue": rho_pvalue,
            },
            extra_info={
                "sigma_squared": sigma_squared,
                "var_covar_matrix": var_covar,
                "impacts": impacts,
            },
        )

        # Add rho as attribute to result
        self.result.rho = self.rho

        self._is_fitted = True
        logger.info(f"SAR fitted: ρ={self.rho:.4f}, R²={r_squared:.4f}")

        return self.result

    def _fit_ml(self, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix) -> None:
        """
        Maximum likelihood estimation using concentrated likelihood.

        Args:
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
        """
        n = len(y)

        # Pre-compute eigenvalues for log-determinant
        # For large matrices, use approximation
        if n <= 1000:
            try:
                eigenvalues = np.linalg.eigvals((W @ sparse.eye(n)).toarray())
            except:
                # Fallback to approximation
                eigenvalues = self._approximate_eigenvalues(W, n)
        else:
            eigenvalues = self._approximate_eigenvalues(W, n)

        # Optimize concentrated log-likelihood
        def neg_log_lik(rho):
            return -self._concentrated_log_likelihood(rho, y, X, W, eigenvalues)

        # Find optimal rho in (-1, 1)
        result = optimize.minimize_scalar(neg_log_lik, bounds=(-0.99, 0.99), method="bounded")

        self.rho = result.x

        # Estimate beta given rho
        A = sparse.eye(n) - self.rho * W
        y_star = A @ y
        X_star = X  # No transformation needed for X in SAR

        # OLS on transformed variables
        XtX = X_star.T @ X_star
        Xty = X_star.T @ y_star

        self.coefficients = np.linalg.solve(XtX, Xty)

    def _concentrated_log_likelihood(
        self,
        rho: float,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        eigenvalues: np.ndarray,
    ) -> float:
        """
        Calculate concentrated log-likelihood.

        Args:
            rho: Spatial parameter
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
            eigenvalues: Pre-computed eigenvalues

        Returns:
            Concentrated log-likelihood value
        """
        n = len(y)

        # Transform y
        A = sparse.eye(n) - rho * W
        y_star = A @ y

        # Estimate beta
        XtX = X.T @ X
        Xty = X.T @ y_star
        beta = np.linalg.solve(XtX, Xty)

        # Calculate residuals and sigma squared
        residuals = y_star - X @ beta
        sigma_squared = np.sum(residuals**2) / n

        # Log-determinant term
        log_det = np.sum(np.log(1 - rho * eigenvalues))

        # Concentrated log-likelihood
        log_lik = -0.5 * n * (np.log(2 * np.pi) + np.log(sigma_squared)) + log_det

        return log_lik

    def _log_likelihood(
        self, rho: float, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix
    ) -> float:
        """Calculate full log-likelihood."""
        n = len(y)

        A = sparse.eye(n) - rho * W
        y_star = A @ y

        residuals = y_star - X @ self.coefficients
        sigma_squared = np.sum(residuals**2) / n

        # Approximate log-determinant
        if n <= 1000:
            try:
                log_det = np.log(np.linalg.det(A.toarray()))
            except:
                eigenvalues = self._approximate_eigenvalues(W, n)
                log_det = np.sum(np.log(1 - rho * eigenvalues))
        else:
            eigenvalues = self._approximate_eigenvalues(W, n)
            log_det = np.sum(np.log(1 - rho * eigenvalues))

        log_lik = -0.5 * n * (np.log(2 * np.pi) + np.log(sigma_squared)) + log_det

        return log_lik

    def _approximate_eigenvalues(self, W: sparse.csr_matrix, n: int, k: int = 100) -> np.ndarray:
        """
        Approximate eigenvalues using sparse methods.

        Args:
            W: Spatial weights matrix
            n: Matrix dimension
            k: Number of eigenvalues to compute

        Returns:
            Approximate eigenvalues
        """
        from scipy.sparse.linalg import eigs

        try:
            # Compute largest magnitude eigenvalues
            k_use = min(k, n - 2)
            eigenvalues, _ = eigs(W, k=k_use, which="LM")
            return np.real(eigenvalues)
        except:
            # Fallback to zero if computation fails
            logger.warning("Eigenvalue computation failed, using approximation")
            return np.zeros(k)

    def _calculate_var_covar(
        self, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix, sigma_squared: float
    ) -> np.ndarray:
        """
        Calculate variance-covariance matrix.

        Simplified asymptotic variance calculation.
        """
        n = len(y)
        n_vars = X.shape[1]

        # This is a simplified approximation
        # Full calculation requires numerical Hessian

        # Variance of rho
        var_rho = sigma_squared / n

        # Variance of beta
        XtX = X.T @ X
        var_beta = sigma_squared * np.linalg.inv(XtX)

        # Combined variance-covariance (simplified)
        var_covar = np.zeros((n_vars + 1, n_vars + 1))
        var_covar[0, 0] = var_rho
        var_covar[1:, 1:] = var_beta

        return var_covar

    def _calculate_impacts(self, X: np.ndarray, W: sparse.csr_matrix) -> dict:
        """
        Calculate direct, indirect, and total impacts.

        Args:
            X: Independent variables
            W: Spatial weights matrix

        Returns:
            Dictionary with impact measures
        """
        n = X.shape[0]

        # Spatial multiplier: S = (I - ρW)^(-1)
        I = sparse.eye(n)
        S = sparse.linalg.inv(I - self.rho * W)

        # Average impacts for each variable
        impacts = {}

        for k in range(len(self.coefficients)):
            beta_k = self.coefficients[k]

            # Direct impact: average diagonal of S * beta
            S_diag = S.diagonal()
            direct = np.mean(S_diag) * beta_k

            # Total impact: average row sum of S * beta
            S_rowsum = np.array(S.sum(axis=1)).flatten()
            total = np.mean(S_rowsum) * beta_k

            # Indirect impact
            indirect = total - direct

            impacts[f"var_{k}"] = {"direct": direct, "indirect": indirect, "total": total}

        # Average across all variables
        impacts["average"] = {
            "direct": np.mean([v["direct"] for v in impacts.values()]),
            "indirect": np.mean([v["indirect"] for v in impacts.values()]),
            "total": np.mean([v["total"] for v in impacts.values()]),
        }

        return impacts

    def predict(self, X: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """
        Generate predictions.

        Note: Predictions assume no spatial feedback (uses mean spatial effect).

        Args:
            X: Independent variables
            add_constant: Whether to add intercept

        Returns:
            Predicted values

        Raises:
            ValueError: If model not fitted
        """
        if not self._is_fitted or self.coefficients is None:
            raise ValueError("Model must be fitted before prediction")

        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        # Direct effect only (no spatial feedback for new observations)
        return X @ self.coefficients
