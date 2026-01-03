"""
Hot spot analysis using Getis-Ord Gi* and spatial scan statistics.

© 2025 KR-Labs. All rights reserved.

References
----------
Getis, A., & Ord, J. K. (1992). The analysis of spatial association by use
    of distance statistics. Geographical Analysis, 24(3), 189-206.
Ord, J. K., & Getis, A. (1995). Local spatial autocorrelation statistics:
    distributional issues and an application. Geographical Analysis, 27(4), 286-306.
Kulldorff, M. (1997). A spatial scan statistic. Communications in Statistics
    -Theory and Methods, 26(6), 1481-1496.
"""

from typing import List, Optional, Union

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import csr_matrix


class GetisOrdGiStar:
    """
    Getis-Ord Gi* statistic for hot spot analysis.

    Identifies statistically significant spatial clusters of high values
    (hot spots) and low values (cold spots).

    Parameters
    ----------
    star : bool, default=True
        If True, uses Gi* (includes focal observation).
        If False, uses Gi (excludes focal observation).
    permutations : int, optional
        Number of permutations for significance testing.
        If None, uses analytical inference.
    correction : {'bonferroni', 'fdr', 'none'}, default='fdr'
        Multiple testing correction method

    Attributes
    ----------
    gi_values_ : ndarray
        Getis-Ord Gi* values for each location
    z_scores_ : ndarray
        Standardized z-scores
    p_values_ : ndarray
        P-values for each location
    hot_spots_ : ndarray
        Boolean array indicating significant hot spots
    cold_spots_ : ndarray
        Boolean array indicating significant cold spots

    Examples
    --------
    >>> from krl_geospatial.analysis import GetisOrdGiStar
    >>> from krl_geospatial.weights import QueenWeights
    >>>
    >>> w = QueenWeights()
    >>> w.fit(gdf)
    >>>
    >>> gi_star = GetisOrdGiStar()
    >>> gi_star.fit(gdf, w, 'crime_rate')
    >>>
    >>> # Identify hot spots
    >>> hot_spots = gdf[gi_star.hot_spots_]
    >>> print(f"Found {len(hot_spots)} hot spots")
    """

    def __init__(
        self,
        star: bool = True,
        permutations: Optional[int] = None,
        correction: str = "fdr",
    ):
        if correction not in ["bonferroni", "fdr", "none"]:
            raise ValueError(f"Invalid correction method: {correction}")

        self.star = star
        self.permutations = permutations
        self.correction = correction

        self.gi_values_ = None
        self.z_scores_ = None
        self.p_values_ = None
        self.hot_spots_ = None
        self.cold_spots_ = None
        self._variable = None

    def fit(
        self,
        gdf,
        weights,
        variable: str,
        alpha: float = 0.05,
    ):
        """
        Compute Getis-Ord Gi* statistics.

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
        self : GetisOrdGiStar
            Fitted estimator
        """
        self._variable = variable
        X = gdf[variable].values
        W = weights.to_sparse()
        n = len(X)

        # Calculate Gi* for each location
        self.gi_values_ = np.zeros(n)
        self.z_scores_ = np.zeros(n)

        # Global statistics
        X_mean = X.mean()
        X_std = X.std()

        for i in range(n):
            # Get neighbors
            if self.star:
                # Gi* includes focal observation
                neighbors = W[i].nonzero()[1]
                neighbors = np.append(neighbors, i)
            else:
                # Gi excludes focal observation
                neighbors = W[i].nonzero()[1]

            if len(neighbors) == 0:
                continue

            # Gi statistic
            w_sum = len(neighbors)  # Binary weights
            numerator = X[neighbors].sum()

            # Calculate expected value and variance
            E_Gi = w_sum * X_mean

            # Variance
            S = X_std
            n_val = n
            var_Gi = S * np.sqrt((n_val * w_sum - w_sum**2) / (n_val - 1))

            if var_Gi > 0:
                self.z_scores_[i] = (numerator - E_Gi) / var_Gi
                self.gi_values_[i] = numerator
            else:
                self.z_scores_[i] = 0
                self.gi_values_[i] = numerator

        # Calculate p-values
        if self.permutations is not None:
            # Permutation-based inference
            self.p_values_ = self._permutation_inference(X, W, alpha)
        else:
            # Analytical inference
            self.p_values_ = 2 * (1 - stats.norm.cdf(np.abs(self.z_scores_)))

        # Apply multiple testing correction
        self.p_values_ = self._correct_pvalues(self.p_values_)

        # Identify hot and cold spots
        self.hot_spots_ = (self.z_scores_ > 0) & (self.p_values_ < alpha)
        self.cold_spots_ = (self.z_scores_ < 0) & (self.p_values_ < alpha)

        return self

    def _permutation_inference(self, X, W, alpha):
        """Perform permutation-based inference."""
        n = len(X)
        p_values = np.zeros(n)

        for i in range(n):
            # Observed Gi*
            if self.star:
                neighbors = np.append(W[i].nonzero()[1], i)
            else:
                neighbors = W[i].nonzero()[1]

            if len(neighbors) == 0:
                p_values[i] = 1.0
                continue

            observed_gi = X[neighbors].sum()

            # Permutation distribution
            perm_gi = np.zeros(self.permutations)
            for perm in range(self.permutations):
                X_perm = np.random.permutation(X)
                perm_gi[perm] = X_perm[neighbors].sum()

            # P-value
            p_values[i] = (
                np.sum(np.abs(perm_gi - perm_gi.mean()) >= np.abs(observed_gi - perm_gi.mean()))
                / self.permutations
            )

        return p_values

    def _correct_pvalues(self, p_values):
        """Apply multiple testing correction."""
        if self.correction == "bonferroni":
            # Bonferroni correction
            return np.minimum(p_values * len(p_values), 1.0)

        elif self.correction == "fdr":
            # False Discovery Rate (Benjamini-Hochberg)
            n = len(p_values)
            sorted_indices = np.argsort(p_values)
            sorted_pvalues = p_values[sorted_indices]

            # Calculate adjusted p-values
            adjusted = np.zeros(n)
            for i in range(n):
                adjusted[sorted_indices[i]] = min(sorted_pvalues[i] * n / (i + 1), 1.0)

            # Enforce monotonicity
            for i in range(n - 2, -1, -1):
                idx = sorted_indices[i]
                next_idx = sorted_indices[i + 1]
                adjusted[idx] = min(adjusted[idx], adjusted[next_idx])

            return adjusted

        else:  # 'none'
            return p_values

    def get_cluster_map(self, alpha: float = 0.05):
        """
        Get cluster classification for each location.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level

        Returns
        -------
        clusters : ndarray
            Cluster classification: 1=hot spot, -1=cold spot, 0=not significant
        """
        clusters = np.zeros(len(self.z_scores_), dtype=int)
        clusters[self.hot_spots_] = 1
        clusters[self.cold_spots_] = -1
        return clusters


