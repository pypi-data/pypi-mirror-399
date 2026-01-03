"""
Clustering validation metrics for spatial data.

Provides metrics to evaluate the quality of spatial clustering results,
including silhouette score, Davies-Bouldin index, and Calinski-Harabasz index.

© 2025 KR-Labs. All rights reserved.
"""

from typing import Optional

import numpy as np
from scipy.sparse import csr_matrix


def silhouette_score(gdf, labels, weights=None, metric="euclidean"):
    """
    Compute spatially-aware silhouette coefficient.

    The silhouette coefficient measures how similar an object is to its own
    cluster compared to other clusters. For spatial data, this can be weighted
    by spatial proximity.

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data with observations
    labels : array-like of shape (n_samples,)
        Cluster labels for each observation
    weights : SpatialWeights, optional
        Spatial weights for spatial weighting
    metric : str, default='euclidean'
        Distance metric

    Returns
    -------
    score : float
        Mean silhouette coefficient over all samples (-1 to 1)
        Higher values indicate better-defined clusters

    Examples
    --------
    >>> from krl_geospatial.clustering import silhouette_score
    >>> score = silhouette_score(gdf, labels)
    >>> print(f"Silhouette score: {score:.3f}")
    """
    # Extract coordinates
    coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
    labels = np.asarray(labels)

    # Remove noise points (label -1)
    mask = labels >= 0
    coords = coords[mask]
    labels = labels[mask]

    if len(np.unique(labels)) < 2:
        return 0.0  # Need at least 2 clusters

    n_samples = len(coords)
    silhouettes = np.zeros(n_samples)

    for i in range(n_samples):
        # Get own cluster
        own_cluster = labels[i]

        # Calculate average distance to points in own cluster
        own_cluster_mask = labels == own_cluster
        own_cluster_points = coords[own_cluster_mask]

        if len(own_cluster_points) == 1:
            # Singleton cluster
            silhouettes[i] = 0
            continue

        # Exclude self
        other_in_cluster = np.delete(
            own_cluster_points, np.where(own_cluster_mask)[0].tolist().index(i), axis=0
        )

        if metric == "euclidean":
            a_i = np.mean(np.sqrt(np.sum((other_in_cluster - coords[i]) ** 2, axis=1)))
        else:
            a_i = np.mean(np.abs(other_in_cluster - coords[i]).sum(axis=1))

        # Calculate minimum average distance to points in other clusters
        b_i = np.inf

        for other_cluster in np.unique(labels):
            if other_cluster == own_cluster:
                continue

            other_cluster_mask = labels == other_cluster
            other_cluster_points = coords[other_cluster_mask]

            if metric == "euclidean":
                dist = np.mean(np.sqrt(np.sum((other_cluster_points - coords[i]) ** 2, axis=1)))
            else:
                dist = np.mean(np.abs(other_cluster_points - coords[i]).sum(axis=1))

            if dist < b_i:
                b_i = dist

        # Silhouette coefficient
        if b_i == np.inf:
            silhouettes[i] = 0
        else:
            silhouettes[i] = (b_i - a_i) / max(a_i, b_i)

    return np.mean(silhouettes)


def davies_bouldin_index(gdf, labels, metric="euclidean"):
    """
    Compute Davies-Bouldin index.

    Lower values indicate better clustering (more compact and well-separated clusters).

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data with observations
    labels : array-like of shape (n_samples,)
        Cluster labels for each observation
    metric : str, default='euclidean'
        Distance metric

    Returns
    -------
    score : float
        Davies-Bouldin index (lower is better, minimum is 0)

    Examples
    --------
    >>> from krl_geospatial.clustering import davies_bouldin_index
    >>> db_index = davies_bouldin_index(gdf, labels)
    >>> print(f"DB index: {db_index:.3f}")
    """
    # Extract coordinates
    coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
    labels = np.asarray(labels)

    # Remove noise points
    mask = labels >= 0
    coords = coords[mask]
    labels = labels[mask]

    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    if n_clusters < 2:
        return 0.0

    # Calculate cluster centroids
    centroids = np.array([coords[labels == k].mean(axis=0) for k in unique_labels])

    # Calculate within-cluster scatter
    scatter = np.zeros(n_clusters)
    for i, k in enumerate(unique_labels):
        cluster_points = coords[labels == k]
        if metric == "euclidean":
            scatter[i] = np.mean(np.sqrt(np.sum((cluster_points - centroids[i]) ** 2, axis=1)))
        else:
            scatter[i] = np.mean(np.abs(cluster_points - centroids[i]).sum(axis=1))

    # Calculate pairwise centroid distances
    if metric == "euclidean":
        centroid_distances = np.sqrt(
            np.sum((centroids[:, np.newaxis] - centroids[np.newaxis, :]) ** 2, axis=2)
        )
    else:
        centroid_distances = np.abs(centroids[:, np.newaxis] - centroids[np.newaxis, :]).sum(axis=2)

    # Calculate DB index
    db_values = np.zeros(n_clusters)

    for i in range(n_clusters):
        max_ratio = 0
        for j in range(n_clusters):
            if i != j:
                ratio = (scatter[i] + scatter[j]) / centroid_distances[i, j]
                if ratio > max_ratio:
                    max_ratio = ratio
        db_values[i] = max_ratio

    return np.mean(db_values)


