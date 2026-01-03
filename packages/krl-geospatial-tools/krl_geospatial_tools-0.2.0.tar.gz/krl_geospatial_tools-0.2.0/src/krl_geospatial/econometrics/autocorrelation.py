"""
Spatial autocorrelation statistics.

Global and local measures of spatial autocorrelation for detecting
spatial patterns and clustering.
"""

from typing import Optional, Tuple, Union

import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import sparse, stats

logger = get_logger(__name__)


def morans_i(
    values: np.ndarray, W: sparse.csr_matrix, permutations: int = 999
) -> Tuple[float, float, float]:
    """
    Calculate Moran's I statistic for global spatial autocorrelation.

    Moran's I measures the overall spatial autocorrelation in a variable,
    indicating whether similar values cluster together spatially.

    Args:
        values: Variable values (n x 1)
        W: Row-standardized spatial weights matrix (n x n)
        permutations: Number of random permutations for inference

    Returns:
        Tuple of (I, expected_I, p_value)
        - I: Moran's I statistic
        - expected_I: Expected value under null hypothesis
        - p_value: Pseudo p-value from permutation test

    Examples:
        >>> from krl_geospatial.weights import QueenWeights
        >>> W = QueenWeights().from_dataframe(gdf).matrix
        >>> I, E_I, p = morans_i(gdf['income'].values, W)
        >>> print(f"Moran's I: {I:.4f}, p-value: {p:.4f}")

    References:
        Moran, P.A.P. (1950). Notes on continuous stochastic phenomena.
        Biometrika, 37(1/2), 17-23.
    """
    values = np.asarray(values).flatten()
    n = len(values)

    # Standardize values
    z = values - np.mean(values)
    z_std = z / np.std(values)

    # Calculate Moran's I
    # I = (n/S0) * (z'Wz) / (z'z)
    # where S0 = sum of all weights

    Wz = W @ z_std
    numerator = z_std.T @ Wz
    denominator = z_std.T @ z_std

    S0 = W.sum()
    I = (n / S0) * (numerator / denominator)

    # Expected value under null hypothesis
    E_I = -1 / (n - 1)

    # Permutation test for significance
    if permutations > 0:
        I_perm = np.zeros(permutations)

        for i in range(permutations):
            # Randomly permute values
            idx_perm = np.random.permutation(n)
            z_perm = z_std[idx_perm]

            Wz_perm = W @ z_perm
            num_perm = z_perm.T @ Wz_perm
            den_perm = z_perm.T @ z_perm

            I_perm[i] = (n / S0) * (num_perm / den_perm)

        # Two-tailed p-value
        p_value = np.sum(np.abs(I_perm) >= np.abs(I)) / permutations
    else:
        # Analytical p-value (using normality assumption)
        # Variance calculation (simplified)
        var_I = 1 / n  # Simplified
        z_score = (I - E_I) / np.sqrt(var_I)
        p_value = 2 * (1 - stats.norm.cdf(np.abs(z_score)))

    logger.debug(f"Moran's I: {I:.4f}, E(I): {E_I:.4f}, p={p_value:.4f}")

    return I, E_I, p_value


