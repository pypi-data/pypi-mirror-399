"""
Distance-based spatial weights.

This module provides classes for constructing spatial weights based on
distances between observations (points or polygon centroids).
"""

from typing import Optional

import geopandas as gpd
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from libpysal.weights import KNN as LibPySAL_KNN
from libpysal.weights import DistanceBand as LibPySAL_DistanceBand

from .base import SpatialWeights

logger = get_logger(__name__)


class KNNWeights(SpatialWeights):
    """
    K-Nearest Neighbors spatial weights.

    Each observation is connected to its k nearest neighbors based on
    Euclidean distance between centroids.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import KNNWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute KNN weights (5 nearest neighbors)
        w = KNNWeights(k=5).fit(gdf)

        # Standardize weights
        w.standardize()
        ```

    Attributes:
        k (int): Number of nearest neighbors
        p (float): Minkowski p-norm distance metric (1=Manhattan, 2=Euclidean)
    """

    def __init__(self, k: int = 4, p: float = 2.0):
        """
        Initialize K-Nearest Neighbors weights.

        Args:
            k: Number of nearest neighbors
            p: Minkowski p-norm (1=Manhattan, 2=Euclidean)

        Raises:
            ValueError: If k < 1 or p <= 0
        """
        super().__init__()

        if k < 1:
            raise ValueError("k must be at least 1")
        if p <= 0:
            raise ValueError("p must be positive")

        self.k = k
        self.p = p
        logger.info(f"Initialized KNNWeights with k={k}, p={p}")

    def fit(self, gdf: gpd.GeoDataFrame) -> "KNNWeights":
        """
        Compute KNN weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing geometries

        Returns:
            self: Fitted KNNWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty, or k >= n
        """
        self._validate_geodataframe(gdf)

        if self.k >= len(gdf):
            raise ValueError(f"k ({self.k}) must be less than number of observations ({len(gdf)})")

        logger.info(f"Computing KNN weights (k={self.k}, p={self.p}) for {len(gdf)} observations")

        # Use libpysal to compute weights
        w_pysal = LibPySAL_KNN.from_dataframe(gdf, k=self.k, p=self.p, use_index=False)

        # Convert to our format
        self.n = w_pysal.n
        self.neighbors = dict(w_pysal.neighbors)
        self.weights = dict(w_pysal.weights)
        self._fitted = True

        cardinality = self.cardinality()
        logger.info(
            f"KNN weights computed: {self.n} observations, "
            f"mean neighbors={cardinality['mean']:.2f}"
        )

        return self

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return f"KNNWeights(k={self.k}, p={self.p}, fitted=False)"

        return (
            f"KNNWeights(k={self.k}, p={self.p}, n={self.n}, "
            f"standardized={self.is_standardized})"
        )


class DistanceBandWeights(SpatialWeights):
    """
    Distance band spatial weights.

    Observations within a specified distance threshold are considered neighbors.
    All neighbors within the threshold receive equal weight (binary weights).

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import DistanceBandWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute distance band weights (1000m threshold)
        w = DistanceBandWeights(threshold=1000).fit(gdf)

        # Check for islands
        cardinality = w.cardinality()
        if cardinality['islands']:
            print(f"Warning: {len(cardinality['islands'])} isolated observations")
        ```

    Attributes:
        threshold (float): Distance threshold for defining neighbors
        p (float): Minkowski p-norm distance metric (1=Manhattan, 2=Euclidean)
        binary (bool): If True, use binary weights. If False, use inverse distance.
    """

    def __init__(self, threshold: float, p: float = 2.0, binary: bool = True):
        """
        Initialize distance band weights.

        Args:
            threshold: Maximum distance for neighbors
            p: Minkowski p-norm (1=Manhattan, 2=Euclidean)
            binary: If True, binary weights. If False, inverse distance weights.

        Raises:
            ValueError: If threshold <= 0 or p <= 0
        """
        super().__init__()

        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if p <= 0:
            raise ValueError("p must be positive")

        self.threshold = threshold
        self.p = p
        self.binary = binary
        logger.info(
            f"Initialized DistanceBandWeights with threshold={threshold}, "
            f"p={p}, binary={binary}"
        )

    def fit(self, gdf: gpd.GeoDataFrame) -> "DistanceBandWeights":
        """
        Compute distance band weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing geometries

        Returns:
            self: Fitted DistanceBandWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty
        """
        self._validate_geodataframe(gdf)

        logger.info(
            f"Computing distance band weights (threshold={self.threshold}, "
            f"p={self.p}, binary={self.binary}) for {len(gdf)} observations"
        )

        # Use libpysal to compute weights
        w_pysal = LibPySAL_DistanceBand.from_dataframe(
            gdf, threshold=self.threshold, p=self.p, binary=self.binary, use_index=False
        )

        # Convert to our format
        self.n = w_pysal.n
        self.neighbors = dict(w_pysal.neighbors)
        self.weights = dict(w_pysal.weights)
        self._fitted = True

        cardinality = self.cardinality()
        logger.info(
            f"Distance band weights computed: {self.n} observations, "
            f"mean neighbors={cardinality['mean']:.2f}, "
            f"islands={len(cardinality['islands'])}"
        )

        if cardinality["islands"]:
            logger.warning(
                f"Found {len(cardinality['islands'])} islands (no neighbors within threshold). "
                "Consider increasing the threshold."
            )

        return self

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return (
                f"DistanceBandWeights(threshold={self.threshold}, p={self.p}, "
                f"binary={self.binary}, fitted=False)"
            )

        return (
            f"DistanceBandWeights(threshold={self.threshold}, p={self.p}, "
            f"binary={self.binary}, n={self.n}, standardized={self.is_standardized})"
        )


