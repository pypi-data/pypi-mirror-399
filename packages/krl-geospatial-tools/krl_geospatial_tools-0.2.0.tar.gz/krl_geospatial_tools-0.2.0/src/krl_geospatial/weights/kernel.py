"""
Kernel-based spatial weights.

This module provides classes for constructing spatial weights using
kernel functions that decay smoothly with distance.
"""

from typing import Literal, Optional, Union

import geopandas as gpd
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from libpysal.weights import Kernel as LibPySAL_Kernel

from .base import SpatialWeights

logger = get_logger(__name__)

KernelType = Literal["triangular", "uniform", "quadratic", "quartic", "gaussian"]


class KernelWeights(SpatialWeights):
    """
    Kernel-based spatial weights.

    Weights are computed using a kernel function that decays with distance.
    Common kernels include Gaussian, Epanechnikov (quadratic), and triangular.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import KernelWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute Gaussian kernel weights with bandwidth=1000
        w = KernelWeights(
            kernel='gaussian',
            bandwidth=1000
        ).fit(gdf)

        # Kernel weights are typically used unstandardized
        # But can be standardized if needed
        w.standardize()
        ```

    Attributes:
        kernel (str): Type of kernel function ('triangular', 'uniform', 'quadratic',
                     'quartic', 'gaussian')
        bandwidth (float): Bandwidth parameter controlling decay rate
        fixed (bool): If True, use fixed bandwidth. If False, use adaptive bandwidth.
        k (Optional[int]): For adaptive bandwidth, number of nearest neighbors
    """

    def __init__(
        self,
        kernel: KernelType = "gaussian",
        bandwidth: Optional[float] = None,
        fixed: bool = True,
        k: Optional[int] = None,
    ):
        """
        Initialize kernel weights.

        Args:
            kernel: Type of kernel function
            bandwidth: Bandwidth parameter. If None and fixed=True, will be estimated.
                      Ignored if fixed=False.
            fixed: If True, use fixed bandwidth. If False, use adaptive bandwidth
                   based on k nearest neighbors.
            k: Number of nearest neighbors for adaptive bandwidth. Required if fixed=False.

        Raises:
            ValueError: If invalid parameters are provided
        """
        super().__init__()

        valid_kernels = ["triangular", "uniform", "quadratic", "quartic", "gaussian"]
        if kernel not in valid_kernels:
            raise ValueError(f"kernel must be one of {valid_kernels}, got '{kernel}'")

        if not fixed and k is None:
            raise ValueError("k must be specified when fixed=False (adaptive bandwidth)")

        if not fixed and k is not None and k < 1:
            raise ValueError("k must be at least 1")

        if bandwidth is not None and bandwidth <= 0:
            raise ValueError("bandwidth must be positive")

        self.kernel = kernel
        self.bandwidth = bandwidth
        self.fixed = fixed
        self.k = k

        logger.info(
            f"Initialized KernelWeights with kernel={kernel}, "
            f"bandwidth={bandwidth}, fixed={fixed}, k={k}"
        )

    def fit(self, gdf: gpd.GeoDataFrame) -> "KernelWeights":
        """
        Compute kernel weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing geometries

        Returns:
            self: Fitted KernelWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty
        """
        self._validate_geodataframe(gdf)

        if not self.fixed and self.k is not None and self.k >= len(gdf):
            raise ValueError(f"k ({self.k}) must be less than number of observations ({len(gdf)})")

        logger.info(
            f"Computing {self.kernel} kernel weights "
            f"(bandwidth={self.bandwidth}, fixed={self.fixed}, k={self.k}) "
            f"for {len(gdf)} observations"
        )

        # Use libpysal to compute weights
        # Note: libpysal Kernel requires k even for fixed bandwidth
        # Use k=12 as default for fixed bandwidth (reasonable for most datasets)
        k_param = self.k if self.k is not None else 12

        w_pysal = LibPySAL_Kernel.from_dataframe(
            gdf,
            function=self.kernel,
            bandwidth=self.bandwidth,
            fixed=self.fixed,
            k=k_param,
            use_index=False,
        )

        # Convert to our format
        self.n = w_pysal.n
        self.neighbors = dict(w_pysal.neighbors)
        self.weights = dict(w_pysal.weights)
        self._fitted = True

        # Store the actual bandwidth used (libpysal may estimate it)
        if hasattr(w_pysal, "bandwidth"):
            if isinstance(w_pysal.bandwidth, (list, np.ndarray)):
                # Adaptive bandwidth
                self._actual_bandwidth = np.array(w_pysal.bandwidth)
            else:
                # Fixed bandwidth
                self._actual_bandwidth = w_pysal.bandwidth

        cardinality = self.cardinality()
        logger.info(
            f"Kernel weights computed: {self.n} observations, "
            f"mean neighbors={cardinality['mean']:.2f}"
        )

        return self

    def get_bandwidth(self) -> Union[float, np.ndarray]:
        """
        Get the bandwidth parameter used.

        For fixed bandwidth, returns a scalar.
        For adaptive bandwidth, returns an array of bandwidths per observation.

        Returns:
            Bandwidth value(s)

        Raises:
            ValueError: If weights have not been computed
        """
        if not self._fitted:
            raise ValueError(
                f"{self.__class__.__name__} must be fitted before accessing bandwidth. "
                "Call fit() first."
            )

        return self._actual_bandwidth

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return (
                f"KernelWeights(kernel='{self.kernel}', bandwidth={self.bandwidth}, "
                f"fixed={self.fixed}, k={self.k}, fitted=False)"
            )

        bw_str = f"{self.bandwidth}" if self.fixed else f"adaptive(k={self.k})"
        return (
            f"KernelWeights(kernel='{self.kernel}', bandwidth={bw_str}, "
            f"n={self.n}, standardized={self.is_standardized})"
        )


