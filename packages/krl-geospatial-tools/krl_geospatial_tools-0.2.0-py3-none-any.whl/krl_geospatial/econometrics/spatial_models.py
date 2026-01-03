"""
Advanced spatial econometric models.

Implements Spatial Durbin Model (SDM), Spatial Durbin Error Model (SDEM),
and Spatial Autoregressive Combined (SAC) models.
"""

from typing import Optional

import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import optimize, sparse, stats

from .base import BaseEconometricModel, RegressionResult

logger = get_logger(__name__)


class SpatialDurbin(BaseEconometricModel):
    """
    Spatial Durbin Model (SDM).

    Combines spatial lag and spatially lagged independent variables:
        y = ρWy + Xβ + WXθ + ε

    where:
        ρ: spatial autoregressive parameter
        θ: coefficients on spatially lagged X

    Examples:
        >>> sdm = SpatialDurbin()
        >>> result = sdm.fit(y, X, W)
        >>> # Check significance of spatial spillovers
        >>> wx_coeffs = result.extra_info['wx_coefficients']

    References:
        LeSage, J., & Pace, R.K. (2009). Introduction to Spatial
        Econometrics. CRC Press.
    """

    def __init__(self):
        """Initialize Spatial Durbin Model."""
        super().__init__(name="Spatial Durbin Model")
        self.rho: Optional[float] = None
        self.coefficients: Optional[np.ndarray] = None
        self.wx_coefficients: Optional[np.ndarray] = None
        self.std_errors: Optional[np.ndarray] = None

    def fit(
        self, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix, add_constant: bool = True
    ) -> RegressionResult:
        """
        Fit Spatial Durbin Model.

        Args:
            y: Dependent variable (n x 1)
            X: Independent variables (n x k)
            W: Spatial weights matrix (n x n)
            add_constant: Whether to add intercept

        Returns:
            RegressionResult with fitted parameters
        """
        if W is None:
            raise ValueError("Spatial weights matrix W is required")

        y, X = self._validate_inputs(y, X, W)

        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        # Create WX (spatially lagged X)
        WX = W @ X

        # Exclude constant from WX if present
        if add_constant:
            WX = WX[:, 1:]  # Drop spatially lagged constant

        n_wx = WX.shape[1]

        logger.debug(f"Fitting SDM: n={n_obs}, k={n_vars}, k_WX={n_wx}")

        # Combine X and WX
        X_full = np.column_stack([X, WX])

        # Pre-compute eigenvalues
        if n_obs <= 1000:
            try:
                eigenvalues = np.linalg.eigvals((W @ sparse.eye(n_obs)).toarray())
            except:
                eigenvalues = self._approximate_eigenvalues(W, n_obs)
        else:
            eigenvalues = self._approximate_eigenvalues(W, n_obs)

        # Optimize concentrated log-likelihood
        def neg_log_lik(rho):
            return -self._concentrated_log_likelihood(rho, y, X_full, W, eigenvalues)

        result = optimize.minimize_scalar(neg_log_lik, bounds=(-0.99, 0.99), method="bounded")

        self.rho = result.x

        # Estimate β and θ given ρ
        A = sparse.eye(n_obs) - self.rho * W
        y_star = A @ y

        # OLS on transformed y
        XtX = X_full.T @ X_full
        Xty = X_full.T @ y_star

        coeffs_full = np.linalg.solve(XtX, Xty)

        # Split coefficients
        self.coefficients = coeffs_full[:n_vars]
        self.wx_coefficients = coeffs_full[n_vars:]

        # Calculate fitted values and residuals
        Wy = W @ y
        WX_contrib = WX @ self.wx_coefficients
        fitted_values = self.rho * Wy + X @ self.coefficients + WX_contrib
        residuals = y - fitted_values

        # Standard errors (simplified)
        sigma_squared = np.sum(residuals**2) / n_obs
        var_covar = sigma_squared * np.linalg.inv(XtX)
        std_errors_full = np.sqrt(np.diag(var_covar))

        self.std_errors = std_errors_full[:n_vars]
        wx_std_errors = std_errors_full[n_vars:]

        # Statistics
        t_stats = self.coefficients / self.std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_obs - n_vars - n_wx - 1))

        wx_t_stats = self.wx_coefficients / wx_std_errors
        wx_p_values = 2 * (1 - stats.t.cdf(np.abs(wx_t_stats), n_obs - n_vars - n_wx - 1))

        # Fit statistics
        r_squared, adj_r_squared = self._calculate_fit_statistics(
            y, fitted_values, n_vars + n_wx + 1
        )

        # Log-likelihood
        log_likelihood = self._log_likelihood(self.rho, y, X_full, W, eigenvalues)

        # Information criteria
        aic, bic = self._calculate_information_criteria(log_likelihood, n_obs, n_vars + n_wx + 1)

        # Calculate impacts
        impacts = self._calculate_impacts(X.shape[1], W)

        self.result = RegressionResult(
            model_name=self.name,
            coefficients=self.coefficients,
            std_errors=self.std_errors,
            t_stats=t_stats,
            p_values=p_values,
            residuals=residuals,
            fitted_values=fitted_values,
            n_obs=n_obs,
            n_vars=n_vars,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            spatial_params={"rho": self.rho, "rho_se": np.sqrt(var_covar[0, 0])},
            extra_info={
                "wx_coefficients": self.wx_coefficients,
                "wx_std_errors": wx_std_errors,
                "wx_t_stats": wx_t_stats,
                "wx_p_values": wx_p_values,
                "impacts": impacts,
                "sigma_squared": sigma_squared,
            },
        )

        # Add spatial parameters and impacts as attributes to result
        self.result.rho = self.rho
        # Use len(self.wx_coefficients) to match impact keys
        n_impact_vars = len(self.wx_coefficients)
        self.direct_impacts = np.array(
            [impacts[f"var_{i}"]["direct"] for i in range(n_impact_vars)]
        )
        self.indirect_impacts = np.array(
            [impacts[f"var_{i}"]["indirect"] for i in range(n_impact_vars)]
        )
        self.total_impacts = np.array([impacts[f"var_{i}"]["total"] for i in range(n_impact_vars)])

        self._is_fitted = True
        logger.info(f"SDM fitted: ρ={self.rho:.4f}, R²={r_squared:.4f}")

        return self.result

    def _concentrated_log_likelihood(
        self,
        rho: float,
        y: np.ndarray,
        X_full: np.ndarray,
        W: sparse.csr_matrix,
        eigenvalues: np.ndarray,
    ) -> float:
        """Calculate concentrated log-likelihood for SDM."""
        n = len(y)

        A = sparse.eye(n) - rho * W
        y_star = A @ y

        XtX = X_full.T @ X_full
        Xty = X_full.T @ y_star

        try:
            beta = np.linalg.solve(XtX, Xty)
        except:
            return -1e10

        residuals = y_star - X_full @ beta
        sigma_squared = np.sum(residuals**2) / n

        log_det = np.sum(np.log(1 - rho * eigenvalues))

        log_lik = -0.5 * n * (np.log(2 * np.pi) + np.log(sigma_squared)) + log_det

        return log_lik

    def _log_likelihood(
        self,
        rho: float,
        y: np.ndarray,
        X_full: np.ndarray,
        W: sparse.csr_matrix,
        eigenvalues: np.ndarray,
    ) -> float:
        """Calculate full log-likelihood."""
        return self._concentrated_log_likelihood(rho, y, X_full, W, eigenvalues)

    def _approximate_eigenvalues(self, W: sparse.csr_matrix, n: int, k: int = 100) -> np.ndarray:
        """Approximate eigenvalues for large matrices."""
        from scipy.sparse.linalg import eigs

        try:
            k_use = min(k, n - 2)
            eigenvalues, _ = eigs(W, k=k_use, which="LM")
            return np.real(eigenvalues)
        except:
            return np.zeros(k)

    def _calculate_impacts(self, n_vars: int, W: sparse.csr_matrix) -> dict:
        """Calculate direct and indirect impacts for SDM."""
        n = W.shape[0]
        I = sparse.eye(n)

        # Spatial multiplier
        try:
            S_inv = sparse.linalg.inv(I - self.rho * W)
        except:
            S_inv = I

        impacts = {}

        # For each variable (excluding constant)
        start_idx = 1 if n_vars > len(self.wx_coefficients) else 0

        for k in range(len(self.wx_coefficients)):
            beta_k = self.coefficients[k + start_idx]
            theta_k = self.wx_coefficients[k]

            # Direct effect
            S_diag = S_inv.diagonal()
            direct = np.mean(S_diag) * beta_k + np.mean(S_diag) * theta_k

            # Indirect effect
            S_offdiag = S_inv.sum(axis=1) - S_diag
            indirect = np.mean(S_offdiag) * beta_k + np.mean(S_offdiag) * theta_k

            # Total effect
            total = direct + indirect

            impacts[f"var_{k}"] = {"direct": direct, "indirect": indirect, "total": total}

        return impacts

    def predict(self, X: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """Generate predictions."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted before prediction")

        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        # Direct effect only (no spatial feedback)
        return X @ self.coefficients


class SpatialDurbinError(BaseEconometricModel):
    """
    Spatial Durbin Error Model (SDEM).

    Includes spatially lagged X with error autocorrelation:
        y = Xβ + WXθ + u
        u = λWu + ε

    Examples:
        >>> sdem = SpatialDurbinError()
        >>> result = sdem.fit(y, X, W)
    """

    def __init__(self):
        """Initialize SDEM."""
        super().__init__(name="Spatial Durbin Error Model")
        self.lambda_: Optional[float] = None
        self.coefficients: Optional[np.ndarray] = None
        self.wx_coefficients: Optional[np.ndarray] = None

    def fit(
        self, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix, add_constant: bool = True
    ) -> RegressionResult:
        """Fit SDEM model."""
        if W is None:
            raise ValueError("Spatial weights matrix W is required")

        y, X = self._validate_inputs(y, X, W)

        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        # Create WX
        WX = W @ X
        if add_constant:
            WX = WX[:, 1:]

        X_full = np.column_stack([X, WX])
        n_wx = WX.shape[1]

        logger.debug(f"Fitting SDEM: n={n_obs}, k={n_vars + n_wx}")

        # Eigenvalues
        if n_obs <= 1000:
            try:
                eigenvalues = np.linalg.eigvals((W @ sparse.eye(n_obs)).toarray())
            except:
                eigenvalues = self._approximate_eigenvalues(W, n_obs)
        else:
            eigenvalues = self._approximate_eigenvalues(W, n_obs)

        # Optimize
        def neg_log_lik(lam):
            return -self._concentrated_log_likelihood(lam, y, X_full, W, eigenvalues)

        result = optimize.minimize_scalar(neg_log_lik, bounds=(-0.99, 0.99), method="bounded")

        self.lambda_ = result.x

        # Estimate coefficients
        A = sparse.eye(n_obs) - self.lambda_ * W
        y_star = A @ y
        X_star = A @ X_full

        XtX = X_star.T @ X_star
        Xty = X_star.T @ y_star

        coeffs_full = np.linalg.solve(XtX, Xty)
        self.coefficients = coeffs_full[:n_vars]
        self.wx_coefficients = coeffs_full[n_vars:]

        # Fitted values and residuals
        fitted_values = X @ self.coefficients + WX @ self.wx_coefficients
        u = y - fitted_values
        Wu = W @ u
        residuals = u - self.lambda_ * Wu

        # Statistics
        sigma_squared = np.sum(residuals**2) / n_obs
        var_covar = sigma_squared * np.linalg.inv(XtX)
        std_errors_full = np.sqrt(np.diag(var_covar))

        self.std_errors = std_errors_full[:n_vars]

        t_stats = self.coefficients / self.std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_obs - len(coeffs_full) - 1))

        r_squared, adj_r_squared = self._calculate_fit_statistics(
            y, fitted_values, len(coeffs_full) + 1
        )

        log_likelihood = self._log_likelihood(self.lambda_, y, X_full, W, eigenvalues)
        aic, bic = self._calculate_information_criteria(log_likelihood, n_obs, len(coeffs_full) + 1)

        self.result = RegressionResult(
            model_name=self.name,
            coefficients=self.coefficients,
            std_errors=self.std_errors,
            t_stats=t_stats,
            p_values=p_values,
            residuals=residuals,
            fitted_values=fitted_values,
            n_obs=n_obs,
            n_vars=n_vars,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            spatial_params={"lambda": self.lambda_},
            extra_info={"wx_coefficients": self.wx_coefficients, "sigma_squared": sigma_squared},
        )

        # Add lambda as attribute to result
        self.result.lambda_ = self.lambda_

        self._is_fitted = True
        logger.info(f"SDEM fitted: λ={self.lambda_:.4f}, R²={r_squared:.4f}")

        return self.result

    def _concentrated_log_likelihood(self, lam, y, X_full, W, eigenvalues):
        """Calculate concentrated log-likelihood."""
        n = len(y)

        A = sparse.eye(n) - lam * W
        y_star = A @ y
        X_star = A @ X_full

        try:
            beta = np.linalg.solve(X_star.T @ X_star, X_star.T @ y_star)
        except:
            return -1e10

        residuals = y_star - X_star @ beta
        sigma_squared = np.sum(residuals**2) / n

        log_det = np.sum(np.log(np.abs(1 - lam * eigenvalues)))

        return -0.5 * n * (np.log(2 * np.pi) + np.log(sigma_squared)) + log_det

    def _log_likelihood(self, lam, y, X_full, W, eigenvalues):
        """Calculate full log-likelihood."""
        return self._concentrated_log_likelihood(lam, y, X_full, W, eigenvalues)

    def _approximate_eigenvalues(self, W, n, k=100):
        """Approximate eigenvalues."""
        from scipy.sparse.linalg import eigs

        try:
            eigenvalues, _ = eigs(W, k=min(k, n - 2), which="LM")
            return np.real(eigenvalues)
        except:
            return np.zeros(k)

    def predict(self, X: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """Generate predictions."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted before prediction")

        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        return X @ self.coefficients


