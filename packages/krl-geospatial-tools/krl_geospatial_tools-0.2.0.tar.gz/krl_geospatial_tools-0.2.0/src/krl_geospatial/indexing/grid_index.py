"""
Grid-based spatial index implementation.

Grid indexing divides space into regular cells and assigns geometries
to cells based on their bounding boxes.
"""

from typing import Dict, List, Optional, Set, Tuple, Union

import geopandas as gpd
import numpy as np
from shapely.geometry import Point, box
from shapely.geometry.base import BaseGeometry

try:
    from krl_core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class GridIndex:
    """
    Grid-based spatial index for efficient spatial queries.

    Grid indexing divides the spatial extent into a regular grid of cells.
    Each geometry is assigned to one or more cells based on its bounding box.
    This provides fast approximate spatial queries.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.indexing import GridIndex

        # Load spatial data
        gdf = gpd.read_file("parcels.shp")

        # Build grid index with 100x100 cells
        idx = GridIndex(n_cells_x=100, n_cells_y=100)
        idx.build(gdf)

        # Query intersecting features
        bbox = (-120, 30, -110, 40)
        intersecting = idx.intersection(bbox)

        # Get grid statistics
        stats = idx.statistics()
        print(f"Average geometries per cell: {stats['mean_per_cell']:.2f}")
        ```

    Attributes:
        n_cells_x (int): Number of grid cells in x direction
        n_cells_y (int): Number of grid cells in y direction
        gdf (Optional[gpd.GeoDataFrame]): Source GeoDataFrame
        grid (Dict[Tuple[int, int], List[int]]): Grid cell to geometry indices mapping
    """

    def __init__(self, n_cells_x: int = 10, n_cells_y: int = 10):
        """
        Initialize a grid-based spatial index.

        Args:
            n_cells_x: Number of grid cells in x direction
            n_cells_y: Number of grid cells in y direction

        Raises:
            ValueError: If n_cells_x or n_cells_y < 1
        """
        if n_cells_x < 1 or n_cells_y < 1:
            raise ValueError("Number of cells must be at least 1 in each direction")

        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.grid: Dict[Tuple[int, int], List[int]] = {}
        self._built = False

        # Spatial extent (computed during build)
        self.minx: float = 0.0
        self.miny: float = 0.0
        self.maxx: float = 0.0
        self.maxy: float = 0.0
        self.cell_width: float = 0.0
        self.cell_height: float = 0.0

        logger.info(f"Initialized GridIndex with {n_cells_x}x{n_cells_y} cells")

    def build(self, gdf: gpd.GeoDataFrame) -> "GridIndex":
        """
        Build grid index from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame to index

        Returns:
            self: Built GridIndex

        Raises:
            ValueError: If GeoDataFrame is empty
        """
        if len(gdf) == 0:
            raise ValueError("Cannot build index from empty GeoDataFrame")

        logger.info(
            f"Building grid index for {len(gdf)} geometries "
            f"with {self.n_cells_x}x{self.n_cells_y} cells"
        )

        self.gdf = gdf.copy()
        self.grid = {}

        # Compute spatial extent
        total_bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        self.minx, self.miny, self.maxx, self.maxy = total_bounds

        # Add small buffer to avoid edge cases
        eps = 1e-10
        self.maxx += eps
        self.maxy += eps

        # Compute cell dimensions
        self.cell_width = (self.maxx - self.minx) / self.n_cells_x
        self.cell_height = (self.maxy - self.miny) / self.n_cells_y

        # Assign geometries to cells
        for idx_val, geom in enumerate(gdf.geometry):
            if geom is not None and not geom.is_empty:
                cells = self._geometry_to_cells(geom)
                for cell in cells:
                    if cell not in self.grid:
                        self.grid[cell] = []
                    self.grid[cell].append(idx_val)

        self._built = True

        # Log statistics
        n_cells_used = len(self.grid)
        avg_per_cell = np.mean([len(ids) for ids in self.grid.values()])
        logger.info(
            f"Grid index built: {n_cells_used} cells used, "
            f"avg {avg_per_cell:.2f} geometries per cell"
        )

        return self

    def _geometry_to_cells(self, geom: BaseGeometry) -> List[Tuple[int, int]]:
        """
        Determine which grid cells a geometry overlaps.

        Args:
            geom: Geometry to map to cells

        Returns:
            List of (cell_x, cell_y) tuples
        """
        minx, miny, maxx, maxy = geom.bounds

        # Convert bounds to cell indices
        cell_minx = int((minx - self.minx) / self.cell_width)
        cell_miny = int((miny - self.miny) / self.cell_height)
        cell_maxx = int((maxx - self.minx) / self.cell_width)
        cell_maxy = int((maxy - self.miny) / self.cell_height)

        # Clamp to grid bounds
        cell_minx = max(0, min(cell_minx, self.n_cells_x - 1))
        cell_miny = max(0, min(cell_miny, self.n_cells_y - 1))
        cell_maxx = max(0, min(cell_maxx, self.n_cells_x - 1))
        cell_maxy = max(0, min(cell_maxy, self.n_cells_y - 1))

        # Generate list of cells
        cells = []
        for cx in range(cell_minx, cell_maxx + 1):
            for cy in range(cell_miny, cell_maxy + 1):
                cells.append((cx, cy))

        return cells

    def _bbox_to_cells(self, bbox: Tuple[float, float, float, float]) -> List[Tuple[int, int]]:
        """
        Determine which grid cells a bounding box overlaps.

        Args:
            bbox: Bounding box (minx, miny, maxx, maxy)

        Returns:
            List of (cell_x, cell_y) tuples
        """
        minx, miny, maxx, maxy = bbox

        # Convert bounds to cell indices
        cell_minx = int((minx - self.minx) / self.cell_width)
        cell_miny = int((miny - self.miny) / self.cell_height)
        cell_maxx = int((maxx - self.minx) / self.cell_width)
        cell_maxy = int((maxy - self.miny) / self.cell_height)

        # Clamp to grid bounds
        cell_minx = max(0, min(cell_minx, self.n_cells_x - 1))
        cell_miny = max(0, min(cell_miny, self.n_cells_y - 1))
        cell_maxx = max(0, min(cell_maxx, self.n_cells_x - 1))
        cell_maxy = max(0, min(cell_maxy, self.n_cells_y - 1))

        # Generate list of cells
        cells = []
        for cx in range(cell_minx, cell_maxx + 1):
            for cy in range(cell_miny, cell_maxy + 1):
                cells.append((cx, cy))

        return cells

    def intersection(
        self,
        bbox: Union[Tuple[float, float, float, float], BaseGeometry],
        return_indices: bool = False,
    ) -> Union[gpd.GeoDataFrame, List[int]]:
        """
        Query geometries that may intersect a bounding box or geometry.

        Note: This returns candidates based on grid cells. Some results
        may not actually intersect the query bbox.

        Args:
            bbox: Bounding box (minx, miny, maxx, maxy) or geometry
            return_indices: If True, return indices instead of GeoDataFrame

        Returns:
            GeoDataFrame of candidate geometries or list of indices

        Raises:
            ValueError: If index has not been built
        """
        if not self._built:
            raise ValueError("Index must be built before querying. Call build() first.")

        # Convert geometry to bbox if needed
        if isinstance(bbox, BaseGeometry):
            bbox = bbox.bounds

        # Find overlapping cells
        cells = self._bbox_to_cells(bbox)

        # Collect unique geometry indices
        candidate_ids: Set[int] = set()
        for cell in cells:
            if cell in self.grid:
                candidate_ids.update(self.grid[cell])

        candidate_ids = sorted(candidate_ids)

        if return_indices:
            return list(candidate_ids)

        # Return subset of GeoDataFrame
        return self.gdf.iloc[candidate_ids].copy()

    def nearest(
        self,
        point: Union[Tuple[float, float], Point],
        k: int = 1,
        search_radius: int = 1,
        return_indices: bool = False,
    ) -> Union[gpd.GeoDataFrame, List[int]]:
        """
        Find approximate k nearest neighbors to a point.

        Searches cells within a radius around the point's cell.
        May not return exact k nearest neighbors for large k or small search_radius.

        Args:
            point: Query point as (x, y) tuple or Point geometry
            k: Number of nearest neighbors to return
            search_radius: Number of cells to search in each direction
            return_indices: If True, return indices instead of GeoDataFrame

        Returns:
            GeoDataFrame of approximate k nearest geometries or list of indices

        Raises:
            ValueError: If index has not been built or k < 1
        """
        if not self._built:
            raise ValueError("Index must be built before querying. Call build() first.")

        if k < 1:
            raise ValueError("k must be at least 1")

        # Convert Point to tuple if needed
        if isinstance(point, Point):
            point = (point.x, point.y)

        # Find cell containing point
        cell_x = int((point[0] - self.minx) / self.cell_width)
        cell_y = int((point[1] - self.miny) / self.cell_height)

        # Clamp to grid bounds
        cell_x = max(0, min(cell_x, self.n_cells_x - 1))
        cell_y = max(0, min(cell_y, self.n_cells_y - 1))

        # Search cells within radius
        candidate_ids: Set[int] = set()
        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                cx = cell_x + dx
                cy = cell_y + dy
                if 0 <= cx < self.n_cells_x and 0 <= cy < self.n_cells_y:
                    cell = (cx, cy)
                    if cell in self.grid:
                        candidate_ids.update(self.grid[cell])

        # If we don't have enough candidates, return all
        if len(candidate_ids) <= k:
            candidate_ids = sorted(candidate_ids)
            if return_indices:
                return list(candidate_ids)
            return self.gdf.iloc[candidate_ids].copy()

        # Compute distances and return k nearest
        candidates = self.gdf.iloc[list(candidate_ids)]
        query_point = Point(point)
        distances = candidates.geometry.distance(query_point)
        nearest_indices = distances.nsmallest(k).index.tolist()

        if return_indices:
            return nearest_indices

        return self.gdf.loc[nearest_indices].copy()

    def statistics(self) -> Dict[str, Union[int, float]]:
        """
        Compute statistics about the grid index.

        Returns:
            Dictionary with statistics:
                - total_cells: Total number of cells in grid
                - used_cells: Number of cells containing geometries
                - min_per_cell: Minimum geometries in any used cell
                - max_per_cell: Maximum geometries in any used cell
                - mean_per_cell: Mean geometries per used cell
                - sparsity: Fraction of empty cells

        Raises:
            ValueError: If index has not been built
        """
        if not self._built:
            raise ValueError("Index must be built before computing statistics.")

        total_cells = self.n_cells_x * self.n_cells_y
        used_cells = len(self.grid)

        if used_cells == 0:
            return {
                "total_cells": total_cells,
                "used_cells": 0,
                "min_per_cell": 0,
                "max_per_cell": 0,
                "mean_per_cell": 0.0,
                "sparsity": 1.0,
            }

        counts = [len(ids) for ids in self.grid.values()]

        return {
            "total_cells": total_cells,
            "used_cells": used_cells,
            "min_per_cell": min(counts),
            "max_per_cell": max(counts),
            "mean_per_cell": np.mean(counts),
            "sparsity": 1.0 - (used_cells / total_cells),
        }

    def clear(self) -> None:
        """Clear the index and release resources."""
        self.grid = {}
        self.gdf = None
        self._built = False
        logger.info("Grid index cleared")

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._built:
            return f"GridIndex({self.n_cells_x}x{self.n_cells_y}, built=False)"

        n_geometries = len(self.gdf) if self.gdf is not None else 0
        n_cells_used = len(self.grid)
        return (
            f"GridIndex({self.n_cells_x}x{self.n_cells_y}, "
            f"n_geometries={n_geometries}, cells_used={n_cells_used}, built=True)"
        )
