"""
Base classes for spatial weights.

This module provides the abstract base class for all spatial weight matrices
and common utilities for weight manipulation and standardization.
"""

import warnings
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import geopandas as gpd
import numpy as np
import pandas as pd
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from scipy import sparse

logger = get_logger(__name__)


class SpatialWeights(ABC):
    """
    Abstract base class for spatial weight matrices.

    Spatial weights define the neighborhood structure between spatial units,
    essential for spatial autocorrelation analysis and spatial regression models.

    Attributes:
        weights (Dict[int, List[float]]): Dictionary mapping observation index to weights
        neighbors (Dict[int, List[int]]): Dictionary mapping observation index to neighbor indices
        n (int): Number of observations
        is_standardized (bool): Whether weights are row-standardized
    """

    def __init__(self):
        """Initialize a SpatialWeights object."""
        self.weights: Dict[int, List[float]] = {}
        self.neighbors: Dict[int, List[int]] = {}
        self.n: int = 0
        self.is_standardized: bool = False
        self._fitted: bool = False
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def fit(self, gdf: gpd.GeoDataFrame) -> "SpatialWeights":
        """
        Compute spatial weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing geometries

        Returns:
            self: Fitted SpatialWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty
        """
        pass

    def _validate_geodataframe(self, gdf: gpd.GeoDataFrame) -> None:
        """
        Validate GeoDataFrame for spatial weights computation.

        Args:
            gdf: GeoDataFrame to validate

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise ValueError("Input must be a GeoDataFrame")

        if len(gdf) == 0:
            raise ValueError("GeoDataFrame cannot be empty")

        if gdf.geometry.isna().any():
            raise ValueError("GeoDataFrame contains null geometries")

        # Warn about geographic CRS
        if gdf.crs and gdf.crs.is_geographic:
            warnings.warn(
                "GeoDataFrame has a geographic CRS. Distance-based operations "
                "may be inaccurate. Consider reprojecting to a projected CRS.",
                UserWarning,
            )

    def standardize(self, inplace: bool = True) -> Optional["SpatialWeights"]:
        """
        Row-standardize the spatial weights.

        Row standardization ensures that weights for each observation sum to 1,
        which is common in spatial econometrics to facilitate interpretation.

        Args:
            inplace: If True, modify weights in-place. If False, return new object.

        Returns:
            None if inplace=True, otherwise new standardized SpatialWeights object

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before standardization. "
                "Call fit() first."
            )

        if self.is_standardized:
            logger.warning("Weights are already standardized")
            if not inplace:
                return self._copy()
            return None

        target = self if inplace else self._copy()

        for i in target.neighbors.keys():
            w_sum = sum(target.weights[i])
            if w_sum > 0:
                target.weights[i] = [w / w_sum for w in target.weights[i]]
            else:
                # Handle isolated observations (no neighbors)
                target.weights[i] = target.weights[i]

        target.is_standardized = True
        logger.info("Weights standardized")

        if not inplace:
            return target
        return None

    def to_sparse(self) -> sparse.csr_matrix:
        """
        Convert spatial weights to a sparse matrix.

        Returns:
            Sparse matrix representation in CSR format

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before conversion. " "Call fit() first."
            )

        row_indices = []
        col_indices = []
        data = []

        for i in range(self.n):
            if i in self.neighbors:
                for j, w in zip(self.neighbors[i], self.weights[i]):
                    row_indices.append(i)
                    col_indices.append(j)
                    data.append(w)

        return sparse.csr_matrix((data, (row_indices, col_indices)), shape=(self.n, self.n))

    def to_dense(self) -> np.ndarray:
        """
        Convert spatial weights to a dense matrix.

        Warning: This can be memory-intensive for large datasets.

        Returns:
            Dense numpy array representation

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before conversion. " "Call fit() first."
            )

        matrix = np.zeros((self.n, self.n))

        for i in range(self.n):
            if i in self.neighbors:
                for j, w in zip(self.neighbors[i], self.weights[i]):
                    matrix[i, j] = w

        return matrix

    def cardinality(self) -> Dict[str, Union[int, float, List[int]]]:
        """
        Compute cardinality statistics (neighborhood sizes).

        Returns:
            Dictionary with statistics:
                - min: Minimum number of neighbors
                - max: Maximum number of neighbors
                - mean: Mean number of neighbors
                - median: Median number of neighbors
                - islands: List of observation indices with no neighbors

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before computing cardinality. "
                "Call fit() first."
            )

        neighbor_counts = [len(self.neighbors.get(i, [])) for i in range(self.n)]
        islands = [i for i in range(self.n) if len(self.neighbors.get(i, [])) == 0]

        return {
            "min": min(neighbor_counts),
            "max": max(neighbor_counts),
            "mean": np.mean(neighbor_counts),
            "median": np.median(neighbor_counts),
            "islands": islands,
        }

    def symmetry_check(self) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Check if the spatial weights matrix is symmetric.

        Returns:
            Tuple of (is_symmetric, asymmetric_pairs)
            - is_symmetric: True if matrix is symmetric
            - asymmetric_pairs: List of (i, j) pairs where w[i,j] != w[j,i]

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before symmetry check. "
                "Call fit() first."
            )

        asymmetric = []

        for i in range(self.n):
            if i not in self.neighbors:
                continue

            for j_idx, j in enumerate(self.neighbors[i]):
                w_ij = self.weights[i][j_idx]

                # Check if j has i as neighbor
                if j not in self.neighbors or i not in self.neighbors[j]:
                    asymmetric.append((i, j))
                    continue

                # Find weight w_ji
                i_idx = self.neighbors[j].index(i)
                w_ji = self.weights[j][i_idx]

                # Check if weights are equal (within tolerance)
                if not np.isclose(w_ij, w_ji):
                    if (j, i) not in asymmetric:  # Avoid duplicates
                        asymmetric.append((i, j))

        return len(asymmetric) == 0, asymmetric

    def _copy(self) -> "SpatialWeights":
        """
        Create a deep copy of the SpatialWeights object.

        Returns:
            Deep copy of this object
        """
        import copy

        return copy.deepcopy(self)

    def summary(self) -> pd.DataFrame:
        """
        Generate a summary of the spatial weights.

        Returns:
            DataFrame with summary statistics

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before summary. " "Call fit() first."
            )

        cardinality_stats = self.cardinality()
        is_symmetric, _ = self.symmetry_check()

        # Calculate sparsity
        non_zero = sum(len(neighbors) for neighbors in self.neighbors.values())
        total_cells = self.n * self.n
        sparsity = 1 - (non_zero / total_cells) if total_cells > 0 else 1.0

        summary_data = {
            "Property": [
                "Number of observations",
                "Min neighbors",
                "Max neighbors",
                "Mean neighbors",
                "Median neighbors",
                "Islands (no neighbors)",
                "Standardized",
                "Symmetric",
                "Sparsity",
            ],
            "Value": [
                self.n,
                cardinality_stats["min"],
                cardinality_stats["max"],
                f"{cardinality_stats['mean']:.2f}",
                cardinality_stats["median"],
                len(cardinality_stats["islands"]),
                self.is_standardized,
                is_symmetric,
                f"{sparsity:.4f}",
            ],
        }

        return pd.DataFrame(summary_data)

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return f"{self.__class__.__name__}(fitted=False)"

        return f"{self.__class__.__name__}(n={self.n}, " f"standardized={self.is_standardized})"
