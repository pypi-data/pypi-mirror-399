"""
Local Indicators of Spatial Association (LISA) and pattern analysis.

© 2025 KR-Labs. All rights reserved.

References
----------
Anselin, L. (1995). Local indicators of spatial association—LISA.
    Geographical Analysis, 27(2), 93-115.
"""

from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


class LISAAnalysis:
    """
    Local Indicators of Spatial Association (LISA).

    Identifies local spatial clusters and outliers using local Moran's I.

    Parameters
    ----------
    permutations : int, default=999
        Number of permutations for significance testing

    Attributes
    ----------
    local_i_ : ndarray
        Local Moran's I values
    p_values_ : ndarray
        P-values from permutation test
    quadrant_ : ndarray
        Quadrant classification (1=HH, 2=LH, 3=LL, 4=HL)
    significant_ : ndarray
        Boolean array indicating significant locations
    cluster_labels_ : ndarray
        Cluster labels: 'HH', 'LL', 'LH', 'HL', 'NS' (not significant)

    Examples
    --------
    >>> from krl_geospatial.analysis import LISAAnalysis
    >>> from krl_geospatial.weights import QueenWeights
    >>>
    >>> w = QueenWeights()
    >>> w.fit(gdf)
    >>>
    >>> lisa = LISAAnalysis(permutations=999)
    >>> lisa.fit(gdf, w, 'income')
    >>>
    >>> # Get cluster map
    >>> clusters = lisa.get_cluster_map()
    >>> print(clusters.value_counts())
    """

    def __init__(self, permutations: int = 999):
        if permutations < 1:
            raise ValueError("permutations must be >= 1")

        self.permutations = permutations

        self.local_i_ = None
        self.p_values_ = None
        self.quadrant_ = None
        self.significant_ = None
        self.cluster_labels_ = None
        self._z_values = None
        self._lag_values = None

    def fit(
        self,
        gdf,
        weights,
        variable: str,
        alpha: float = 0.05,
    ):
        """
        Compute Local Moran's I statistics.

        Parameters
        ----------
        gdf : GeoDataFrame
            Geographic data
        weights : SpatialWeights
            Spatial weights matrix
        variable : str
            Name of variable to analyze
        alpha : float, default=0.05
            Significance level

        Returns
        -------
        self : LISAAnalysis
            Fitted estimator
        """
        X = gdf[variable].values
        W = weights.to_sparse()
        n = len(X)

        # Standardize
        X_mean = X.mean()
        X_std = X.std()
        z = (X - X_mean) / X_std
        self._z_values = z

        # Calculate spatial lag
        W_row_sums = np.array(W.sum(axis=1)).flatten()
        W_normalized = W.copy()

        for i in range(n):
            if W_row_sums[i] > 0:
                W_normalized[i] = W_normalized[i] / W_row_sums[i]

        lag = W_normalized @ z
        self._lag_values = lag

        # Local Moran's I
        self.local_i_ = z * lag

        # Permutation test for significance
        self.p_values_ = np.zeros(n)

        for i in range(n):
            # Observed value
            observed = self.local_i_[i]

            # Permutation distribution
            perm_values = np.zeros(self.permutations)
            neighbors = W[i].nonzero()[1]

            if len(neighbors) == 0:
                self.p_values_[i] = 1.0
                continue

            for perm in range(self.permutations):
                # Permute neighbor values
                perm_z = np.random.permutation(z)
                perm_lag = perm_z[neighbors].mean()
                perm_values[perm] = z[i] * perm_lag

            # P-value (two-tailed)
            self.p_values_[i] = np.sum(np.abs(perm_values) >= np.abs(observed)) / self.permutations

        # Identify quadrants
        self.quadrant_ = np.zeros(n, dtype=int)
        self.quadrant_[(z > 0) & (lag > 0)] = 1  # HH: High-High
        self.quadrant_[(z < 0) & (lag > 0)] = 2  # LH: Low-High
        self.quadrant_[(z < 0) & (lag < 0)] = 3  # LL: Low-Low
        self.quadrant_[(z > 0) & (lag < 0)] = 4  # HL: High-Low

        # Significant locations
        self.significant_ = self.p_values_ < alpha

        # Cluster labels
        labels = np.full(n, "NS", dtype="<U2")  # Not Significant
        labels[(self.quadrant_ == 1) & self.significant_] = "HH"
        labels[(self.quadrant_ == 2) & self.significant_] = "LH"
        labels[(self.quadrant_ == 3) & self.significant_] = "LL"
        labels[(self.quadrant_ == 4) & self.significant_] = "HL"
        self.cluster_labels_ = labels

        return self

    def get_cluster_map(self, alpha: Optional[float] = None):
        """
        Get cluster map DataFrame.

        Parameters
        ----------
        alpha : float, optional
            Significance level (uses fitting alpha if None)

        Returns
        -------
        cluster_map : Series
            Cluster labels for each location
        """
        if alpha is not None:
            significant = self.p_values_ < alpha
            labels = np.full(len(self.quadrant_), "NS", dtype="<U2")
            labels[(self.quadrant_ == 1) & significant] = "HH"
            labels[(self.quadrant_ == 2) & significant] = "LH"
            labels[(self.quadrant_ == 3) & significant] = "LL"
            labels[(self.quadrant_ == 4) & significant] = "HL"
            return pd.Series(labels)

        return pd.Series(self.cluster_labels_)

    def plot_moran_scatterplot(self, ax=None, **kwargs):
        """
        Create Moran scatterplot.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to plot on
        **kwargs : dict
            Additional arguments passed to scatter plot

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object
        ax : matplotlib.axes.Axes
            Axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        else:
            fig = ax.figure

        # Plot points
        colors = []
        for label in self.cluster_labels_:
            if label == "HH":
                colors.append("red")
            elif label == "LL":
                colors.append("blue")
            elif label == "LH":
                colors.append("lightblue")
            elif label == "HL":
                colors.append("pink")
            else:
                colors.append("gray")

        ax.scatter(self._z_values, self._lag_values, c=colors, alpha=0.6, **kwargs)

        # Add regression line
        slope = np.polyfit(self._z_values, self._lag_values, 1)[0]
        x_line = np.array([self._z_values.min(), self._z_values.max()])
        y_line = slope * x_line
        ax.plot(x_line, y_line, "k--", lw=2, label=f"Slope: {slope:.3f}")

        # Add quadrant lines
        ax.axhline(y=0, color="k", lw=0.5)
        ax.axvline(x=0, color="k", lw=0.5)

        # Labels
        ax.set_xlabel("Standardized Value")
        ax.set_ylabel("Spatial Lag")
        ax.set_title("Moran Scatterplot")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig, ax

    def plot_cluster_map(self, gdf, ax=None, **kwargs):
        """
        Plot LISA cluster map.

        Parameters
        ----------
        gdf : GeoDataFrame
            Geographic data
        ax : matplotlib.axes.Axes, optional
            Axes to plot on
        **kwargs : dict
            Additional arguments passed to GeoDataFrame.plot()

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object
        ax : matplotlib.axes.Axes
            Axes object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 10))
        else:
            fig = ax.figure

        # Create color map
        color_map = {
            "HH": "red",
            "LL": "blue",
            "LH": "lightblue",
            "HL": "pink",
            "NS": "lightgray",
        }

        colors = [color_map[label] for label in self.cluster_labels_]

        gdf.plot(ax=ax, color=colors, edgecolor="black", linewidth=0.5, **kwargs)

        # Legend
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor="red", label="High-High"),
            Patch(facecolor="blue", label="Low-Low"),
            Patch(facecolor="lightblue", label="Low-High"),
            Patch(facecolor="pink", label="High-Low"),
            Patch(facecolor="lightgray", label="Not Significant"),
        ]
        ax.legend(handles=legend_elements, loc="best")
        ax.set_title("LISA Cluster Map")
        ax.axis("off")

        return fig, ax


