"""
REDCAP (REgionalization with Dynamically Constrained Agglomerative clustering and Partitioning).

Implements spatially constrained hierarchical clustering with various linkage methods.

© 2025 KR-Labs. All rights reserved.

References
----------
Guo, D. (2008). Regionalization with dynamically constrained agglomerative
    clustering and partitioning (REDCAP). International Journal of Geographical
    Information Science, 22(7), 801-823.
"""

from typing import List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import linkage as scipy_linkage
from scipy.sparse import csr_matrix


class REDCAP:
    """
    REgionalization with Dynamically Constrained Agglomerative clustering.

    REDCAP performs hierarchical clustering with spatial contiguity constraints,
    producing a dendrogram that can be cut at any level to create regions.

    Parameters
    ----------
    n_clusters : int
        Number of clusters to create
    linkage : {'single', 'complete', 'average', 'ward'}, default='ward'
        Linkage criterion for hierarchical clustering
    dissimilarity : {'euclidean', 'sqeuclidean'}, default='sqeuclidean'
        Distance metric for attribute dissimilarity

    Attributes
    ----------
    labels_ : ndarray of shape (n_samples,)
        Cluster labels for each observation
    linkage_matrix_ : ndarray
        Hierarchical clustering encoded as linkage matrix
    inertia_ : float
        Sum of squared distances within clusters

    Examples
    --------
    >>> from krl_geospatial.clustering import REDCAP
    >>> from krl_geospatial.weights import QueenWeights
    >>>
    >>> w = QueenWeights()
    >>> w.fit(gdf)
    >>>
    >>> redcap = REDCAP(n_clusters=5, linkage='ward')
    >>> redcap.fit(gdf, w, attributes=['income', 'density'])
    >>> labels = redcap.labels_
    >>>
    >>> # Plot dendrogram
    >>> redcap.plot_dendrogram()
    """

    def __init__(
        self,
        n_clusters: int,
        linkage: str = "ward",
        dissimilarity: str = "sqeuclidean",
    ):
        if n_clusters < 2:
            raise ValueError("n_clusters must be >= 2")
        if linkage not in ["single", "complete", "average", "ward"]:
            raise ValueError(f"Invalid linkage: {linkage}")
        if dissimilarity not in ["euclidean", "sqeuclidean"]:
            raise ValueError(f"Invalid dissimilarity: {dissimilarity}")

        self.n_clusters = n_clusters
        self.linkage = linkage
        self.dissimilarity = dissimilarity

        self.labels_ = None
        self.linkage_matrix_ = None
        self.inertia_ = None
        self._tree = None

    def fit(
        self,
        gdf,
        weights,
        attributes: Union[List[str], np.ndarray],
    ):
        """
        Compute REDCAP regionalization.

        Parameters
        ----------
        gdf : GeoDataFrame
            Geographic data with observations
        weights : SpatialWeights
            Spatial weights defining connectivity
        attributes : list of str or ndarray
            Variable names or data array for clustering

        Returns
        -------
        self : REDCAP
            Fitted estimator
        """
        # Extract attribute data
        if isinstance(attributes, (list, tuple)):
            X = gdf[attributes].values
        else:
            X = np.asarray(attributes)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        n_samples = X.shape[0]

        # Standardize attributes
        X_std = (X - X.mean(axis=0)) / X.std(axis=0)

        # Get spatial weights
        W = weights.to_sparse()

        # Initialize each observation as its own cluster
        clusters = {i: [i] for i in range(n_samples)}
        cluster_centroids = {i: X_std[i].copy() for i in range(n_samples)}
        active_clusters = set(range(n_samples))

        # Track merges for linkage matrix
        merges = []
        next_cluster_id = n_samples

        # Agglomerative clustering with spatial constraint
        while len(active_clusters) > 1:
            # Find pair of adjacent clusters to merge
            best_pair = None
            best_distance = np.inf

            for cluster_i in active_clusters:
                # Find spatially contiguous neighbors
                neighbors = self._find_contiguous_clusters(cluster_i, clusters, active_clusters, W)

                for cluster_j in neighbors:
                    if cluster_j <= cluster_i:
                        continue

                    # Calculate distance between clusters
                    distance = self._cluster_distance(
                        clusters[cluster_i],
                        clusters[cluster_j],
                        cluster_centroids[cluster_i],
                        cluster_centroids[cluster_j],
                        X_std,
                    )

                    if distance < best_distance:
                        best_distance = distance
                        best_pair = (cluster_i, cluster_j)

            if best_pair is None:
                # No more adjacent clusters
                break

            # Merge clusters
            cluster_i, cluster_j = best_pair
            new_members = clusters[cluster_i] + clusters[cluster_j]
            new_centroid = X_std[new_members].mean(axis=0)

            # Record merge in linkage matrix format
            # [cluster_i, cluster_j, distance, size]
            merges.append([cluster_i, cluster_j, best_distance, len(new_members)])

            # Create new cluster
            clusters[next_cluster_id] = new_members
            cluster_centroids[next_cluster_id] = new_centroid

            # Remove merged clusters
            del clusters[cluster_i]
            del clusters[cluster_j]
            del cluster_centroids[cluster_i]
            del cluster_centroids[cluster_j]
            active_clusters.discard(cluster_i)
            active_clusters.discard(cluster_j)

            # Add new cluster
            active_clusters.add(next_cluster_id)
            next_cluster_id += 1

            # Stop if we've reached desired number of clusters
            if len(active_clusters) <= self.n_clusters:
                break

        # Create linkage matrix
        self.linkage_matrix_ = np.array(merges)

        # Create labels by cutting dendrogram
        self.labels_ = self._cut_dendrogram(clusters, n_samples)

        # Calculate inertia
        self.inertia_ = self._calculate_inertia(X_std, self.labels_)

        return self

    def _find_contiguous_clusters(self, cluster_id, clusters, active_clusters, W):
        """Find clusters that are spatially contiguous to given cluster."""
        members = clusters[cluster_id]
        contiguous = set()

        for member in members:
            neighbors = W[member].nonzero()[1]
            for neighbor in neighbors:
                # Find which cluster this neighbor belongs to
                for other_cluster_id in active_clusters:
                    if other_cluster_id == cluster_id:
                        continue
                    if neighbor in clusters[other_cluster_id]:
                        contiguous.add(other_cluster_id)
                        break

        return contiguous

    def _cluster_distance(self, members_i, members_j, centroid_i, centroid_j, X):
        """Calculate distance between two clusters based on linkage method."""
        if self.linkage == "single":
            # Minimum distance (single linkage)
            min_dist = np.inf
            for i in members_i:
                for j in members_j:
                    dist = np.sum((X[i] - X[j]) ** 2)
                    if dist < min_dist:
                        min_dist = dist
            return min_dist

        elif self.linkage == "complete":
            # Maximum distance (complete linkage)
            max_dist = 0
            for i in members_i:
                for j in members_j:
                    dist = np.sum((X[i] - X[j]) ** 2)
                    if dist > max_dist:
                        max_dist = dist
            return max_dist

        elif self.linkage == "average":
            # Average distance (average linkage)
            total_dist = 0
            count = 0
            for i in members_i:
                for j in members_j:
                    total_dist += np.sum((X[i] - X[j]) ** 2)
                    count += 1
            return total_dist / count if count > 0 else 0

        elif self.linkage == "ward":
            # Ward's method (minimize within-cluster variance)
            n_i = len(members_i)
            n_j = len(members_j)

            # Distance between centroids
            centroid_dist = np.sum((centroid_i - centroid_j) ** 2)

            # Ward's formula
            return (n_i * n_j) / (n_i + n_j) * centroid_dist

    def _cut_dendrogram(self, final_clusters, n_samples):
        """Create labels from final cluster assignments."""
        labels = np.full(n_samples, -1, dtype=int)

        for cluster_id, (cluster_key, members) in enumerate(final_clusters.items()):
            for member in members:
                labels[member] = cluster_id

        return labels

    def _calculate_inertia(self, X, labels):
        """Calculate total within-cluster sum of squares."""
        inertia = 0
        for label in np.unique(labels):
            if label < 0:
                continue
            cluster_members = X[labels == label]
            centroid = cluster_members.mean(axis=0)
            inertia += ((cluster_members - centroid) ** 2).sum()
        return inertia

    def plot_dendrogram(self, **kwargs):
        """
        Plot the hierarchical clustering dendrogram.

        Parameters
        ----------
        **kwargs : dict
            Additional arguments passed to scipy.cluster.hierarchy.dendrogram

        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object
        """
        if self.linkage_matrix_ is None:
            raise ValueError("Must call fit() before plotting dendrogram")

        fig, ax = plt.subplots(figsize=(10, 6))

        dendrogram(self.linkage_matrix_, ax=ax, **kwargs)

        ax.set_title(f"REDCAP Dendrogram ({self.linkage} linkage)")
        ax.set_xlabel("Observation Index")
        ax.set_ylabel("Distance")

        plt.tight_layout()
        return fig

    def predict(self, gdf):
        """
        Not implemented for REDCAP (non-parametric algorithm).

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError(
            "REDCAP is a non-parametric algorithm and cannot predict "
            "cluster membership for new observations."
        )
