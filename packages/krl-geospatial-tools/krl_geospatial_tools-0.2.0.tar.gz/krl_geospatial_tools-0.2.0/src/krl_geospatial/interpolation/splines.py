"""
Spline-based spatial interpolation.

© 2025 KR-Labs. All rights reserved.

References
----------
Duchon, J. (1977). Splines minimizing rotation-invariant semi-norms in
    Sobolev spaces. In Constructive theory of functions of several variables
    (pp. 85-100). Springer.
Wahba, G. (1990). Spline models for observational data. SIAM.
"""

from typing import Optional

import numpy as np
from scipy.linalg import solve
from scipy.spatial.distance import cdist


class ThinPlateSpline:
    """
    Thin plate spline interpolation.

    Fits a smooth surface that minimizes bending energy while passing
    through (or near) the observed data points.

    Parameters
    ----------
    smoothing : float, default=0.0
        Smoothing parameter (0 = interpolation, >0 = smoothing)

    Attributes
    ----------
    X_train_ : ndarray
        Training coordinates
    y_train_ : ndarray
        Training values
    weights_ : ndarray
        Spline weights

    Examples
    --------
    >>> from krl_geospatial.interpolation import ThinPlateSpline
    >>>
    >>> # Exact interpolation
    >>> tps = ThinPlateSpline(smoothing=0.0)
    >>> tps.fit(train_gdf, 'elevation')
    >>> predictions = tps.predict(test_gdf)
    >>>
    >>> # Smoothed interpolation
    >>> tps_smooth = ThinPlateSpline(smoothing=0.1)
    >>> tps_smooth.fit(train_gdf, 'noisy_data')
    >>> predictions = tps_smooth.predict(test_gdf)
    """

    def __init__(self, smoothing: float = 0.0):
        if smoothing < 0:
            raise ValueError("smoothing must be non-negative")

        self.smoothing = smoothing

        self.X_train_ = None
        self.y_train_ = None
        self.weights_ = None
        self._variable = None

    def fit(self, gdf, variable: str):
        """
        Fit thin plate spline.

        Parameters
        ----------
        gdf : GeoDataFrame
            Training data
        variable : str
            Name of variable to interpolate

        Returns
        -------
        self : ThinPlateSpline
            Fitted estimator
        """
        self._variable = variable
        self.X_train_ = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        self.y_train_ = gdf[variable].values
        n = len(self.X_train_)

        # Build system matrix
        # Distance matrix
        distances = cdist(self.X_train_, self.X_train_)

        # Radial basis function matrix
        K = self._radial_basis(distances)

        # Polynomial matrix
        P = np.column_stack([np.ones(n), self.X_train_[:, 0], self.X_train_[:, 1]])

        # Build full matrix
        # [K + λI   P  ] [w]   [y]
        # [P^T      0  ] [a] = [0]

        A = np.zeros((n + 3, n + 3))
        A[:n, :n] = K + self.smoothing * np.eye(n)
        A[:n, n:] = P
        A[n:, :n] = P.T

        b = np.zeros(n + 3)
        b[:n] = self.y_train_

        # Solve system
        try:
            self.weights_ = solve(A, b)
        except np.linalg.LinAlgError:
            # Fallback to pseudo-inverse
            self.weights_ = np.linalg.lstsq(A, b, rcond=None)[0]

        return self

    def predict(self, gdf):
        """
        Predict at new locations.

        Parameters
        ----------
        gdf : GeoDataFrame
            Locations to predict at

        Returns
        -------
        predictions : ndarray
            Predicted values
        """
        X_pred = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        n_pred = len(X_pred)
        n_train = len(self.X_train_)

        # Calculate distances to training points
        distances = cdist(X_pred, self.X_train_)

        # Radial basis values
        K_pred = self._radial_basis(distances)

        # Polynomial values
        P_pred = np.column_stack([np.ones(n_pred), X_pred[:, 0], X_pred[:, 1]])

        # Predict
        predictions = K_pred @ self.weights_[:n_train] + P_pred @ self.weights_[n_train:]

        return predictions

    def _radial_basis(self, r):
        """
        Thin plate spline radial basis function.

        φ(r) = r² log(r) for r > 0, 0 for r = 0
        """
        with np.errstate(divide="ignore", invalid="ignore"):
            result = r**2 * np.log(r)
            result[r == 0] = 0
            result[np.isnan(result)] = 0
        return result