def spatial_scan(
    gdf,
    variable: str,
    max_radius: Optional[float] = None,
    n_circles: int = 20,
    alpha: float = 0.05,
):
    """
    Kulldorff's spatial scan statistic for cluster detection.

    Scans the study area with circular windows of varying sizes to detect
    spatial clusters of high or low values.

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data with point geometries
    variable : str
        Name of variable to analyze
    max_radius : float, optional
        Maximum radius for circular scan window
        If None, uses maximum pairwise distance / 2
    n_circles : int, default=20
        Number of different radii to test
    alpha : float, default=0.05
        Significance level

    Returns
    -------
    results : dict
        Dictionary containing:
        - 'clusters': List of detected clusters
        - 'log_likelihood_ratios': LLR for each cluster
        - 'p_values': P-values for each cluster
        - 'centers': Center coordinates of each cluster
        - 'radii': Radii of each cluster

    Examples
    --------
    >>> from krl_geospatial.analysis import spatial_scan
    >>>
    >>> results = spatial_scan(gdf, 'case_count', max_radius=5000)
    >>> print(f"Found {len(results['clusters'])} clusters")
    """
    # Extract coordinates and values
    coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
    values = gdf[variable].values
    n = len(values)

    # Calculate maximum radius if not provided
    if max_radius is None:
        from scipy.spatial.distance import pdist

        distances = pdist(coords)
        max_radius = distances.max() / 2

    # Generate radii to test
    radii = np.linspace(max_radius / n_circles, max_radius, n_circles)

    # Total sum and count
    total_sum = values.sum()
    total_count = n

    # Store results
    clusters = []
    llr_values = []

    # Scan each location as potential cluster center
    for center_idx in range(n):
        center = coords[center_idx]

        # Test each radius
        for radius in radii:
            # Find points within radius
            distances = np.sqrt(np.sum((coords - center) ** 2, axis=1))
            in_circle = distances <= radius

            if in_circle.sum() < 2:
                continue

            # Calculate likelihood ratio
            circle_sum = values[in_circle].sum()
            circle_count = in_circle.sum()
            outside_sum = total_sum - circle_sum
            outside_count = total_count - circle_count

            if outside_count == 0:
                continue

            # Expected values under null hypothesis
            expected_in = (circle_count / total_count) * total_sum
            expected_out = (outside_count / total_count) * total_sum

            # Log likelihood ratio
            if circle_sum > expected_in:
                llr = circle_sum * np.log(circle_sum / expected_in) + outside_sum * np.log(
                    outside_sum / expected_out
                )

                clusters.append(
                    {
                        "center_idx": center_idx,
                        "center": center,
                        "radius": radius,
                        "members": np.where(in_circle)[0],
                        "sum": circle_sum,
                        "count": circle_count,
                    }
                )
                llr_values.append(llr)

    if not clusters:
        return {
            "clusters": [],
            "log_likelihood_ratios": np.array([]),
            "p_values": np.array([]),
            "centers": np.array([]),
            "radii": np.array([]),
        }

    # Sort by LLR
    llr_values = np.array(llr_values)
    sorted_indices = np.argsort(llr_values)[::-1]

    # Keep non-overlapping clusters
    selected_clusters = []
    selected_llr = []
    used_points = set()

    for idx in sorted_indices:
        cluster = clusters[idx]
        members = set(cluster["members"])

        # Check for overlap
        if len(members & used_points) / len(members) < 0.5:  # Allow 50% overlap
            selected_clusters.append(cluster)
            selected_llr.append(llr_values[idx])
            used_points.update(members)

    # Calculate p-values (simplified - full implementation would use Monte Carlo)
    p_values = 1 - stats.chi2.cdf(2 * np.array(selected_llr), df=1)

    # Return list of cluster dicts
    result = []
    for cluster, llr, p_val in zip(selected_clusters, selected_llr, p_values):
        if p_val < alpha:
            result.append(
                {
                    "center_idx": cluster["center_idx"],
                    "center": cluster["center"],
                    "radius": cluster["radius"],
                    "llr": llr,
                    "p_value": p_val,
                    "count": cluster["count"],
                    "members": cluster["members"],
                }
            )

    return result
