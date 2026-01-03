"""
Inverse Distance Weighting (IDW) interpolation.

© 2025 KR-Labs. All rights reserved.

References
----------
Shepard, D. (1968). A two-dimensional interpolation function for irregularly-spaced
    data. Proceedings of the 1968 23rd ACM national conference, 517-524.
"""

from typing import Optional

import numpy as np
from scipy.spatial.distance import cdist


class IDW:
    """
    Inverse Distance Weighting interpolation.

    Predicts values using inverse distance weighted average of nearby points.

    Parameters
    ----------
    power : float, default=2.0
        Power parameter for inverse distance weighting
    radius : float, optional
        Search radius. If None, uses all points
    n_closest : int, optional
        Number of closest points to use. If None, uses all points within radius
    anisotropy_angle : float, optional
        Angle (in degrees) for anisotropic distance calculation
    anisotropy_ratio : float, default=1.0
        Ratio of major to minor axis for anisotropic distance

    Attributes
    ----------
    X_train_ : ndarray
        Training coordinates
    y_train_ : ndarray
        Training values

    Examples
    --------
    >>> from krl_geospatial.interpolation import IDW
    >>>
    >>> # Basic IDW
    >>> idw = IDW(power=2, radius=1000)
    >>> idw.fit(train_gdf, 'temperature')
    >>> predictions = idw.predict(test_gdf)
    >>>
    >>> # Anisotropic IDW
    >>> idw_aniso = IDW(
    ...     power=2,
    ...     anisotropy_angle=45,
    ...     anisotropy_ratio=2.0
    ... )
    >>> idw_aniso.fit(train_gdf, 'elevation')
    >>> predictions = idw_aniso.predict(test_gdf)
    """

    def __init__(
        self,
        power: float = 2.0,
        radius: Optional[float] = None,
        n_closest: Optional[int] = None,
        anisotropy_angle: Optional[float] = None,
        anisotropy_ratio: float = 1.0,
    ):
        if power <= 0:
            raise ValueError("power must be positive")
        if anisotropy_ratio <= 0:
            raise ValueError("anisotropy_ratio must be positive")

        self.power = power
        self.radius = radius
        self.n_closest = n_closest
        self.anisotropy_angle = anisotropy_angle
        self.anisotropy_ratio = anisotropy_ratio

        self.X_train_ = None
        self.y_train_ = None
        self._variable = None

    def fit(self, gdf, variable: str):
        """
        Fit IDW model.

        Parameters
        ----------
        gdf : GeoDataFrame
            Training data
        variable : str
            Name of variable to interpolate

        Returns
        -------
        self : IDW
            Fitted estimator
        """
        self._variable = variable
        self.X_train_ = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        self.y_train_ = gdf[variable].values
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
        predictions = np.zeros(n_pred)

        for i in range(n_pred):
            # Calculate distances
            if self.anisotropy_angle is not None:
                distances = self._anisotropic_distance(X_pred[i], self.X_train_)
            else:
                distances = np.sqrt(np.sum((self.X_train_ - X_pred[i]) ** 2, axis=1))

            # Apply radius filter
            if self.radius is not None:
                mask = distances <= self.radius
                if not mask.any():
                    # No points within radius, use closest point
                    predictions[i] = self.y_train_[np.argmin(distances)]
                    continue
                distances = distances[mask]
                y_subset = self.y_train_[mask]
            else:
                y_subset = self.y_train_

            # Apply n_closest filter
            if self.n_closest is not None and len(distances) > self.n_closest:
                closest_indices = np.argsort(distances)[: self.n_closest]
                distances = distances[closest_indices]
                y_subset = y_subset[closest_indices]

            # Handle exact matches
            zero_distance = distances < 1e-10
            if zero_distance.any():
                predictions[i] = y_subset[zero_distance][0]
                continue

            # Calculate weights
            weights = 1 / (distances**self.power)
            weights = weights / weights.sum()

            # Weighted average
            predictions[i] = np.dot(weights, y_subset)

        return predictions

    def _anisotropic_distance(self, point, points):
        """
        Calculate anisotropic distances.

        Distances are scaled differently along major and minor axes.
        """
        # Translate to origin
        diff = points - point

        # Rotate to align with anisotropy direction
        theta = np.radians(self.anisotropy_angle)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        x_rot = diff[:, 0] * cos_theta + diff[:, 1] * sin_theta
        y_rot = -diff[:, 0] * sin_theta + diff[:, 1] * cos_theta

        # Scale by anisotropy ratio
        x_scaled = x_rot
        y_scaled = y_rot * self.anisotropy_ratio

        # Calculate distance
        distances = np.sqrt(x_scaled**2 + y_scaled**2)

        return distances

    def cross_validate(self, gdf, variable: str):
        """
        Perform leave-one-out cross-validation.

        Parameters
        ----------
        gdf : GeoDataFrame
            Data for cross-validation
        variable : str
            Variable name

        Returns
        -------
        rmse : float
            Root mean squared error
        mae : float
            Mean absolute error
        predictions : ndarray
            Cross-validated predictions
        """
        X = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        y = gdf[variable].values
        n = len(X)

        predictions = np.zeros(n)

        for i in range(n):
            # Leave one out
            mask = np.ones(n, dtype=bool)
            mask[i] = False

            X_train = X[mask]
            y_train = y[mask]

            # Calculate distances
            if self.anisotropy_angle is not None:
                distances = self._anisotropic_distance(X[i], X_train)
            else:
                distances = np.sqrt(np.sum((X_train - X[i]) ** 2, axis=1))

            # Apply filters
            if self.radius is not None:
                radius_mask = distances <= self.radius
                if not radius_mask.any():
                    predictions[i] = y_train[np.argmin(distances)]
                    continue
                distances = distances[radius_mask]
                y_subset = y_train[radius_mask]
            else:
                y_subset = y_train

            if self.n_closest is not None and len(distances) > self.n_closest:
                closest_indices = np.argsort(distances)[: self.n_closest]
                distances = distances[closest_indices]
                y_subset = y_subset[closest_indices]

            # Calculate weights
            weights = 1 / (distances**self.power)
            weights = weights / weights.sum()

            predictions[i] = np.dot(weights, y_subset)

        # Calculate metrics
        errors = y - predictions
        rmse = np.sqrt(np.mean(errors**2))
        mae = np.mean(np.abs(errors))

        return rmse, mae, predictions
