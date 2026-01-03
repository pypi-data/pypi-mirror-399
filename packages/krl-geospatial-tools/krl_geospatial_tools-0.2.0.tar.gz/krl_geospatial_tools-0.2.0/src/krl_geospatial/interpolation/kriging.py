"""
Kriging interpolation methods.

© 2025 KR-Labs. All rights reserved.

References
----------
Cressie, N. (1993). Statistics for spatial data. John Wiley & Sons.
Isaaks, E. H., & Srivastava, R. M. (1989). An introduction to applied
    geostatistics. Oxford University Press.
"""

from typing import Callable, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.linalg import solve
from scipy.optimize import minimize
from scipy.spatial.distance import cdist


class OrdinaryKriging:
    """
    Ordinary kriging interpolation.

    Predicts values at unsampled locations using a weighted average of
    nearby observations, with weights determined by spatial covariance.

    Parameters
    ----------
    variogram_model : {'spherical', 'exponential', 'gaussian', 'linear'}, default='spherical'
        Variogram model to fit
    variogram_parameters : dict, optional
        Parameters for variogram model (sill, range, nugget)
    n_closest : int, optional
        Number of closest points to use for prediction
        If None, uses all points

    Attributes
    ----------
    variogram_params_ : dict
        Fitted variogram parameters
    X_train_ : ndarray
        Training coordinates
    y_train_ : ndarray
        Training values

    Examples
    --------
    >>> from krl_geospatial.interpolation import OrdinaryKriging
    >>>
    >>> kriging = OrdinaryKriging(variogram_model='spherical')
    >>> kriging.fit(train_gdf, 'elevation')
    >>>
    >>> # Predict at new locations
    >>> predictions = kriging.predict(test_gdf)
    >>>
    >>> # Get prediction variance
    >>> predictions, variances = kriging.predict(test_gdf, return_variance=True)
    """

    def __init__(
        self,
        variogram_model: str = "spherical",
        variogram_parameters: Optional[dict] = None,
        n_closest: Optional[int] = None,
    ):
        if variogram_model not in ["spherical", "exponential", "gaussian", "linear"]:
            raise ValueError(f"Invalid variogram model: {variogram_model}")

        self.variogram_model = variogram_model
        self.variogram_parameters = variogram_parameters
        self.n_closest = n_closest

        self.variogram_params_ = None
        self.X_train_ = None
        self.y_train_ = None
        self._variable = None

    def fit(self, gdf, variable: str):
        """
        Fit kriging model.

        Parameters
        ----------
        gdf : GeoDataFrame
            Training data
        variable : str
            Name of variable to interpolate

        Returns
        -------
        self : OrdinaryKriging
            Fitted estimator
        """
        self._variable = variable
        self.X_train_ = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        self.y_train_ = gdf[variable].values

        # Fit variogram if parameters not provided
        if self.variogram_parameters is None:
            self.variogram_params_ = self._fit_variogram()
        else:
            self.variogram_params_ = self.variogram_parameters

        return self

    def _fit_variogram(self):
        """
        Fit variogram model to empirical variogram.
        """
        # Calculate empirical variogram
        distances, semivariances = self._empirical_variogram()

        # Initial parameter guesses
        sill_guess = np.var(self.y_train_)
        range_guess = distances.max() / 3
        nugget_guess = 0.0

        # Fit variogram model
        if self.variogram_model == "spherical":

            def objective(params):
                sill, range_, nugget = params
                predicted = self._spherical_variogram(distances, sill, range_, nugget)
                return np.sum((semivariances - predicted) ** 2)

        elif self.variogram_model == "exponential":

            def objective(params):
                sill, range_, nugget = params
                predicted = self._exponential_variogram(distances, sill, range_, nugget)
                return np.sum((semivariances - predicted) ** 2)

        elif self.variogram_model == "gaussian":

            def objective(params):
                sill, range_, nugget = params
                predicted = self._gaussian_variogram(distances, sill, range_, nugget)
                return np.sum((semivariances - predicted) ** 2)

        else:  # linear

            def objective(params):
                slope, nugget = params
                predicted = self._linear_variogram(distances, slope, nugget)
                return np.sum((semivariances - predicted) ** 2)

            result = minimize(
                objective,
                x0=[sill_guess / range_guess, nugget_guess],
                bounds=[(0, None), (0, sill_guess)],
            )
            return {"slope": result.x[0], "nugget": result.x[1]}

        result = minimize(
            objective,
            x0=[sill_guess, range_guess, nugget_guess],
            bounds=[(0, None), (0, None), (0, sill_guess)],
        )

        return {
            "sill": result.x[0],
            "range": result.x[1],
            "nugget": result.x[2],
        }

    def _empirical_variogram(self, n_lags: int = 15):
        """Calculate empirical variogram."""
        distances = cdist(self.X_train_, self.X_train_)

        # Create lag bins
        max_dist = distances.max() / 2  # Use half max distance
        lag_bins = np.linspace(0, max_dist, n_lags + 1)
        lag_centers = (lag_bins[:-1] + lag_bins[1:]) / 2

        semivariances = np.zeros(n_lags)

        for i in range(n_lags):
            mask = (distances >= lag_bins[i]) & (distances < lag_bins[i + 1])
            pairs = np.where(np.triu(mask, k=1))

            if len(pairs[0]) > 0:
                squared_diffs = (self.y_train_[pairs[0]] - self.y_train_[pairs[1]]) ** 2
                semivariances[i] = squared_diffs.mean() / 2

        return lag_centers, semivariances

    def _spherical_variogram(self, h, sill, range_, nugget):
        """Spherical variogram model."""
        h = np.atleast_1d(h)
        gamma = np.zeros_like(h, dtype=float)
        mask = h > 0
        in_range = mask & (h <= range_)
        gamma[in_range] = nugget + (sill - nugget) * (
            1.5 * h[in_range] / range_ - 0.5 * (h[in_range] / range_) ** 3
        )
        gamma[mask & (h > range_)] = sill
        return gamma.item() if gamma.shape == (1,) else gamma

    def _exponential_variogram(self, h, sill, range_, nugget):
        """Exponential variogram model."""
        h = np.atleast_1d(h)
        gamma = np.zeros_like(h, dtype=float)
        mask = h > 0
        gamma[mask] = nugget + (sill - nugget) * (1 - np.exp(-h[mask] / range_))
        return gamma.item() if gamma.shape == (1,) else gamma

    def _gaussian_variogram(self, h, sill, range_, nugget):
        """Gaussian variogram model."""
        h = np.atleast_1d(h)
        gamma = np.zeros_like(h, dtype=float)
        mask = h > 0
        gamma[mask] = nugget + (sill - nugget) * (1 - np.exp(-((h[mask] / range_) ** 2)))
        return gamma.item() if gamma.shape == (1,) else gamma

    def _linear_variogram(self, h, slope, nugget):
        """Linear variogram model."""
        h = np.atleast_1d(h)
        result = nugget + slope * h
        return result.item() if result.shape == (1,) else result

    def _variogram(self, h):
        """Calculate variogram value at distance h."""
        if self.variogram_model == "spherical":
            return self._spherical_variogram(
                h,
                self.variogram_params_["sill"],
                self.variogram_params_["range"],
                self.variogram_params_["nugget"],
            )
        elif self.variogram_model == "exponential":
            return self._exponential_variogram(
                h,
                self.variogram_params_["sill"],
                self.variogram_params_["range"],
                self.variogram_params_["nugget"],
            )
        elif self.variogram_model == "gaussian":
            return self._gaussian_variogram(
                h,
                self.variogram_params_["sill"],
                self.variogram_params_["range"],
                self.variogram_params_["nugget"],
            )
        else:  # linear
            return self._linear_variogram(
                h, self.variogram_params_["slope"], self.variogram_params_["nugget"]
            )

    def predict(self, gdf, return_variance: bool = False):
        """
        Predict at new locations.

        Parameters
        ----------
        gdf : GeoDataFrame
            Locations to predict at
        return_variance : bool, default=False
            Whether to return prediction variance

        Returns
        -------
        predictions : ndarray
            Predicted values
        variances : ndarray, optional
            Prediction variances (if return_variance=True)
        """
        X_pred = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        n_pred = len(X_pred)
        n_train = len(self.X_train_)

        predictions = np.zeros(n_pred)
        variances = np.zeros(n_pred) if return_variance else None

        for i in range(n_pred):
            # Calculate distances to training points
            distances = np.sqrt(np.sum((self.X_train_ - X_pred[i]) ** 2, axis=1))

            # Use n_closest points if specified
            if self.n_closest is not None and self.n_closest < n_train:
                closest_indices = np.argsort(distances)[: self.n_closest]
                distances_subset = distances[closest_indices]
                y_subset = self.y_train_[closest_indices]
            else:
                distances_subset = distances
                y_subset = self.y_train_

            n_subset = len(distances_subset)

            # Build kriging system
            # Covariance matrix between training points
            C = np.zeros((n_subset + 1, n_subset + 1))
            for j in range(n_subset):
                for k in range(n_subset):
                    dist_jk = np.abs(distances_subset[j] - distances_subset[k]) if j != k else 0
                    if j == k:
                        dist_jk = 0
                    else:
                        # Calculate actual distance between points j and k
                        if self.n_closest is not None and self.n_closest < n_train:
                            j_idx = closest_indices[j]
                            k_idx = closest_indices[k]
                        else:
                            j_idx = j
                            k_idx = k
                        dist_jk = np.sqrt(
                            np.sum((self.X_train_[j_idx] - self.X_train_[k_idx]) ** 2)
                        )

                    C[j, k] = self._variogram(dist_jk)

            C[:n_subset, n_subset] = 1
            C[n_subset, :n_subset] = 1
            C[n_subset, n_subset] = 0

            # Covariance vector between prediction point and training points
            c = np.zeros(n_subset + 1)
            for j in range(n_subset):
                c[j] = self._variogram(distances_subset[j])
            c[n_subset] = 1

            # Solve kriging system
            try:
                weights = solve(C, c)
            except np.linalg.LinAlgError:
                # Fallback to pseudo-inverse if singular
                weights = np.linalg.lstsq(C, c, rcond=None)[0]

            # Prediction
            predictions[i] = np.dot(weights[:n_subset], y_subset)

            # Variance
            if return_variance:
                variances[i] = np.dot(weights, c)

        if return_variance:
            return predictions, variances
        return predictions