def gearys_c(
    values: np.ndarray, W: sparse.csr_matrix, permutations: int = 999
) -> Tuple[float, float, float]:
    """
    Calculate Geary's C statistic for global spatial autocorrelation.

    Geary's C is complementary to Moran's I, with C < 1 indicating
    positive spatial autocorrelation and C > 1 indicating negative.

    Args:
        values: Variable values (n x 1)
        W: Row-standardized spatial weights matrix (n x n)
        permutations: Number of random permutations for inference

    Returns:
        Tuple of (C, expected_C, p_value)
        - C: Geary's C statistic
        - expected_C: Expected value (1.0) under null hypothesis
        - p_value: Pseudo p-value from permutation test

    Examples:
        >>> C, E_C, p = gearys_c(gdf['income'].values, W)
        >>> if C < 1:
        ...     print("Positive spatial autocorrelation")

    References:
        Geary, R.C. (1954). The contiguity ratio and statistical mapping.
        The Incorporated Statistician, 5(3), 115-146.
    """
    values = np.asarray(values).flatten()
    n = len(values)

    # Calculate Geary's C
    # C = ((n-1)/2S0) * sum_ij w_ij(x_i - x_j)^2 / sum_i(x_i - mean)^2

    z = values - np.mean(values)
    S0 = W.sum()

    # Compute squared differences for neighbors
    numerator = 0.0
    rows, cols = W.nonzero()

    for i, j in zip(rows, cols):
        w_ij = W[i, j]
        numerator += w_ij * (values[i] - values[j]) ** 2

    denominator = 2 * S0 * np.sum(z**2)

    C = ((n - 1) / denominator) * numerator

    # Expected value
    E_C = 1.0

    # Permutation test
    if permutations > 0:
        C_perm = np.zeros(permutations)

        for perm in range(permutations):
            idx_perm = np.random.permutation(n)
            values_perm = values[idx_perm]

            num_perm = 0.0
            for i, j in zip(rows, cols):
                w_ij = W[i, j]
                num_perm += w_ij * (values_perm[i] - values_perm[j]) ** 2

            C_perm[perm] = ((n - 1) / denominator) * num_perm

        # Two-tailed p-value
        p_value = np.sum(np.abs(C_perm - 1) >= np.abs(C - 1)) / permutations
    else:
        # Analytical p-value (simplified)
        var_C = 1 / n
        z_score = (C - E_C) / np.sqrt(var_C)
        p_value = 2 * (1 - stats.norm.cdf(np.abs(z_score)))

    logger.debug(f"Geary's C: {C:.4f}, E(C): {E_C:.4f}, p={p_value:.4f}")

    return C, E_C, p_value