class RegularizedSpline:
    """
    Regularized spline with tension parameter.

    Extends thin plate splines with additional tension control to reduce
    overfitting and oscillations.

    Parameters
    ----------
    tension : float, default=0.0
        Tension parameter (0 = thin plate spline, >0 = more tension)
    smoothing : float, default=0.0
        Smoothing parameter

    Examples
    --------
    >>> from krl_geospatial.interpolation import RegularizedSpline
    >>>
    >>> # High tension for flatter surface
    >>> spline = RegularizedSpline(tension=1.0, smoothing=0.1)
    >>> spline.fit(train_gdf, 'temperature')
    >>> predictions = spline.predict(test_gdf)
    """

    def __init__(
        self,
        tension: float = 0.0,
        smoothing: float = 0.0,
    ):
        if tension < 0:
            raise ValueError("tension must be non-negative")
        if smoothing < 0:
            raise ValueError("smoothing must be non-negative")

        self.tension = tension
        self.smoothing = smoothing

        self.X_train_ = None
        self.y_train_ = None
        self.weights_ = None
        self._variable = None

    def fit(self, gdf, variable: str):
        """Fit regularized spline."""
        self._variable = variable
        self.X_train_ = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        self.y_train_ = gdf[variable].values
        n = len(self.X_train_)

        # Build system with tension
        distances = cdist(self.X_train_, self.X_train_)

        # Modified radial basis with tension
        K = self._radial_basis_tension(distances)

        # Polynomial matrix
        P = np.column_stack([np.ones(n), self.X_train_[:, 0], self.X_train_[:, 1]])

        # Build full matrix with smoothing and tension
        A = np.zeros((n + 3, n + 3))
        A[:n, :n] = K + (self.smoothing + self.tension) * np.eye(n)
        A[:n, n:] = P
        A[n:, :n] = P.T

        b = np.zeros(n + 3)
        b[:n] = self.y_train_

        # Solve system
        try:
            self.weights_ = solve(A, b)
        except np.linalg.LinAlgError:
            self.weights_ = np.linalg.lstsq(A, b, rcond=None)[0]

        return self

    def predict(self, gdf):
        """Predict at new locations."""
        X_pred = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        n_pred = len(X_pred)
        n_train = len(self.X_train_)

        # Calculate distances
        distances = cdist(X_pred, self.X_train_)

        # Radial basis with tension
        K_pred = self._radial_basis_tension(distances)

        # Polynomial values
        P_pred = np.column_stack([np.ones(n_pred), X_pred[:, 0], X_pred[:, 1]])

        # Predict
        predictions = K_pred @ self.weights_[:n_train] + P_pred @ self.weights_[n_train:]

        return predictions

    def _radial_basis_tension(self, r):
        """
        Modified radial basis function with tension.

        Blends between thin plate spline and exponential decay.
        """
        if self.tension == 0:
            # Standard thin plate spline
            with np.errstate(divide="ignore", invalid="ignore"):
                result = r**2 * np.log(r)
                result[r == 0] = 0
                result[np.isnan(result)] = 0
            return result
        else:
            # With tension: φ(r) = exp(-τr) * r² log(r)
            with np.errstate(divide="ignore", invalid="ignore"):
                result = np.exp(-self.tension * r) * r**2 * np.log(r)
                result[r == 0] = 0
                result[np.isnan(result)] = 0
            return result
