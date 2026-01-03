"""
Max-p regionalization algorithm.

Implements the max-p regions problem: find the maximum number of regions
such that each region satisfies a threshold constraint while minimizing
within-region heterogeneity.

© 2025 KR-Labs. All rights reserved.

References
----------
Duque, J. C., Anselin, L., & Rey, S. J. (2012). The max‐p‐regions problem.
    Journal of Regional Science, 52(3), 397-419.
"""

from typing import Callable, List, Optional, Union

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


class MaxP:
    """
    Max-p regions problem solver.

    Finds the maximum number of spatially contiguous regions such that each
    region satisfies a threshold constraint (e.g., minimum population) while
    minimizing within-region heterogeneity.

    Parameters
    ----------
    threshold : float
        Minimum threshold value each region must satisfy
    threshold_variable : str or ndarray
        Variable name or data for threshold constraint
    top_n : int, optional
        Number of top candidates to consider in region growing (default: 10)
    max_iterations : int, optional
        Maximum iterations for construction phase (default: 100)
    random_state : int, optional
        Random seed for reproducibility

    Attributes
    ----------
    labels_ : ndarray of shape (n_samples,)
        Region labels for each observation
    n_regions_ : int
        Number of regions created (the 'p' value)
    inertia_ : float
        Sum of squared distances within regions
    threshold_satisfied_ : bool
        Whether all regions satisfy the threshold

    Examples
    --------
    >>> from krl_geospatial.clustering import MaxP
    >>> from krl_geospatial.weights import QueenWeights
    >>>
    >>> w = QueenWeights()
    >>> w.fit(gdf)
    >>>
    >>> maxp = MaxP(
    ...     threshold=10000,
    ...     threshold_variable='population',
    ...     random_state=42
    ... )
    >>> maxp.fit(gdf, w, attributes=['income', 'density'])
    >>> print(f"Created {maxp.n_regions_} regions")
    """

    def __init__(
        self,
        threshold: float,
        threshold_variable: Union[str, np.ndarray],
        top_n: int = 10,
        max_iterations: int = 100,
        random_state: Optional[int] = None,
    ):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if top_n < 1:
            raise ValueError("top_n must be >= 1")

        self.threshold = threshold
        self.threshold_variable = threshold_variable
        self.top_n = top_n
        self.max_iterations = max_iterations
        self.random_state = random_state

        self.labels_ = None
        self.n_regions_ = 0
        self.inertia_ = None
        self.threshold_satisfied_ = True

        self._rng = np.random.default_rng(random_state)

    def fit(
        self,
        gdf,
        weights,
        attributes: Union[List[str], np.ndarray],
    ):
        """
        Compute max-p regionalization.

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
        self : MaxP
            Fitted estimator
        """
        # Extract attribute data
        if isinstance(attributes, (list, tuple)):
            X = gdf[attributes].values
        else:
            X = np.asarray(attributes)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        # Extract threshold variable
        if isinstance(self.threshold_variable, str):
            threshold_data = gdf[self.threshold_variable].values
        else:
            threshold_data = np.asarray(self.threshold_variable)

        n_samples = X.shape[0]

        # Standardize attributes for distance calculation
        X_std = (X - X.mean(axis=0)) / X.std(axis=0)

        # Get spatial weights as adjacency
        W = weights.to_sparse()

        # Initialize labels (-1 = unassigned)
        self.labels_ = np.full(n_samples, -1, dtype=int)

        # Construction phase: grow regions
        region_id = 0
        unassigned = set(range(n_samples))

        for iteration in range(self.max_iterations):
            if not unassigned:
                break

            # Select random seed from unassigned
            seed = self._rng.choice(list(unassigned))

            # Try to grow region from seed
            region = self._grow_region(seed, unassigned, X_std, threshold_data, W)

            if region is not None:
                # Assign region
                for node in region:
                    self.labels_[node] = region_id
                    unassigned.discard(node)
                region_id += 1
            else:
                # Cannot satisfy threshold from this seed
                unassigned.discard(seed)
                # Assign to nearest existing region
                if region_id > 0:
                    self.labels_[seed] = self._assign_to_nearest_region(seed, X_std, W)

        # Handle any remaining unassigned (assign to neighbors)
        for node in list(unassigned):
            if region_id == 0:
                # No regions created, create one
                self.labels_[node] = 0
                region_id = 1
            else:
                self.labels_[node] = self._assign_to_nearest_region(node, X_std, W)

        self.n_regions_ = len(np.unique(self.labels_))

        # Check threshold satisfaction
        self.threshold_satisfied_ = all(
            threshold_data[self.labels_ == r].sum() >= self.threshold
            for r in range(self.n_regions_)
        )

        # Calculate inertia
        self.inertia_ = self._calculate_inertia(X_std, self.labels_)

        return self

    def _grow_region(self, seed, unassigned, X, threshold_data, W):
        """
        Grow a region from a seed node.

        Returns list of nodes if threshold can be satisfied, None otherwise.
        """
        region = [seed]
        region_set = {seed}
        region_sum = threshold_data[seed]

        # Get region centroid
        centroid = X[seed].copy()

        while region_sum < self.threshold:
            # Find candidate neighbors
            candidates = []

            for node in region:
                neighbors = W[node].nonzero()[1]
                for neighbor in neighbors:
                    if neighbor in unassigned and neighbor not in region_set:
                        # Calculate distance to centroid
                        dist = np.sum((X[neighbor] - centroid) ** 2)
                        candidates.append((neighbor, dist))

            if not candidates:
                # No more candidates available
                return None

            # Sort by distance and select top candidates
            candidates = sorted(candidates, key=lambda x: x[1])
            top_candidates = candidates[: self.top_n]

            # Randomly select from top candidates
            if top_candidates:
                selected = self._rng.choice([c[0] for c in top_candidates])
                region.append(selected)
                region_set.add(selected)
                region_sum += threshold_data[selected]

                # Update centroid
                centroid = X[list(region)].mean(axis=0)
            else:
                return None

        return region

    def _assign_to_nearest_region(self, node, X, W):
        """Assign node to nearest existing region among neighbors."""
        neighbors = W[node].nonzero()[1]

        # Find labeled neighbors
        labeled_neighbors = [n for n in neighbors if self.labels_[n] >= 0]

        if not labeled_neighbors:
            # No labeled neighbors, find any labeled node
            labeled = np.where(self.labels_ >= 0)[0]
            if len(labeled) == 0:
                return 0

            # Find closest labeled node
            dists = np.sum((X[labeled] - X[node]) ** 2, axis=1)
            closest = labeled[np.argmin(dists)]
            return self.labels_[closest]

        # Find closest labeled neighbor
        dists = np.sum((X[labeled_neighbors] - X[node]) ** 2, axis=1)
        closest = labeled_neighbors[np.argmin(dists)]
        return self.labels_[closest]

    def _calculate_inertia(self, X, labels):
        """Calculate total within-region sum of squares."""
        inertia = 0
        for label in np.unique(labels):
            if label < 0:
                continue
            region_members = X[labels == label]
            centroid = region_members.mean(axis=0)
            inertia += ((region_members - centroid) ** 2).sum()
        return inertia

    def predict(self, gdf):
        """
        Not implemented for Max-p (non-parametric algorithm).

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError(
            "Max-p is a non-parametric algorithm and cannot predict "
            "region membership for new observations."
        )