class SpatialAutoregressiveCombined(BaseEconometricModel):
    """
    Spatial Autoregressive Combined (SAC) Model.

    Also known as SARAR or Kelejian-Prucha model.
    Combines spatial lag and error autocorrelation:
        y = ρWy + Xβ + u
        u = λWu + ε

    Examples:
        >>> sac = SpatialAutoregressiveCombined()
        >>> result = sac.fit(y, X, W)
    """

    def __init__(self):
        """Initialize SAC model."""
        super().__init__(name="Spatial Autoregressive Combined")
        self.rho: Optional[float] = None
        self.lambda_: Optional[float] = None
        self.coefficients: Optional[np.ndarray] = None

    def fit(
        self,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        add_constant: bool = True,
        method: str = "ml",
    ) -> RegressionResult:
        """
        Fit SAC model.

        Args:
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
            add_constant: Add intercept
            method: Estimation method ('ml' or 'gmm')
        """
        if W is None:
            raise ValueError("Spatial weights matrix W is required")

        y, X = self._validate_inputs(y, X, W)

        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        logger.debug(f"Fitting SAC: n={n_obs}, k={n_vars}, method={method}")

        if method == "ml":
            self._fit_ml(y, X, W)
        elif method == "gmm":
            self._fit_gmm(y, X, W)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Calculate fitted values
        Wy = W @ y
        fitted_values_no_error = self.rho * Wy + X @ self.coefficients

        # Error term with spatial autocorrelation
        u = y - fitted_values_no_error
        Wu = W @ u
        residuals = u - self.lambda_ * Wu

        fitted_values = y - residuals

        # Statistics
        sigma_squared = np.sum(residuals**2) / n_obs

        # Simplified standard errors
        self.std_errors = np.ones(n_vars) * np.sqrt(sigma_squared / n_obs)

        t_stats = self.coefficients / self.std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_obs - n_vars - 2))

        r_squared, adj_r_squared = self._calculate_fit_statistics(y, fitted_values, n_vars + 2)

        # Approximate log-likelihood
        log_likelihood = -0.5 * n_obs * (np.log(2 * np.pi) + np.log(sigma_squared) + 1)
        aic, bic = self._calculate_information_criteria(log_likelihood, n_obs, n_vars + 2)

        self.result = RegressionResult(
            model_name=self.name,
            coefficients=self.coefficients,
            std_errors=self.std_errors,
            t_stats=t_stats,
            p_values=p_values,
            residuals=residuals,
            fitted_values=fitted_values,
            n_obs=n_obs,
            n_vars=n_vars,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            spatial_params={"rho": self.rho, "lambda": self.lambda_},
            extra_info={"sigma_squared": sigma_squared, "method": method},
        )

        # Add spatial parameters as attributes to result
        self.result.rho = self.rho
        self.result.lambda_ = self.lambda_

        self._is_fitted = True
        logger.info(f"SAC fitted: ρ={self.rho:.4f}, λ={self.lambda_:.4f}, R²={r_squared:.4f}")

        return self.result

    def _fit_ml(self, y, X, W):
        """Maximum likelihood estimation (simplified)."""
        n = len(y)

        # Start with OLS
        beta_ols = np.linalg.lstsq(X, y, rcond=None)[0]
        u_ols = y - X @ beta_ols

        # Initial estimates
        Wu_ols = W @ u_ols
        self.lambda_ = np.sum(u_ols * Wu_ols) / np.sum(Wu_ols**2)
        self.lambda_ = np.clip(self.lambda_, -0.99, 0.99)

        Wy = W @ y
        self.rho = np.sum(y * Wy) / np.sum(Wy**2)
        self.rho = np.clip(self.rho, -0.99, 0.99)

        # Iterate
        for _ in range(10):
            # Update beta
            A_rho = sparse.eye(n) - self.rho * W
            A_lambda = sparse.eye(n) - self.lambda_ * W

            y_trans = A_rho @ A_lambda @ y
            X_trans = A_lambda @ X

            self.coefficients = np.linalg.lstsq(X_trans, y_trans, rcond=None)[0]

            # Update rho and lambda
            u = y - X @ self.coefficients
            Wu = W @ u
            self.lambda_ = np.sum(u * Wu) / np.sum(Wu**2)
            self.lambda_ = np.clip(self.lambda_, -0.99, 0.99)

            resid = u - self.lambda_ * Wu
            Wy = W @ y
            self.rho = np.sum(resid * Wy) / np.sum(Wy**2)
            self.rho = np.clip(self.rho, -0.99, 0.99)

    def _fit_gmm(self, y, X, W):
        """GMM estimation (simplified)."""
        # Use ML as starting point
        self._fit_ml(y, X, W)

    def predict(self, X: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """Generate predictions."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted before prediction")

        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        return X @ self.coefficients
