"""
Flow map visualization for origin-destination data.

This module provides flow map capabilities for visualizing movement,
migration, trade, and other origin-destination patterns.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import folium
import geopandas as gpd
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from shapely.geometry import LineString, Point

from .utils import get_color_scheme

logger = get_logger(__name__)


class FlowMap:
    """
    Flow map for origin-destination visualization.

    Flow maps display movement between locations using lines where:
    - Line width represents flow volume
    - Line color represents flow category or direction
    - Arrows indicate direction

    Attributes:
        map: Underlying folium Map object

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.mapping import FlowMap

        # Create flow data
        flows = gpd.GeoDataFrame({
            'origin': ['NYC', 'LA', 'Chicago'],
            'destination': ['LA', 'NYC', 'NYC'],
            'flow': [1000, 800, 500],
            'geometry': [LineString(...), ...]
        })

        # Create flow map
        m = FlowMap(
            flows,
            flow_column='flow',
            min_width=1,
            max_width=10,
            arrows=True
        )

        # Save to file
        m.save('migration_flows.html')
        ```
    """

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        flow_column: str,
        origin_column: Optional[str] = None,
        destination_column: Optional[str] = None,
        color_column: Optional[str] = None,
        min_width: float = 1.0,
        max_width: float = 10.0,
        color: str = "#3388ff",
        cmap: Optional[str] = None,
        opacity: float = 0.7,
        arrows: bool = True,
        arrow_size: float = 15,
        curve: bool = False,
        curve_weight: float = 0.3,
        location: Optional[List[float]] = None,
        zoom_start: int = 4,
        tiles: str = "OpenStreetMap",
        popup_columns: Optional[List[str]] = None,
    ):
        """
        Initialize flow map.

        Args:
            gdf: GeoDataFrame with LineString geometries or origin/dest points
            flow_column: Column with flow volumes
            origin_column: Column with origin names (optional)
            destination_column: Column with destination names (optional)
            color_column: Column for coloring flows (optional)
            min_width: Minimum line width
            max_width: Maximum line width
            color: Default line color
            cmap: Color scheme if color_column provided
            opacity: Line opacity (0-1)
            arrows: Show direction arrows
            arrow_size: Arrow size in pixels
            curve: Use curved lines instead of straight
            curve_weight: Curve amount (0-1)
            location: Map center [lat, lon]
            zoom_start: Initial zoom level
            tiles: Base tile layer
            popup_columns: Columns to show in popups
        """
        self.gdf = gdf.copy()
        self.flow_column = flow_column
        self.origin_column = origin_column
        self.destination_column = destination_column
        self.color_column = color_column
        self.min_width = min_width
        self.max_width = max_width
        self.default_color = color
        self.opacity = opacity
        self.arrows = arrows
        self.arrow_size = arrow_size
        self.curve = curve
        self.curve_weight = curve_weight

        # Validate column
        if flow_column not in self.gdf.columns:
            raise ValueError(f"Flow column '{flow_column}' not found")

        # Ensure WGS84
        if self.gdf.crs and self.gdf.crs.to_epsg() != 4326:
            logger.info(f"Reprojecting from {self.gdf.crs} to EPSG:4326")
            self.gdf = self.gdf.to_crs(epsg=4326)

        # Initialize map
        if location is None:
            bounds = self.gdf.total_bounds
            location = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

        self.map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)

        # Calculate line widths
        self.widths = self._calculate_widths()

        # Get colors
        if color_column and cmap:
            unique_values = self.gdf[color_column].unique()
            self.color_map = dict(
                zip(unique_values, get_color_scheme(cmap, n_colors=len(unique_values)))
            )
        else:
            self.color_map = None

        # Add flows to map
        self._add_flows(popup_columns)

        logger.info(f"Created flow map with {len(self.gdf)} flows")

    def _calculate_widths(self) -> np.ndarray:
        """Calculate line widths based on flow volumes."""
        values = self.gdf[self.flow_column].values

        # Remove NaN
        valid_mask = ~np.isnan(values)
        valid_values = values[valid_mask]

        if len(valid_values) == 0:
            logger.warning("No valid flow values")
            return np.full(len(values), self.min_width)

        # Normalize to [min_width, max_width]
        min_val, max_val = valid_values.min(), valid_values.max()

        if max_val > min_val:
            normalized = (valid_values - min_val) / (max_val - min_val)
            widths_valid = self.min_width + normalized * (self.max_width - self.min_width)
        else:
            widths_valid = np.full(len(valid_values), (self.min_width + self.max_width) / 2)

        # Fill in all values
        widths = np.full(len(values), self.min_width)
        widths[valid_mask] = widths_valid

        return widths

    def _get_curve_points(
        self, start: Tuple[float, float], end: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """
        Generate curved line points.

        Args:
            start: Start point (lat, lon)
            end: End point (lat, lon)

        Returns:
            List of points along curve
        """
        # Calculate midpoint
        mid_lat = (start[0] + end[0]) / 2
        mid_lon = (start[1] + end[1]) / 2

        # Calculate perpendicular offset
        dx = end[1] - start[1]
        dy = end[0] - start[0]
        dist = np.sqrt(dx**2 + dy**2)

        if dist > 0:
            # Perpendicular direction
            perp_x = -dy / dist
            perp_y = dx / dist

            # Offset distance
            offset = dist * self.curve_weight

            # Control point
            ctrl_lat = mid_lat + perp_y * offset
            ctrl_lon = mid_lon + perp_x * offset

            # Generate points along quadratic Bezier curve
            t = np.linspace(0, 1, 20)
            curve_lats = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * ctrl_lat + t**2 * end[0]
            curve_lons = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * ctrl_lon + t**2 * end[1]

            return list(zip(curve_lats, curve_lons))
        else:
            return [start, end]

    def _add_flows(self, popup_columns: Optional[List[str]]):
        """Add flow lines to map."""
        if popup_columns is None:
            popup_columns = [self.flow_column]
            if self.origin_column:
                popup_columns.insert(0, self.origin_column)
            if self.destination_column:
                popup_columns.insert(1, self.destination_column)

        for idx, row in self.gdf.iterrows():
            geom = row.geometry

            # Get line coordinates
            if geom.geom_type == "LineString":
                coords = list(geom.coords)
                start = (coords[0][1], coords[0][0])  # (lat, lon)
                end = (coords[-1][1], coords[-1][0])
            elif geom.geom_type == "Point":
                # Need origin and destination columns
                if not (self.origin_column and self.destination_column):
                    logger.warning(
                        f"Skipping row {idx}: Point geometry requires origin/dest columns"
                    )
                    continue
                # This would need additional logic to get coordinates from names
                logger.warning("Point geometries require pre-computed LineStrings")
                continue
            else:
                logger.warning(f"Skipping row {idx}: Invalid geometry type {geom.geom_type}")
                continue

            # Get line width
            width = self.widths[idx]

            # Get color
            if self.color_map and self.color_column:
                color_value = row[self.color_column]
                color = self.color_map.get(color_value, self.default_color)
            else:
                color = self.default_color

            # Create popup
            popup_html = '<div style="font-family: monospace;">'
            for col in popup_columns:
                if col in row.index:
                    value = row[col]
                    popup_html += f"<b>{col}:</b> {value}<br>"
            popup_html += "</div>"

            # Generate line points (curved or straight)
            if self.curve:
                line_points = self._get_curve_points(start, end)
            else:
                line_points = [start, end]

            # Add line
            folium.PolyLine(
                locations=line_points,
                color=color,
                weight=width,
                opacity=self.opacity,
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(self.map)

            # Add arrow
            if self.arrows:
                # Arrow at end point
                arrow_html = f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="{self.arrow_size}" height="{self.arrow_size}">
                    <polygon points="0,{self.arrow_size} {self.arrow_size/2},0 {self.arrow_size},{self.arrow_size}" 
                             fill="{color}" opacity="{self.opacity}"/>
                </svg>
                """

                # Calculate arrow rotation
                if len(line_points) >= 2:
                    # Use last two points to get direction
                    p1 = line_points[-2]
                    p2 = line_points[-1]
                    angle = np.degrees(np.arctan2(p2[0] - p1[0], p2[1] - p1[1]))

                    folium.Marker(
                        location=end,
                        icon=folium.DivIcon(
                            html=f'<div style="transform: rotate({angle}deg);">{arrow_html}</div>'
                        ),
                    ).add_to(self.map)

    def add_tile_layer(self, tiles: str, name: str):
        """Add an additional tile layer."""
        folium.TileLayer(tiles=tiles, name=name).add_to(self.map)
        logger.debug(f"Added tile layer: {name}")

    def add_layer_control(self):
        """Add layer control for toggling layers."""
        folium.LayerControl().add_to(self.map)
        logger.debug("Added layer control")

    def fit_bounds(self):
        """Fit map to data bounds."""
        bounds = self.gdf.total_bounds
        self.map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        logger.debug("Fitted map to data bounds")

    def save(self, filepath: str):
        """
        Save map to HTML file.

        Args:
            filepath: Output file path
        """
        self.map.save(filepath)
        logger.info(f"Saved flow map to {filepath}")

    def _repr_html_(self):
        """Return HTML representation for Jupyter notebooks."""
        return self.map._repr_html_()