def local_morans_i(
    values: np.ndarray, W: sparse.csr_matrix, permutations: int = 999
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate Local Indicators of Spatial Association (LISA).

    Computes local Moran's I for each location, identifying
    spatial clusters and outliers.

    Args:
        values: Variable values (n x 1)
        W: Row-standardized spatial weights matrix (n x n)
        permutations: Number of random permutations for inference

    Returns:
        Tuple of (I_local, p_values)
        - I_local: Local Moran's I for each location
        - p_values: P-values from permutation tests

    Examples:
        >>> I_local, p_vals = local_morans_i(gdf['income'].values, W)
        >>> # Identify significant clusters
        >>> clusters = (I_local > 0) & (p_vals < 0.05)
        >>> print(f"Found {np.sum(clusters)} significant clusters")

    References:
        Anselin, L. (1995). Local indicators of spatial association - LISA.
        Geographical Analysis, 27(2), 93-115.
    """
    values = np.asarray(values).flatten()
    n = len(values)

    # Standardize values
    mean_val = np.mean(values)
    std_val = np.std(values)
    z = (values - mean_val) / std_val

    # Calculate local Moran's I for each location
    # I_i = z_i * sum_j(w_ij * z_j)

    Wz = W @ z
    I_local = z * Wz

    # Permutation test for each location
    p_values = np.zeros(n)

    if permutations > 0:
        for i in range(n):
            # Get neighbors of location i
            neighbors = W[i].nonzero()[1]

            if len(neighbors) == 0:
                p_values[i] = 1.0
                continue

            # Permute neighbor values
            I_perm = np.zeros(permutations)

            for perm in range(permutations):
                # Randomly select values for neighbors
                idx_perm = np.random.choice(n, size=len(neighbors), replace=False)
                z_neighbors_perm = z[idx_perm]

                # Calculate I_i for permutation
                w_i = W[i, neighbors].toarray().flatten()
                I_perm[perm] = z[i] * np.sum(w_i * z_neighbors_perm)

            # One-tailed p-value (positive autocorrelation)
            if I_local[i] >= 0:
                p_values[i] = np.sum(I_perm >= I_local[i]) / permutations
            else:
                p_values[i] = np.sum(I_perm <= I_local[i]) / permutations
    else:
        # Analytical approximation (simplified)
        var_I = 1.0 / n
        z_scores = I_local / np.sqrt(var_I)
        p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))

    logger.debug(f"Local Moran's I computed for {n} locations")

    return I_local, p_values


def getis_ord_g(values: np.ndarray, W: sparse.csr_matrix) -> Tuple[float, float]:
    """
    Calculate Getis-Ord Global G statistic.

    Measures high/low clustering globally. High G indicates
    clustering of high values; low G indicates clustering of low values.

    Args:
        values: Variable values (n x 1)
        W: Binary spatial weights matrix (n x n)

    Returns:
        Tuple of (G, z_score)
        - G: Global G statistic
        - z_score: Standardized score

    Examples:
        >>> G, z = getis_ord_g(gdf['income'].values, W)
        >>> if z > 1.96:
        ...     print("Significant clustering of high values")

    References:
        Getis, A., & Ord, J.K. (1992). The analysis of spatial association
        by use of distance statistics. Geographical Analysis, 24(3), 189-206.
    """
    values = np.asarray(values).flatten()
    n = len(values)

    # Sum of all weights
    S0 = W.sum()

    # Calculate G
    # G = (sum_i sum_j w_ij x_i x_j) / (sum_i sum_j x_i x_j)

    Wx = W @ values
    numerator = np.sum(values * Wx)
    denominator = np.sum(values) ** 2 - np.sum(values**2)

    G = numerator / denominator

    # Expected value and variance
    E_G = S0 / (n * (n - 1))

    # Simplified variance calculation
    var_G = (S0 * (n - S0)) / ((n * (n - 1)) ** 2)

    # Standardized score
    z_score = (G - E_G) / np.sqrt(var_G) if var_G > 0 else 0.0

    logger.debug(f"Global G: {G:.4f}, z-score: {z_score:.4f}")

    return G, z_score


def getis_ord_gi_star(
    values: np.ndarray, W: sparse.csr_matrix, include_self: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate Getis-Ord Local Gi* statistics.

    Identifies spatial clusters of high and low values (hot spots
    and cold spots). Gi* includes the location itself in the calculation.

    Args:
        values: Variable values (n x 1)
        W: Binary spatial weights matrix (n x n)
        include_self: Whether to include location in its own calculation

    Returns:
        Tuple of (Gi_star, z_scores)
        - Gi_star: Local Gi* for each location
        - z_scores: Standardized z-scores

    Examples:
        >>> Gi_star, z_scores = getis_ord_gi_star(gdf['income'].values, W)
        >>> # Identify hot spots (z > 1.96)
        >>> hot_spots = z_scores > 1.96
        >>> # Identify cold spots (z < -1.96)
        >>> cold_spots = z_scores < -1.96

    References:
        Ord, J.K., & Getis, A. (1995). Local spatial autocorrelation statistics:
        Distributional issues and an application. Geographical Analysis, 27(4), 286-306.
    """
    values = np.asarray(values).flatten()
    n = len(values)

    # If include_self, add self-weight
    if include_self:
        W_star = W + sparse.eye(n)
    else:
        W_star = W.copy()

    # Calculate statistics
    mean_val = np.mean(values)
    std_val = np.std(values)

    Gi_star = np.zeros(n)
    z_scores = np.zeros(n)

    for i in range(n):
        # Get neighbors (including self if include_self=True)
        w_i = W_star[i].toarray().flatten()

        # Calculate Gi*
        # Gi* = (sum_j w_ij x_j - mean * sum_j w_ij) / (s * sqrt[(n*sum w_ij^2 - (sum w_ij)^2)/(n-1)])

        sum_w = np.sum(w_i)
        sum_w_sq = np.sum(w_i**2)

        numerator = np.sum(w_i * values) - mean_val * sum_w

        if n > 1 and std_val > 0:
            denominator = std_val * np.sqrt((n * sum_w_sq - sum_w**2) / (n - 1))

            if denominator > 0:
                z_scores[i] = numerator / denominator
            else:
                z_scores[i] = 0.0
        else:
            z_scores[i] = 0.0

        Gi_star[i] = np.sum(w_i * values)

    logger.debug(f"Gi* computed for {n} locations")

    return Gi_star, z_scores