def calinski_harabasz_index(gdf, labels):
    """
    Compute Calinski-Harabasz index (Variance Ratio Criterion).

    Higher values indicate better-defined clusters with more between-cluster
    separation and less within-cluster dispersion.

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data with observations
    labels : array-like of shape (n_samples,)
        Cluster labels for each observation

    Returns
    -------
    score : float
        Calinski-Harabasz index (higher is better)

    Examples
    --------
    >>> from krl_geospatial.clustering import calinski_harabasz_index
    >>> ch_index = calinski_harabasz_index(gdf, labels)
    >>> print(f"CH index: {ch_index:.3f}")
    """
    # Extract coordinates
    coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
    labels = np.asarray(labels)

    # Remove noise points
    mask = labels >= 0
    coords = coords[mask]
    labels = labels[mask]

    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)
    n_samples = len(coords)

    if n_clusters < 2 or n_samples <= n_clusters:
        return 0.0

    # Overall mean
    overall_mean = coords.mean(axis=0)

    # Between-cluster dispersion
    between_dispersion = 0
    for k in unique_labels:
        cluster_points = coords[labels == k]
        n_k = len(cluster_points)
        centroid_k = cluster_points.mean(axis=0)
        between_dispersion += n_k * np.sum((centroid_k - overall_mean) ** 2)

    # Within-cluster dispersion
    within_dispersion = 0
    for k in unique_labels:
        cluster_points = coords[labels == k]
        centroid_k = cluster_points.mean(axis=0)
        within_dispersion += np.sum((cluster_points - centroid_k) ** 2)

    if within_dispersion == 0:
        return 0.0

    # CH index
    ch_index = (between_dispersion / (n_clusters - 1)) / (
        within_dispersion / (n_samples - n_clusters)
    )

    return ch_index


def spatial_connectivity_index(gdf, labels, weights):
    """
    Compute spatial connectivity index.

    Measures the proportion of within-cluster edges to all possible edges.
    Higher values indicate more spatially contiguous clusters.

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data with observations
    labels : array-like of shape (n_samples,)
        Cluster labels for each observation
    weights : SpatialWeights
        Spatial weights defining connectivity

    Returns
    -------
    score : float
        Spatial connectivity index (0 to 1, higher is better)

    Examples
    --------
    >>> from krl_geospatial.clustering import spatial_connectivity_index
    >>> sci = spatial_connectivity_index(gdf, labels, weights)
    >>> print(f"Spatial connectivity: {sci:.3f}")
    """
    labels = np.asarray(labels)
    W = weights.to_sparse()

    # Remove noise points
    mask = labels >= 0
    labels_filtered = labels[mask]

    # Count within-cluster edges
    within_cluster_edges = 0
    total_edges = 0

    rows, cols = W.nonzero()

    for i, j in zip(rows, cols):
        if i >= j:  # Only count each edge once
            continue

        total_edges += 1

        if labels[i] == labels[j] and labels[i] >= 0:
            within_cluster_edges += 1

    if total_edges == 0:
        return 0.0

    return within_cluster_edges / total_edges


def evaluate_clustering(gdf, labels, weights=None, verbose=True):
    """
    Compute all clustering quality metrics.

    Parameters
    ----------
    gdf : GeoDataFrame
        Geographic data with observations
    labels : array-like of shape (n_samples,)
        Cluster labels for each observation
    weights : SpatialWeights, optional
        Spatial weights for connectivity index
    verbose : bool, default=True
        Whether to print results

    Returns
    -------
    metrics : dict
        Dictionary containing all computed metrics

    Examples
    --------
    >>> from krl_geospatial.clustering import evaluate_clustering
    >>> metrics = evaluate_clustering(gdf, labels, weights)
    """
    labels = np.asarray(labels)

    metrics = {
        "n_clusters": len(np.unique(labels[labels >= 0])),
        "n_noise": np.sum(labels == -1),
        "silhouette": silhouette_score(gdf, labels),
        "davies_bouldin": davies_bouldin_index(gdf, labels),
        "calinski_harabasz": calinski_harabasz_index(gdf, labels),
    }

    if weights is not None:
        metrics["spatial_connectivity"] = spatial_connectivity_index(gdf, labels, weights)

    if verbose:
        print("Clustering Quality Metrics:")
        print(f"  Number of clusters: {metrics['n_clusters']}")
        print(f"  Noise points: {metrics['n_noise']}")
        print(f"  Silhouette score: {metrics['silhouette']:.4f}")
        print(f"  Davies-Bouldin index: {metrics['davies_bouldin']:.4f}")
        print(f"  Calinski-Harabasz index: {metrics['calinski_harabasz']:.4f}")
        if "spatial_connectivity" in metrics:
            print(f"  Spatial connectivity: {metrics['spatial_connectivity']:.4f}")

    return metrics
