"""
Spatial Error Model (SEM).

Implements spatial autoregressive model with spatially autocorrelated errors.
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


class SpatialError(BaseEconometricModel):
    """
    Spatial Error Model (SEM).

    Estimates spatial autoregressive model with error autocorrelation:
        y = Xβ + u
        u = λWu + ε

    where:
        y: dependent variable
        X: independent variables
        β: regression coefficients
        u: error term with spatial autocorrelation
        W: spatial weights matrix
        λ: spatial error parameter
        ε: i.i.d. error term

    Uses maximum likelihood or GMM estimation.

    Attributes:
        name: Model name
        lambda_: Spatial error parameter
        coefficients: Regression coefficients
        std_errors: Standard errors
        residuals: Model residuals

    Examples:
        >>> from krl_geospatial.weights import QueenWeights
        >>> W = QueenWeights().from_dataframe(gdf).matrix
        >>> sem = SpatialError()
        >>> result = sem.fit(y, X, W)
        >>> print(f"Spatial error (lambda): {result.spatial_params['lambda']:.4f}")
    """

    def __init__(self):
        """Initialize Spatial Error model."""
        super().__init__(name="Spatial Error")
        self.lambda_: Optional[float] = None
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
        Fit Spatial Error model.

        Args:
            y: Dependent variable (n x 1)
            X: Independent variables (n x k)
            W: Row-standardized spatial weights matrix (n x n)
            add_constant: Whether to add intercept
            method: Estimation method ('ml' or 'gmm')

        Returns:
            RegressionResult with fitted parameters

        Raises:
            ValueError: If W is not provided or inputs invalid

        Examples:
            >>> result = sem.fit(y, X, W, method='ml')
            >>> print(f"Lambda: {result.spatial_params['lambda']:.4f}")
        """
        if W is None:
            raise ValueError("Spatial weights matrix W is required for SEM model")

        # Validate inputs
        y, X = self._validate_inputs(y, X, W)

        # Store weights matrix
        self._W = W

        # Add constant if requested
        if add_constant:
            X = np.column_stack([np.ones(len(y)), X])

        n_obs = len(y)
        n_vars = X.shape[1]

        logger.debug(f"Fitting SEM: n={n_obs}, k={n_vars}, method={method}")

        # Estimate using specified method
        if method == "ml":
            self._fit_ml(y, X, W)
        elif method == "gmm":
            self._fit_gmm(y, X, W)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'ml' or 'gmm'")

        # Calculate fitted values and residuals
        fitted_values = X @ self.coefficients
        u = y - fitted_values

        # Spatial residuals: ε = u - λWu
        Wu = W @ u
        self.residuals = u - self.lambda_ * Wu

        # Calculate standard errors
        sigma_squared = np.sum(self.residuals**2) / n_obs

        # Asymptotic variance-covariance matrix
        var_covar = self._calculate_var_covar(y, X, W, sigma_squared)
        std_errors_all = np.sqrt(np.diag(var_covar))

        # Separate lambda and beta standard errors
        lambda_se = std_errors_all[0]
        self.std_errors = std_errors_all[1:]

        # Calculate statistics
        t_stats = self.coefficients / self.std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_obs - n_vars - 1))

        lambda_t_stat = self.lambda_ / lambda_se
        lambda_pvalue = 2 * (1 - stats.t.cdf(np.abs(lambda_t_stat), n_obs - n_vars - 1))

        # Calculate fit statistics
        r_squared, adj_r_squared = self._calculate_fit_statistics(
            y, fitted_values, n_vars + 1  # +1 for lambda
        )

        # Calculate log-likelihood
        log_likelihood = self._log_likelihood(self.lambda_, y, X, W)

        # Calculate information criteria
        aic, bic = self._calculate_information_criteria(log_likelihood, n_obs, n_vars + 1)

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
                "lambda": self.lambda_,
                "lambda_se": lambda_se,
                "lambda_t_stat": lambda_t_stat,
                "lambda_pvalue": lambda_pvalue,
            },
            extra_info={
                "sigma_squared": sigma_squared,
                "var_covar_matrix": var_covar,
                "method": method,
            },
        )

        self._is_fitted = True
        logger.info(f"SEM fitted: λ={self.lambda_:.4f}, R²={r_squared:.4f}")

        return self.result

    def _fit_ml(self, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix) -> None:
        """
        Maximum likelihood estimation.

        Args:
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
        """
        n = len(y)

        # Pre-compute eigenvalues for log-determinant
        if n <= 1000:
            try:
                eigenvalues = np.linalg.eigvals((W @ sparse.eye(n)).toarray())
            except:
                eigenvalues = self._approximate_eigenvalues(W, n)
        else:
            eigenvalues = self._approximate_eigenvalues(W, n)

        # Optimize concentrated log-likelihood
        def neg_log_lik(lam):
            return -self._concentrated_log_likelihood(lam, y, X, W, eigenvalues)

        # Find optimal lambda in (-1, 1)
        result = optimize.minimize_scalar(neg_log_lik, bounds=(-0.99, 0.99), method="bounded")

        self.lambda_ = result.x

        # Estimate beta given lambda
        A = sparse.eye(n) - self.lambda_ * W
        y_star = A @ y
        X_star = A @ X

        # OLS on transformed variables
        XtX = X_star.T @ X_star
        Xty = X_star.T @ y_star

        self.coefficients = np.linalg.solve(XtX, Xty)

    def _fit_gmm(self, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix) -> None:
        """
        Generalized Method of Moments estimation.

        Uses moment conditions based on residual autocorrelation.

        Args:
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
        """
        n = len(y)

        # Initial OLS to get residuals
        XtX = X.T @ X
        Xty = X.T @ y
        beta_ols = np.linalg.solve(XtX, Xty)

        u_ols = y - X @ beta_ols
        Wu_ols = W @ u_ols

        # Initial lambda from moment condition
        # E[u'Wu] = 0
        lambda_init = np.sum(u_ols * Wu_ols) / np.sum(Wu_ols**2)
        lambda_init = np.clip(lambda_init, -0.99, 0.99)

        # GMM objective function
        def gmm_objective(params):
            lam = params[0]

            # Transform variables
            A = sparse.eye(n) - lam * W
            y_star = A @ y
            X_star = A @ X

            # Estimate beta
            XtX_star = X_star.T @ X_star
            Xty_star = X_star.T @ y_star

            try:
                beta = np.linalg.solve(XtX_star, Xty_star)
            except np.linalg.LinAlgError:
                return 1e10

            # Calculate residuals
            u = y - X @ beta
            Wu = W @ u

            # Moment conditions
            m1 = np.sum(u * Wu) / n
            m2 = np.sum(Wu**2) / n - np.sum(u**2) / n

            # GMM objective: minimize weighted sum of squared moments
            return m1**2 + m2**2

        # Optimize
        result = optimize.minimize(
            gmm_objective, x0=[lambda_init], bounds=[(-0.99, 0.99)], method="L-BFGS-B"
        )

        self.lambda_ = result.x[0]

        # Final beta estimate
        A = sparse.eye(n) - self.lambda_ * W
        y_star = A @ y
        X_star = A @ X

        XtX = X_star.T @ X_star
        Xty = X_star.T @ y_star

        self.coefficients = np.linalg.solve(XtX, Xty)

    def _concentrated_log_likelihood(
        self,
        lam: float,
        y: np.ndarray,
        X: np.ndarray,
        W: sparse.csr_matrix,
        eigenvalues: np.ndarray,
    ) -> float:
        """
        Calculate concentrated log-likelihood.

        Args:
            lam: Spatial error parameter
            y: Dependent variable
            X: Independent variables
            W: Spatial weights matrix
            eigenvalues: Pre-computed eigenvalues

        Returns:
            Concentrated log-likelihood value
        """
        n = len(y)

        # Transform variables
        A = sparse.eye(n) - lam * W
        y_star = A @ y
        X_star = A @ X

        # Estimate beta
        XtX = X_star.T @ X_star
        Xty = X_star.T @ y_star

        try:
            beta = np.linalg.solve(XtX, Xty)
        except np.linalg.LinAlgError:
            return -1e10

        # Calculate residuals and sigma squared
        residuals = y_star - X_star @ beta
        sigma_squared = np.sum(residuals**2) / n

        # Log-determinant term
        log_det = np.sum(np.log(np.abs(1 - lam * eigenvalues)))

        # Concentrated log-likelihood
        log_lik = -0.5 * n * (np.log(2 * np.pi) + np.log(sigma_squared)) + log_det

        return log_lik

    def _log_likelihood(
        self, lam: float, y: np.ndarray, X: np.ndarray, W: sparse.csr_matrix
    ) -> float:
        """Calculate full log-likelihood."""
        n = len(y)

        A = sparse.eye(n) - lam * W
        y_star = A @ y
        X_star = A @ X

        residuals = y_star - X_star @ self.coefficients
        sigma_squared = np.sum(residuals**2) / n

        # Approximate log-determinant
        if n <= 1000:
            try:
                log_det = np.log(np.abs(np.linalg.det(A.toarray())))
            except:
                eigenvalues = self._approximate_eigenvalues(W, n)
                log_det = np.sum(np.log(np.abs(1 - lam * eigenvalues)))
        else:
            eigenvalues = self._approximate_eigenvalues(W, n)
            log_det = np.sum(np.log(np.abs(1 - lam * eigenvalues)))

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
            k_use = min(k, n - 2)
            eigenvalues, _ = eigs(W, k=k_use, which="LM")
            return np.real(eigenvalues)
        except:
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

        # Variance of lambda
        var_lambda = sigma_squared / n

        # Transform X
        A = sparse.eye(n) - self.lambda_ * W
        X_star = A @ X

        # Variance of beta
        XtX = X_star.T @ X_star
        var_beta = sigma_squared * np.linalg.inv(XtX)

        # Combined variance-covariance (simplified)
        var_covar = np.zeros((n_vars + 1, n_vars + 1))
        var_covar[0, 0] = var_lambda
        var_covar[1:, 1:] = var_beta

        return var_covar

    def predict(self, X: np.ndarray, add_constant: bool = True) -> np.ndarray:
        """
        Generate predictions.

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

        # Direct prediction (error term assumed to be zero for new observations)
        return X @ self.coefficients
