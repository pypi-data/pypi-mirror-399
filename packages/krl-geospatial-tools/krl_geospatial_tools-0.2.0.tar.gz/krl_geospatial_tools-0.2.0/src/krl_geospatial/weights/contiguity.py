"""
Contiguity-based spatial weights.

This module provides classes for constructing spatial weights based on
shared boundaries (contiguity) between polygons.
"""

from typing import Optional

import geopandas as gpd
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from libpysal.weights import Queen as LibPySAL_Queen
from libpysal.weights import Rook as LibPySAL_Rook

from .base import SpatialWeights

logger = get_logger(__name__)


class QueenWeights(SpatialWeights):
    """
    Queen contiguity spatial weights.

    Two polygons are considered neighbors if they share at least one vertex
    (corner or edge). This is more inclusive than Rook contiguity.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import QueenWeights

        # Load polygon data
        gdf = gpd.read_file("counties.shp")

        # Compute Queen contiguity weights
        w = QueenWeights().fit(gdf)

        # Standardize weights
        w.standardize()

        # Get summary statistics
        print(w.summary())
        ```

    Attributes:
        order (int): Order of contiguity (1=first-order, 2=second-order, etc.)
    """

    def __init__(self, order: int = 1):
        """
        Initialize Queen contiguity weights.

        Args:
            order: Order of contiguity. 1 = immediate neighbors,
                   2 = neighbors of neighbors, etc.

        Raises:
            ValueError: If order is less than 1
        """
        super().__init__()

        if order < 1:
            raise ValueError("Order must be at least 1")

        self.order = order
        logger.info(f"Initialized QueenWeights with order={order}")

    def fit(self, gdf: gpd.GeoDataFrame) -> "QueenWeights":
        """
        Compute Queen contiguity weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing polygon geometries

        Returns:
            self: Fitted QueenWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty
            TypeError: If geometries are not polygons
        """
        self._validate_geodataframe(gdf)

        # Check geometry types
        geom_types = gdf.geometry.geom_type.unique()
        if not all(gt in ["Polygon", "MultiPolygon"] for gt in geom_types):
            raise TypeError("Queen contiguity requires polygon geometries. " f"Found: {geom_types}")

        logger.info(
            f"Computing Queen contiguity weights (order={self.order}) for {len(gdf)} polygons"
        )

        if self.order > 1:
            logger.warning(
                "Higher-order contiguity (order > 1) is not fully supported. "
                "Using first-order contiguity."
            )

        # Use libpysal to compute weights
        w_pysal = LibPySAL_Queen.from_dataframe(gdf, use_index=False)

        # Convert to our format
        self.n = w_pysal.n
        self.neighbors = dict(w_pysal.neighbors)
        self.weights = dict(w_pysal.weights)
        self._fitted = True

        cardinality = self.cardinality()
        logger.info(
            f"Queen weights computed: {self.n} observations, "
            f"mean neighbors={cardinality['mean']:.2f}, "
            f"islands={len(cardinality['islands'])}"
        )

        return self

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return f"QueenWeights(order={self.order}, fitted=False)"

        return (
            f"QueenWeights(order={self.order}, n={self.n}, " f"standardized={self.is_standardized})"
        )


class RookWeights(SpatialWeights):
    """
    Rook contiguity spatial weights.

    Two polygons are considered neighbors if they share a common edge
    (but not just a corner). This is more restrictive than Queen contiguity.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.weights import RookWeights

        # Load polygon data
        gdf = gpd.read_file("counties.shp")

        # Compute Rook contiguity weights
        w = RookWeights().fit(gdf)

        # Standardize weights
        w.standardize()

        # Check for islands (polygons with no neighbors)
        cardinality = w.cardinality()
        if cardinality['islands']:
            print(f"Found {len(cardinality['islands'])} islands")
        ```

    Attributes:
        order (int): Order of contiguity (1=first-order, 2=second-order, etc.)
    """

    def __init__(self, order: int = 1):
        """
        Initialize Rook contiguity weights.

        Args:
            order: Order of contiguity. 1 = immediate neighbors,
                   2 = neighbors of neighbors, etc.

        Raises:
            ValueError: If order is less than 1
        """
        super().__init__()

        if order < 1:
            raise ValueError("Order must be at least 1")

        self.order = order
        logger.info(f"Initialized RookWeights with order={order}")

    def fit(self, gdf: gpd.GeoDataFrame) -> "RookWeights":
        """
        Compute Rook contiguity weights from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame containing polygon geometries

        Returns:
            self: Fitted RookWeights object

        Raises:
            ValueError: If GeoDataFrame is invalid or empty
            TypeError: If geometries are not polygons
        """
        self._validate_geodataframe(gdf)

        # Check geometry types
        geom_types = gdf.geometry.geom_type.unique()
        if not all(gt in ["Polygon", "MultiPolygon"] for gt in geom_types):
            raise TypeError("Rook contiguity requires polygon geometries. " f"Found: {geom_types}")

        logger.info(
            f"Computing Rook contiguity weights (order={self.order}) for {len(gdf)} polygons"
        )

        if self.order > 1:
            logger.warning(
                "Higher-order contiguity (order > 1) is not fully supported. "
                "Using first-order contiguity."
            )

        # Use libpysal to compute weights
        w_pysal = LibPySAL_Rook.from_dataframe(gdf, use_index=False)

        # Convert to our format
        self.n = w_pysal.n
        self.neighbors = dict(w_pysal.neighbors)
        self.weights = dict(w_pysal.weights)
        self._fitted = True

        cardinality = self.cardinality()
        logger.info(
            f"Rook weights computed: {self.n} observations, "
            f"mean neighbors={cardinality['mean']:.2f}, "
            f"islands={len(cardinality['islands'])}"
        )

        return self

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._fitted:
            return f"RookWeights(order={self.order}, fitted=False)"

        return (
            f"RookWeights(order={self.order}, n={self.n}, " f"standardized={self.is_standardized})"
        )