def moran_scatterplot(
    gdf,
    weights,
    variable: str,
    ax=None,
):
    """
    Create Moran scatterplot without full LISA analysis.

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data
    weights : SpatialWeights
        Spatial weights matrix
    variable : str
        Name of variable to analyze
    ax : matplotlib.axes.Axes, optional
        Axes to plot on

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes
        Axes object
    slope : float
        Slope of regression line (global Moran's I approximation)
    """
    X = gdf[variable].values
    W = weights.to_sparse()
    n = len(X)

    # Standardize
    z = (X - X.mean()) / X.std()

    # Calculate spatial lag
    W_row_sums = np.array(W.sum(axis=1)).flatten()
    W_normalized = W.copy()

    for i in range(n):
        if W_row_sums[i] > 0:
            W_normalized[i] = W_normalized[i] / W_row_sums[i]

    lag = W_normalized @ z

    # Plot
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    else:
        fig = ax.figure

    ax.scatter(z, lag, alpha=0.6)

    # Regression line
    slope = np.polyfit(z, lag, 1)[0]
    x_line = np.array([z.min(), z.max()])
    y_line = slope * x_line
    ax.plot(x_line, y_line, "r--", lw=2, label=f"Slope: {slope:.3f}")

    # Quadrant lines
    ax.axhline(y=0, color="k", lw=0.5)
    ax.axvline(x=0, color="k", lw=0.5)

    ax.set_xlabel("Standardized Value")
    ax.set_ylabel("Spatial Lag")
    ax.set_title("Moran Scatterplot")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig, ax, slope
