# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-Proprietary

"""
Base classes for geospatial analysis.

This module provides abstract base classes and core data structures for all
geospatial tools in the KRL ecosystem.

This module now uses the centralized Pydantic-based GeospatialResult from
krl-model-zoo-pro for consistency and automatic validation. SpatialResult
is maintained as an alias for backwards compatibility.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry

try:
    from krl_core.logging import get_logger
except ImportError:
    import logging

    def get_logger(name: str) -> logging.Logger:
        """Fallback logger if krl_core not available."""
        return logging.getLogger(name)


logger = get_logger(__name__)

# Import centralized Pydantic GeospatialResult
try:
    from krl_models.core.results import GeospatialResult

    # Provide alias for backwards compatibility
    SpatialResult = GeospatialResult

    # For backwards compatibility, also export GeospatialResult
    __all_results__ = ["SpatialResult", "GeospatialResult"]
except ImportError:
    # Fallback for development/testing without krl-model-zoo-pro
    import warnings
    from dataclasses import dataclass, field

    warnings.warn(
        "krl-model-zoo-pro not installed. Using legacy dataclass SpatialResult. "
        "Install krl-model-zoo-pro for Pydantic validation: pip install krl-model-zoo-pro",
        ImportWarning,
    )

    @dataclass
    class SpatialResult:  # type: ignore[no-redef]
        """
        Legacy dataclass fallback for SpatialResult.

        This is only used when krl-model-zoo-pro is not installed.
        For production, install krl-model-zoo-pro to get the Pydantic version.
        """

        # BaseResult fields for compatibility
        model_name: str = "SpatialAnalysis"
        timestamp: Optional[str] = None
        metadata: Dict[str, Any] = field(default_factory=dict)

        # GeospatialResult-specific fields
        method: str = "spatial_analysis"
        statistic: Optional[float] = None
        p_value: Optional[float] = None
        confidence_interval: Optional[tuple] = None

        # Additional results
        coefficients: Optional[Dict[str, float]] = None
        residuals: Optional[np.ndarray] = None
        fitted_values: Optional[np.ndarray] = None
        std_errors: Optional[Dict[str, float]] = None

        # Model diagnostics
        r_squared: Optional[float] = None
        adjusted_r_squared: Optional[float] = None
        aic: Optional[float] = None
        bic: Optional[float] = None
        log_likelihood: Optional[float] = None

        # Spatial parameters
        spatial_parameter: Optional[float] = None  # rho for lag, lambda for error
        moran_i: Optional[float] = None
        geary_c: Optional[float] = None

        # Metadata
        n_obs: Optional[int] = None
        n_features: Optional[int] = None
        degrees_freedom: Optional[int] = None

        # Additional outputs (legacy)
        extra: Dict[str, Any] = field(default_factory=dict)

        def __post_init__(self) -> None:
            """Set timestamp if not provided."""
            if self.timestamp is None:
                from datetime import datetime, UTC
                self.timestamp = datetime.now(UTC).isoformat()

        def __repr__(self) -> str:
            """String representation of results."""
            lines = [f"SpatialResult(method='{self.method}')"]

            if self.statistic is not None:
                lines.append(f"  Statistic: {self.statistic:.4f}")
            if self.p_value is not None:
                sig = (
                    "***"
                    if self.p_value < 0.001
                    else "**" if self.p_value < 0.01 else "*" if self.p_value < 0.05 else ""
                )
                lines.append(f"  P-value: {self.p_value:.4f} {sig}")
            if self.r_squared is not None:
                lines.append(f"  R-squared: {self.r_squared:.4f}")
            if self.spatial_parameter is not None:
                lines.append(f"  Spatial parameter: {self.spatial_parameter:.4f}")
            if self.n_obs is not None:
                lines.append(f"  N observations: {self.n_obs}")

            return "\n".join(lines)

        def to_dict(self) -> Dict[str, Any]:
            """Convert results to dictionary."""
            return {
                "model_name": self.model_name,
                "timestamp": self.timestamp,
                "metadata": self.metadata,
                "method": self.method,
                "statistic": self.statistic,
                "p_value": self.p_value,
                "confidence_interval": self.confidence_interval,
                "coefficients": self.coefficients,
                "r_squared": self.r_squared,
                "adjusted_r_squared": self.adjusted_r_squared,
                "aic": self.aic,
                "bic": self.bic,
                "spatial_parameter": self.spatial_parameter,
                "moran_i": self.moran_i,
                "geary_c": self.geary_c,
                "n_obs": self.n_obs,
                "n_features": self.n_features,
                **self.extra,
            }

        def is_significant(self, alpha: float = 0.05) -> bool:
            """Check if result is statistically significant."""
            if self.p_value is None:
                raise ValueError("p_value not available")
            return self.p_value < alpha

        def to_dataframe(self) -> pd.DataFrame:
            """Convert coefficients and std errors to DataFrame."""
            if self.coefficients is None:
                raise ValueError("No coefficients available")

            df = pd.DataFrame({"coefficient": self.coefficients})

            if self.std_errors is not None:
                df["std_error"] = pd.Series(self.std_errors)
                df["t_statistic"] = df["coefficient"] / df["std_error"]
                # Two-tailed t-test p-values (approximate)
                from scipy import stats

                df["p_value"] = 2 * (
                    1 - stats.t.cdf(np.abs(df["t_statistic"]), self.degrees_freedom or 100)
                )

            return df

    # Define GeospatialResult as alias for backwards compatibility
    GeospatialResult = SpatialResult
    __all_results__ = ["SpatialResult", "GeospatialResult"]


class BaseGeospatialAnalyzer(ABC):
    """
    Abstract base class for all geospatial analysis tools.

    This class provides common functionality for:
    - Data validation and preprocessing
    - Coordinate reference system (CRS) handling
    - Geometry validation and repair
    - Integration with krl-core logging

    Subclasses must implement the `fit` and `analyze` methods.
    """

    def __init__(
        self,
        crs: Optional[Union[str, int]] = "EPSG:4326",
        validate_geometries: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize geospatial analyzer.

        Args:
            crs: Coordinate reference system (default: WGS84)
            validate_geometries: Whether to validate geometries on input
            **kwargs: Additional keyword arguments
        """
        self.crs = crs
        self.validate_geometries = validate_geometries
        self._fitted = False
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def fit(self, data: gpd.GeoDataFrame, **kwargs: Any) -> "BaseGeospatialAnalyzer":
        """
        Fit the analyzer to the data.

        Args:
            data: GeoDataFrame containing spatial data
            **kwargs: Additional keyword arguments

        Returns:
            Self for method chaining

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement fit()")

    @abstractmethod
    def analyze(self, **kwargs: Any) -> "SpatialResult":
        """
        Perform the spatial analysis.

        Args:
            **kwargs: Analysis-specific keyword arguments

        Returns:
            SpatialResult containing analysis outputs

        Raises:
            NotImplementedError: Must be implemented by subclasses
            RuntimeError: If called before fit()
        """
        if not self._fitted:
            raise RuntimeError("Must call fit() before analyze()")
        raise NotImplementedError("Subclasses must implement analyze()")

    def _validate_geodataframe(
        self, data: gpd.GeoDataFrame, required_cols: Optional[List[str]] = None
    ) -> gpd.GeoDataFrame:
        """
        Validate and prepare a GeoDataFrame for analysis.

        Args:
            data: Input GeoDataFrame
            required_cols: List of required column names

        Returns:
            Validated GeoDataFrame

        Raises:
            TypeError: If data is not a GeoDataFrame
            ValueError: If required columns are missing or geometries are invalid
        """
        if not isinstance(data, gpd.GeoDataFrame):
            raise TypeError(f"Expected GeoDataFrame, got {type(data)}")

        # Check for required columns
        if required_cols:
            missing = set(required_cols) - set(data.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

        # Check CRS
        if data.crs is None:
            self.logger.warning("Input data has no CRS, assuming WGS84")
            data = data.set_crs(self.crs)
        elif data.crs != self.crs:
            self.logger.info(f"Reprojecting from {data.crs} to {self.crs}")
            data = data.to_crs(self.crs)

        # Validate geometries
        if self.validate_geometries:
            invalid = ~data.geometry.is_valid
            if invalid.any():
                n_invalid = invalid.sum()
                self.logger.warning(f"Found {n_invalid} invalid geometries, attempting repair")
                data.loc[invalid, "geometry"] = data.loc[invalid, "geometry"].buffer(0)

        return data

    def _check_fitted(self) -> None:
        """
        Check if the analyzer has been fitted.

        Raises:
            RuntimeError: If analyzer has not been fitted
        """
        if not self._fitted:
            raise RuntimeError(
                f"{self.__class__.__name__} must be fitted before use. Call fit() first."
            )


class SpatialDataFrame(gpd.GeoDataFrame):
    """
    Enhanced GeoDataFrame with additional spatial functionality.

    This class extends geopandas.GeoDataFrame with convenience methods for
    common spatial operations in the KRL ecosystem.
    """

    def __init__(self, *args, **kwargs):
        """Initialize SpatialDataFrame."""
        super().__init__(*args, **kwargs)

    @property
    def bounds_dict(self) -> Dict[str, float]:
        """Get bounding box as dictionary."""
        minx, miny, maxx, maxy = self.total_bounds
        return {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy}

    @property
    def centroid_coords(self) -> np.ndarray:
        """Get centroid coordinates as numpy array."""
        centroids = self.geometry.centroid
        return np.column_stack([centroids.x, centroids.y])

    def buffer_distance(self, distance: float, **kwargs) -> "SpatialDataFrame":
        """
        Create buffers around geometries.

        Args:
            distance: Buffer distance in CRS units
            **kwargs: Additional arguments passed to buffer()

        Returns:
            New SpatialDataFrame with buffered geometries
        """
        buffered = self.copy()
        buffered.geometry = self.geometry.buffer(distance, **kwargs)
        return buffered

    def spatial_join_nearest(
        self, other: gpd.GeoDataFrame, max_distance: Optional[float] = None
    ) -> "SpatialDataFrame":
        """
        Spatial join to nearest feature in other GeoDataFrame.

        Args:
            other: GeoDataFrame to join with
            max_distance: Maximum distance for join (optional)

        Returns:
            Joined SpatialDataFrame
        """
        from shapely.strtree import STRtree

        # Build spatial index
        tree = STRtree(other.geometry)

        # Find nearest neighbor for each geometry
        indices = []
        distances = []

        for geom in self.geometry:
            nearest_idx = tree.nearest(geom)
            nearest_geom = other.geometry.iloc[nearest_idx]
            dist = geom.distance(nearest_geom)

            if max_distance is None or dist <= max_distance:
                indices.append(nearest_idx)
                distances.append(dist)
            else:
                indices.append(-1)
                distances.append(np.nan)

        # Join data
        result = self.copy()
        result["nearest_idx"] = indices
        result["nearest_distance"] = distances

        # Add columns from other GeoDataFrame
        valid_joins = result["nearest_idx"] >= 0
        if valid_joins.any():
            for col in other.columns:
                if col != other.geometry.name:
                    result.loc[valid_joins, f"nearest_{col}"] = other.iloc[
                        result.loc[valid_joins, "nearest_idx"]
                    ][col].values

        return result


def create_geodataframe(
    data: Union[pd.DataFrame, Dict],
    geometry_col: Optional[str] = None,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    crs: str = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame from various input formats.

    Args:
        data: Input data (DataFrame or dict)
        geometry_col: Name of column containing geometries
        x_col: Name of column containing x/longitude coordinates
        y_col: Name of column containing y/latitude coordinates
        crs: Coordinate reference system

    Returns:
        GeoDataFrame

    Raises:
        ValueError: If neither geometry_col nor x_col/y_col are provided

    Examples:
        >>> # From coordinates
        >>> df = pd.DataFrame({'x': [-118, -122], 'y': [34, 37], 'value': [1, 2]})
        >>> gdf = create_geodataframe(df, x_col='x', y_col='y')

        >>> # From geometry column
        >>> df['geometry'] = df.apply(lambda r: Point(r['x'], r['y']), axis=1)
        >>> gdf = create_geodataframe(df, geometry_col='geometry')
    """
    if isinstance(data, dict):
        data = pd.DataFrame(data)

    if geometry_col is not None:
        # Use existing geometry column
        return gpd.GeoDataFrame(data, geometry=geometry_col, crs=crs)

    elif x_col is not None and y_col is not None:
        # Create geometries from coordinates
        geometry = [Point(xy) for xy in zip(data[x_col], data[y_col])]
        return gpd.GeoDataFrame(data, geometry=geometry, crs=crs)

    else:
        raise ValueError("Must provide either geometry_col or both x_col and y_col")


# Utility functions for backwards compatibility with SpatialResult
def get_coefficient(result: SpatialResult, name: str, default: Any = None) -> Any:
    """Get a specific coefficient value from SpatialResult."""
    if result.coefficients is None:
        return default
    return result.coefficients.get(name, default)


def add_coefficient(result: SpatialResult, name: str, value: float) -> None:
    """Add or update a coefficient in SpatialResult."""
    if result.coefficients is None:
        result.coefficients = {}
    result.coefficients[name] = value


def get_diagnostic(
    result: SpatialResult, metric: str, default: Any = None
) -> Any:
    """
    Get a specific diagnostic metric from SpatialResult.

    Args:
        result: SpatialResult instance
        metric: Name of diagnostic (r_squared, aic, bic, etc.)
        default: Default value if metric not found

    Returns:
        Metric value or default
    """
    return getattr(result, metric, default)


# Export all public classes and functions
__all__ = [
    "BaseGeospatialAnalyzer",
    "SpatialResult",
    "GeospatialResult",
    "SpatialDataFrame",
    "create_geodataframe",
    "get_coefficient",
    "add_coefficient",
    "get_diagnostic",
]