class InverseDistanceWeights(SpatialWeights):
    """
    Inverse distance spatial weights.

    Weights are computed as the inverse of distance raised to a power.
    Closer observations receive higher weights: w_ij = 1 / d_ij^alpha

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import InverseDistanceWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute inverse distance weights (alpha=1.0, within 5000m)
        w = InverseDistanceWeights(alpha=1.0, threshold=5000).fit(gdf)

        # Standardize weights
        w.standardize()
        ```

    Attributes:
        alpha (float): Distance decay parameter (higher = faster decay)
        threshold (Optional[float]): Maximum distance. If None, all pairs are neighbors.
        p (float): Minkowski p-norm distance metric (1=Manhattan, 2=Euclidean)
    """

    def __init__(self, alpha: float = 1.0, threshold: Optional[float] = None, p: float = 2.0):
        """
        Initialize inverse distance weights.

        Args:
            alpha: Distance decay parameter (typically 1.0 or 2.0)
            threshold: Maximum distance for neighbors. If None, all pairs are neighbors.
            p: Minkowski p-norm (1=Manhattan, 2=Euclidean)

        Raises:
            ValueError: If alpha <= 0, threshold <= 0, or p <= 0
        """
        super().__init__()

        if alpha <= 0:
            raise ValueError("alpha must be positive")
        if threshold is not None and threshold <= 0:
            raise ValueError("threshold must be positive")
        if p <= 0:
            raise ValueError("p must be positive")

        self.alpha = alpha
        self.threshold = threshold
        self.p = p
        logger.info(
            f"Initialized InverseDistanceWeights with alpha={alpha}, "
            f"threshold={threshold}, p={p}"
        )

    def fit(self, gdf: gpd.GeoDataFrame) -> "InverseDistanceWeights":
        """
        Compute inverse distance weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing geometries

        Returns:
            self: Fitted InverseDistanceWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty
        """
        self._validate_geodataframe(gdf)

        logger.info(
            f"Computing inverse distance weights (alpha={self.alpha}, "
            f"threshold={self.threshold}, p={self.p}) for {len(gdf)} observations"
        )

        # Extract coordinates (use centroids for polygons)
        coords = np.array([(geom.centroid.x, geom.centroid.y) for geom in gdf.geometry])

        self.n = len(gdf)
        self.neighbors = {}
        self.weights = {}

        # Compute pairwise distances and weights
        for i in range(self.n):
            neighbors = []
            weights = []

            for j in range(self.n):
                if i == j:
                    continue

                # Compute distance
                if self.p == 2:
                    dist = np.sqrt(np.sum((coords[i] - coords[j]) ** 2))
                else:
                    dist = np.sum(np.abs(coords[i] - coords[j]) ** self.p) ** (1 / self.p)

                # Check threshold
                if self.threshold is not None and dist > self.threshold:
                    continue

                # Compute inverse distance weight
                if dist > 0:
                    weight = 1.0 / (dist**self.alpha)
                    neighbors.append(j)
                    weights.append(weight)

            self.neighbors[i] = neighbors
            self.weights[i] = weights

        self._fitted = True

        cardinality = self.cardinality()
        logger.info(
            f"Inverse distance weights computed: {self.n} observations, "
            f"mean neighbors={cardinality['mean']:.2f}, "
            f"islands={len(cardinality['islands'])}"
        )

        if cardinality["islands"]:
            logger.warning(
                f"Found {len(cardinality['islands'])} islands. "
                "Consider increasing the threshold or setting threshold=None."
            )

        return self

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return (
                f"InverseDistanceWeights(alpha={self.alpha}, "
                f"threshold={self.threshold}, p={self.p}, fitted=False)"
            )

        return (
            f"InverseDistanceWeights(alpha={self.alpha}, "
            f"threshold={self.threshold}, p={self.p}, n={self.n}, "
            f"standardized={self.is_standardized})"
        )
