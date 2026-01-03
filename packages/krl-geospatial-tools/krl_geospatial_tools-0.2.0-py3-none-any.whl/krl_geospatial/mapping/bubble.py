"""
Bubble map (proportional symbol map) visualization.

This module provides bubble map capabilities with size and color encoding
for visualizing bivariate spatial data.
"""

from typing import Any, Dict, List, Optional, Union

import folium
import geopandas as gpd
import numpy as np
from folium.plugins import MarkerCluster
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)

from .utils import ColorScheme, classify_values, get_color_scheme, value_to_color

logger = get_logger(__name__)


class BubbleMap:
    """
    Bubble map (proportional symbol map) visualization.

    Bubble maps represent data values using circles where:
    - Circle size represents one variable (e.g., population)
    - Circle color represents another variable (e.g., income)

    Attributes:
        map: Underlying folium Map object

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.mapping import BubbleMap

        # Load data
        cities = gpd.read_file('cities.shp')

        # Create bubble map
        m = BubbleMap(
            cities,
            size_column='population',
            color_column='median_income',
            size_scale='sqrt',
            cmap='RdYlGn',
            legend=True
        )

        # Save to file
        m.save('cities_bubble_map.html')
        ```
    """

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        size_column: str,
        color_column: Optional[str] = None,
        size_scale: str = "linear",
        min_radius: float = 5.0,
        max_radius: float = 30.0,
        cmap: Union[str, ColorScheme] = "viridis",
        classification: str = "quantiles",
        k: int = 5,
        opacity: float = 0.7,
        legend: bool = True,
        legend_title: Optional[str] = None,
        location: Optional[List[float]] = None,
        zoom_start: int = 4,
        tiles: str = "OpenStreetMap",
        popup_columns: Optional[List[str]] = None,
        cluster: bool = False,
    ):
        """
        Initialize bubble map.

        Args:
            gdf: GeoDataFrame with point geometries
            size_column: Column for bubble size
            color_column: Column for bubble color (optional)
            size_scale: Scaling method ('linear', 'sqrt', 'log')
            min_radius: Minimum bubble radius in pixels
            max_radius: Maximum bubble radius in pixels
            cmap: Color scheme for color_column
            classification: Classification method for colors
            k: Number of color classes
            opacity: Bubble opacity (0-1)
            legend: Show legend
            legend_title: Custom legend title
            location: Map center [lat, lon]
            zoom_start: Initial zoom level
            tiles: Base tile layer
            popup_columns: Columns to show in popups
            cluster: Enable marker clustering
        """
        self.gdf = gdf.copy()
        self.size_column = size_column
        self.color_column = color_column
        self.size_scale = size_scale
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.opacity = opacity

        # Validate columns
        if size_column not in self.gdf.columns:
            raise ValueError(f"Size column '{size_column}' not found")

        if color_column and color_column not in self.gdf.columns:
            raise ValueError(f"Color column '{color_column}' not found")

        # Check geometry type
        geom_types = self.gdf.geometry.geom_type.unique()
        if not all(gt == "Point" for gt in geom_types):
            logger.warning("Non-point geometries found, using centroids")
            self.gdf["geometry"] = self.gdf.geometry.centroid

        # Ensure WGS84
        if self.gdf.crs and self.gdf.crs.to_epsg() != 4326:
            logger.info(f"Reprojecting from {self.gdf.crs} to EPSG:4326")
            self.gdf = self.gdf.to_crs(epsg=4326)

        # Initialize map
        if location is None:
            bounds = self.gdf.total_bounds
            location = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

        self.map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)

        # Calculate bubble sizes
        self.sizes = self._calculate_sizes()

        # Calculate colors if color_column provided
        if color_column:
            values = self.gdf[color_column].values
            self.bin_indices, self.bin_edges = classify_values(values, method=classification, k=k)
            self.colors = get_color_scheme(cmap, n_colors=k)
        else:
            self.bin_indices = None
            self.bin_edges = None
            self.colors = ["#3388ff"]  # Default blue

        # Add bubbles to map
        self._add_bubbles(popup_columns, cluster)

        # Add legend
        if legend:
            legend_title = legend_title or size_column
            self._add_legend(legend_title)

        logger.info(f"Created bubble map with {len(self.gdf)} bubbles")

    def _calculate_sizes(self) -> np.ndarray:
        """Calculate bubble sizes with scaling."""
        values = self.gdf[self.size_column].values

        # Remove NaN
        valid_mask = ~np.isnan(values)
        valid_values = values[valid_mask]

        if len(valid_values) == 0:
            logger.warning("No valid size values")
            return np.full(len(values), self.min_radius)

        # Apply scaling
        if self.size_scale == "sqrt":
            scaled = np.sqrt(valid_values)
        elif self.size_scale == "log":
            # Add 1 to avoid log(0)
            scaled = np.log1p(valid_values)
        else:  # linear
            scaled = valid_values

        # Normalize to [min_radius, max_radius]
        min_val, max_val = scaled.min(), scaled.max()

        if max_val > min_val:
            normalized = (scaled - min_val) / (max_val - min_val)
            sizes_valid = self.min_radius + normalized * (self.max_radius - self.min_radius)
        else:
            sizes_valid = np.full(len(scaled), (self.min_radius + self.max_radius) / 2)

        # Fill in all values
        sizes = np.full(len(values), self.min_radius)
        sizes[valid_mask] = sizes_valid

        return sizes

    def _add_bubbles(self, popup_columns: Optional[List[str]], cluster: bool):
        """Add bubble markers to map."""
        if popup_columns is None:
            popup_columns = [self.size_column]
            if self.color_column:
                popup_columns.append(self.color_column)

        # Create marker cluster if requested
        if cluster:
            marker_cluster = MarkerCluster(name="Bubbles").add_to(self.map)
            parent = marker_cluster
        else:
            parent = self.map

        # Add each bubble
        for idx, row in self.gdf.iterrows():
            # Get coordinates
            point = row.geometry
            coords = [point.y, point.x]

            # Get size
            size = self.sizes[idx]

            # Get color
            if self.color_column:
                color_value = row[self.color_column]
                if np.isnan(color_value):
                    color = "#808080"  # Gray for NaN
                else:
                    color = value_to_color(color_value, self.bin_edges, self.colors)
            else:
                color = self.colors[0]

            # Create popup
            popup_html = '<div style="font-family: monospace;">'
            for col in popup_columns:
                value = row[col]
                popup_html += f"<b>{col}:</b> {value}<br>"
            popup_html += "</div>"

            # Add circle marker
            folium.CircleMarker(
                location=coords,
                radius=size,
                color="black",
                weight=1,
                fill=True,
                fillColor=color,
                fillOpacity=self.opacity,
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(parent)

    def _add_legend(self, title: str):
        """Add size and color legend."""
        # Size legend
        size_legend_html = (
            '<div style="background-color: white; padding: 10px; border: 2px solid gray;">'
        )
        size_legend_html += f'<h4 style="margin: 0 0 10px 0;">{title}</h4>'

        # Show example sizes
        example_sizes = [self.min_radius, (self.min_radius + self.max_radius) / 2, self.max_radius]
        size_values = self.gdf[self.size_column].values
        valid_values = size_values[~np.isnan(size_values)]

        if len(valid_values) > 0:
            min_val, max_val = valid_values.min(), valid_values.max()
            example_values = [min_val, (min_val + max_val) / 2, max_val]

            for size, value in zip(example_sizes, example_values):
                size_legend_html += f'<div style="margin: 5px 0;">'
                size_legend_html += f'<svg height="{int(size*2)}" width="{int(size*2)}">'
                size_legend_html += f'<circle cx="{int(size)}" cy="{int(size)}" r="{int(size)}" '
                size_legend_html += (
                    f'stroke="black" stroke-width="1" fill="#3388ff" opacity="0.7"/>'
                )
                size_legend_html += f"</svg>"
                size_legend_html += f'<span style="margin-left: 10px;">{value:.1f}</span>'
                size_legend_html += f"</div>"

        size_legend_html += "</div>"

        # Add to map
        size_macro = folium.Element(
            f"""
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    z-index: 1000;">
            {size_legend_html}
        </div>
        """
        )

        self.map.get_root().html.add_child(size_macro)

        # Color legend if color_column provided
        if self.color_column:
            from .utils import create_legend_html

            color_legend_html = create_legend_html(
                self.bin_edges, self.colors, title=self.color_column
            )

            color_macro = folium.Element(
                f"""
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; 
                        z-index: 1000;">
                {color_legend_html}
            </div>
            """
            )

            self.map.get_root().html.add_child(color_macro)

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
        logger.info(f"Saved bubble map to {filepath}")

    def _repr_html_(self):
        """Return HTML representation for Jupyter notebooks."""
        return self.map._repr_html_()
