"""
SKATER (Spatial 'K'luster Analysis by Tree Edge Removal).

Implements the SKATER algorithm for spatially constrained clustering using
minimum spanning trees and edge removal.

© 2025 KR-Labs. All rights reserved.

References
----------
Assunção, R. M., Neves, M. C., Câmara, G., & Da Costa Freitas, C. (2006).
    Efficient regionalization techniques for socio‐economic geographical units
    using minimum spanning trees. International Journal of Geographical
    Information Science, 20(7), 797-811.
"""

from typing import List, Optional, Union

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from sklearn.metrics import pairwise_distances


class SKATER:
    """
    Spatial 'K'luster Analysis by Tree Edge Removal.

    SKATER creates spatially contiguous regions by constructing a minimum
    spanning tree (MST) from the spatial connectivity graph and iteratively
    removing edges that maximize within-cluster homogeneity.

    Parameters
    ----------
    n_clusters : int
        Number of clusters to create
    floor : int, optional
        Minimum size for each region (default: 1)
    trace : bool, optional
        Whether to store partition history (default: False)

    Attributes
    ----------
    labels_ : ndarray of shape (n_samples,)
        Cluster labels for each observation
    tree_ : csr_matrix
        Minimum spanning tree
    inertia_ : float
        Sum of squared distances within clusters
    n_iter_ : int
        Number of edge removals performed

    Examples
    --------
    >>> from krl_geospatial.clustering import SKATER
    >>> from krl_geospatial.weights import QueenWeights
    >>>
    >>> w = QueenWeights()
    >>> w.fit(gdf)
    >>>
    >>> skater = SKATER(n_clusters=5, floor=10)
    >>> skater.fit(gdf, w, attributes=['income', 'population'])
    >>> labels = skater.labels_
    """

    def __init__(
        self,
        n_clusters: int,
        floor: int = 1,
        trace: bool = False,
    ):
        if n_clusters < 2:
            raise ValueError("n_clusters must be >= 2")
        if floor < 1:
            raise ValueError("floor must be >= 1")

        self.n_clusters = n_clusters
        self.floor = floor
        self.trace = trace

        self.labels_ = None
        self.tree_ = None
        self.inertia_ = None
        self.n_iter_ = 0
        self._partition_history = [] if trace else None

    def fit(
        self,
        gdf,
        weights,
        attributes: Union[List[str], np.ndarray],
    ):
        """
        Compute SKATER regionalization.

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
        self : SKATER
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

        # Build minimum spanning tree from spatial weights
        W = weights.to_sparse()

        # Create distance matrix based on attribute dissimilarity
        # Edge weights are attribute distances for connected neighbors
        dist = pairwise_distances(X_std, metric="euclidean")

        # Multiply W by distances to get weighted adjacency
        W_weighted = W.multiply(dist)

        # Compute MST
        self.tree_ = minimum_spanning_tree(W_weighted)

        # Initialize all observations in one cluster
        self.labels_ = np.zeros(n_samples, dtype=int)

        # Store cluster information
        clusters = {0: list(range(n_samples))}

        # Iteratively remove edges to create n_clusters
        for iteration in range(self.n_clusters - 1):
            # Find best edge to cut
            best_edge = None
            best_reduction = -np.inf
            best_labels = None

            # Try cutting each cluster that's large enough
            for cluster_id, members in clusters.items():
                if len(members) < 2 * self.floor:
                    continue  # Too small to split

                # Get subtree for this cluster
                subtree_indices = members
                subtree = self._extract_subtree(subtree_indices)

                if subtree.nnz == 0:
                    continue

                # Try removing each edge in the subtree
                for i, j in zip(*subtree.nonzero()):
                    # Check if split would violate floor constraint
                    labels_test = self._split_by_edge(subtree_indices, subtree, i, j)

                    sizes = np.bincount(labels_test)
                    if np.any(sizes < self.floor):
                        continue

                    # Calculate reduction in within-cluster variance
                    reduction = self._calculate_reduction(X_std, members, labels_test)

                    if reduction > best_reduction:
                        best_reduction = reduction
                        best_edge = (cluster_id, i, j)
                        best_labels = labels_test.copy()

            if best_edge is None:
                # Cannot split further while satisfying constraints
                break

            # Apply best split
            cluster_id, i, j = best_edge
            members = clusters[cluster_id]

            # Update cluster assignments
            new_cluster_id = max(clusters.keys()) + 1

            for idx, member_idx in enumerate(members):
                if best_labels[idx] == 1:
                    self.labels_[member_idx] = new_cluster_id

            # Update cluster dictionary
            cluster_0 = [m for idx, m in enumerate(members) if best_labels[idx] == 0]
            cluster_1 = [m for idx, m in enumerate(members) if best_labels[idx] == 1]

            del clusters[cluster_id]
            clusters[cluster_id] = cluster_0
            clusters[new_cluster_id] = cluster_1

            self.n_iter_ = iteration + 1

            if self.trace:
                self._partition_history.append(self.labels_.copy())

        # Calculate final inertia
        self.inertia_ = self._calculate_inertia(X_std, self.labels_)

        return self

    def _extract_subtree(self, indices):
        """Extract MST subtree for given node indices."""
        n = len(indices)
        index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(indices)}

        # Create subgraph
        subtree = np.zeros((n, n))

        for i, j in zip(*self.tree_.nonzero()):
            if i in index_map and j in index_map:
                new_i = index_map[i]
                new_j = index_map[j]
                subtree[new_i, new_j] = self.tree_[i, j]
                subtree[new_j, new_i] = self.tree_[j, i]

        return csr_matrix(subtree)

    def _split_by_edge(self, indices, subtree, edge_i, edge_j):
        """Split subtree by removing an edge using BFS."""
        n = len(indices)

        # Remove edge
        adj = subtree.tolil()
        adj[edge_i, edge_j] = 0
        adj[edge_j, edge_i] = 0
        adj = adj.tocsr()

        # BFS to find connected components
        labels = np.full(n, -1, dtype=int)
        component_id = 0

        for start_node in range(n):
            if labels[start_node] != -1:
                continue

            # BFS from start_node
            queue = [start_node]
            labels[start_node] = component_id

            while queue:
                node = queue.pop(0)
                neighbors = adj[node].nonzero()[1]

                for neighbor in neighbors:
                    if labels[neighbor] == -1:
                        labels[neighbor] = component_id
                        queue.append(neighbor)

            component_id += 1

        return labels

    def _calculate_reduction(self, X, members, split_labels):
        """Calculate reduction in sum of squared errors from split."""
        X_subset = X[members]

        # Original SSE
        centroid = X_subset.mean(axis=0)
        sse_original = ((X_subset - centroid) ** 2).sum()

        # SSE after split
        sse_split = 0
        for label in np.unique(split_labels):
            cluster_members = X_subset[split_labels == label]
            cluster_centroid = cluster_members.mean(axis=0)
            sse_split += ((cluster_members - cluster_centroid) ** 2).sum()

        return sse_original - sse_split

    def _calculate_inertia(self, X, labels):
        """Calculate total within-cluster sum of squares."""
        inertia = 0
        for label in np.unique(labels):
            cluster_members = X[labels == label]
            centroid = cluster_members.mean(axis=0)
            inertia += ((cluster_members - centroid) ** 2).sum()
        return inertia

    def predict(self, gdf):
        """
        Not implemented for SKATER (non-parametric algorithm).

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError(
            "SKATER is a non-parametric algorithm and cannot predict "
            "cluster membership for new observations."
        )