class GaussianWeights(KernelWeights):
    """
    Gaussian kernel spatial weights.

    Weights follow a Gaussian (normal) distribution:
    w_ij = exp(-d_ij^2 / (2 * bandwidth^2))

    This is a convenience class for KernelWeights with kernel='gaussian'.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import GaussianWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute Gaussian kernel weights
        w = GaussianWeights(bandwidth=1000).fit(gdf)
        ```
    """

    def __init__(
        self, bandwidth: Optional[float] = None, fixed: bool = True, k: Optional[int] = None
    ):
        """
        Initialize Gaussian kernel weights.

        Args:
            bandwidth: Bandwidth parameter. If None and fixed=True, will be estimated.
            fixed: If True, use fixed bandwidth. If False, adaptive based on k.
            k: Number of nearest neighbors for adaptive bandwidth.
        """
        super().__init__(kernel="gaussian", bandwidth=bandwidth, fixed=fixed, k=k)


class EpanechnikovWeights(KernelWeights):
    """
    Epanechnikov (quadratic) kernel spatial weights.

    Weights follow a quadratic function:
    w_ij = (1 - (d_ij / bandwidth)^2) for d_ij <= bandwidth, else 0

    This is a convenience class for KernelWeights with kernel='quadratic'.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import EpanechnikovWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute Epanechnikov kernel weights
        w = EpanechnikovWeights(bandwidth=1000).fit(gdf)
        ```
    """

    def __init__(
        self, bandwidth: Optional[float] = None, fixed: bool = True, k: Optional[int] = None
    ):
        """
        Initialize Epanechnikov kernel weights.

        Args:
            bandwidth: Bandwidth parameter. If None and fixed=True, will be estimated.
            fixed: If True, use fixed bandwidth. If False, adaptive based on k.
            k: Number of nearest neighbors for adaptive bandwidth.
        """
        super().__init__(kernel="quadratic", bandwidth=bandwidth, fixed=fixed, k=k)


class TriangularWeights(KernelWeights):
    """
    Triangular kernel spatial weights.

    Weights follow a triangular (linear) decay:
    w_ij = (1 - d_ij / bandwidth) for d_ij <= bandwidth, else 0

    This is a convenience class for KernelWeights with kernel='triangular'.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import TriangularWeights

        # Load data
        gdf = gpd.read_file("points.shp")

        # Compute triangular kernel weights
        w = TriangularWeights(bandwidth=1000).fit(gdf)
        ```
    """

    def __init__(
        self, bandwidth: Optional[float] = None, fixed: bool = True, k: Optional[int] = None
    ):
        """
        Initialize triangular kernel weights.

        Args:
            bandwidth: Bandwidth parameter. If None and fixed=True, will be estimated.
            fixed: If True, use fixed bandwidth. If False, adaptive based on k.
            k: Number of nearest neighbors for adaptive bandwidth.
        """
        super().__init__(kernel="triangular", bandwidth=bandwidth, fixed=fixed, k=k)