class UniversalKriging(OrdinaryKriging):
    """
    Universal kriging with trend.

    Extends ordinary kriging to include a deterministic trend component.

    Parameters
    ----------
    variogram_model : str, default='spherical'
        Variogram model
    trend : {'linear', 'quadratic'}, default='linear'
        Trend model
    variogram_parameters : dict, optional
        Variogram parameters
    n_closest : int, optional
        Number of closest points to use

    Examples
    --------
    >>> from krl_geospatial.interpolation import UniversalKriging
    >>>
    >>> uk = UniversalKriging(trend='linear')
    >>> uk.fit(train_gdf, 'elevation')
    >>> predictions = uk.predict(test_gdf)
    """

    def __init__(
        self,
        variogram_model: str = "spherical",
        trend: str = "linear",
        variogram_parameters: Optional[dict] = None,
        n_closest: Optional[int] = None,
    ):
        super().__init__(variogram_model, variogram_parameters, n_closest)

        if trend not in ["linear", "quadratic"]:
            raise ValueError(f"Invalid trend: {trend}")

        self.trend = trend
        self._trend_params = None

    def fit(self, gdf, variable: str):
        """Fit universal kriging model."""
        super().fit(gdf, variable)

        # Fit trend
        X = self.X_train_
        y = self.y_train_

        if self.trend == "linear":
            # Fit linear trend: y = a + b*x + c*y
            design_matrix = np.column_stack([np.ones(len(X)), X[:, 0], X[:, 1]])
        else:  # quadratic
            # Fit quadratic trend
            design_matrix = np.column_stack(
                [np.ones(len(X)), X[:, 0], X[:, 1], X[:, 0] ** 2, X[:, 1] ** 2, X[:, 0] * X[:, 1]]
            )

        self._trend_params = np.linalg.lstsq(design_matrix, y, rcond=None)[0]

        # Detrend data for variogram
        trend_values = design_matrix @ self._trend_params
        self.y_train_ = y - trend_values

        # Re-fit variogram on residuals
        if self.variogram_parameters is None:
            self.variogram_params_ = self._fit_variogram()

        return self

    def predict(self, gdf, return_variance: bool = False):
        """Predict with trend."""
        X_pred = np.column_stack([gdf.geometry.x, gdf.geometry.y])

        # Predict trend
        if self.trend == "linear":
            design_matrix = np.column_stack([np.ones(len(X_pred)), X_pred[:, 0], X_pred[:, 1]])
        else:  # quadratic
            design_matrix = np.column_stack(
                [
                    np.ones(len(X_pred)),
                    X_pred[:, 0],
                    X_pred[:, 1],
                    X_pred[:, 0] ** 2,
                    X_pred[:, 1] ** 2,
                    X_pred[:, 0] * X_pred[:, 1],
                ]
            )

        trend_pred = design_matrix @ self._trend_params

        # Predict residuals
        if return_variance:
            residual_pred, variances = super().predict(gdf, return_variance=True)
            return trend_pred + residual_pred, variances
        else:
            residual_pred = super().predict(gdf, return_variance=False)
            return trend_pred + residual_pred
