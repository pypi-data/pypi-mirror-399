"""
Choropleth mapping for thematic visualizations.

This module provides choropleth (thematic) mapping capabilities with
data classification, color schemes, and legend generation.
"""

from typing import Any, Dict, List, Optional, Union

import folium
import geopandas as gpd
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)

from .utils import (
    ColorScheme,
    classify_values,
    create_legend_html,
    get_color_scheme,
    value_to_color,
)

logger = get_logger(__name__)


class ChoroplethMap:
    """
    Choropleth (thematic) map with data classification and color schemes.

    A choropleth map displays quantitative data by shading areas according
    to their values. This class handles data classification, color mapping,
    and legend generation.

    Attributes:
        map: Underlying folium Map object

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.mapping import ChoroplethMap

        # Load data
        gdf = gpd.read_file('states.shp')

        # Create choropleth map
        m = ChoroplethMap(
            gdf,
            column='population',
            scheme='quantiles',
            k=5,
            cmap='YlOrRd',
            legend=True
        )

        # Save to file
        m.save('population_map.html')

        # Display in Jupyter
        m  # Shows interactive map
        ```
    """

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        column: str,
        scheme: str = "quantiles",
        k: int = 5,
        cmap: Union[str, ColorScheme] = "YlOrRd",
        reverse_colors: bool = False,
        nan_color: str = "#808080",
        legend: bool = True,
        legend_title: Optional[str] = None,
        location: Optional[List[float]] = None,
        zoom_start: int = 4,
        tiles: str = "OpenStreetMap",
        popup_columns: Optional[List[str]] = None,
        style: Optional[Dict[str, Any]] = None,
        highlight_style: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize choropleth map.

        Args:
            gdf: GeoDataFrame with geometry and data
            column: Column name to visualize
            scheme: Classification scheme:
                - 'quantiles': Equal counts per bin
                - 'equal_interval': Equal-width bins
                - 'natural_breaks': Jenks natural breaks
                - 'std_mean': Standard deviation
                - 'fisher_jenks': Fisher-Jenks algorithm
            k: Number of classes/bins
            cmap: Color scheme (ColorScheme enum or string)
            reverse_colors: Reverse color order
            nan_color: Color for missing/NaN values
            legend: Show legend on map
            legend_title: Legend title (defaults to column name)
            location: Map center [lat, lon]
            zoom_start: Initial zoom level
            tiles: Tile layer ('OpenStreetMap', 'CartoDB positron', etc.)
            popup_columns: Columns to show in popups
            style: Base polygon style dict
            highlight_style: Hover highlight style dict
        """
        self.gdf = gdf.copy()
        self.column = column
        self.scheme = scheme
        self.k = k
        self.cmap = cmap
        self.nan_color = nan_color

        # Validate column
        if column not in self.gdf.columns:
            raise ValueError(f"Column '{column}' not found in GeoDataFrame")

        # Ensure CRS is WGS84 for folium
        if self.gdf.crs and self.gdf.crs.to_epsg() != 4326:
            logger.info(f"Reprojecting from {self.gdf.crs} to EPSG:4326")
            self.gdf = self.gdf.to_crs(epsg=4326)

        # Initialize map
        if location is None:
            # Center on data
            bounds = self.gdf.total_bounds  # [minx, miny, maxx, maxy]
            location = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

        self.map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)

        # Classify data
        values = self.gdf[column].values
        self.bin_indices, self.bin_edges = classify_values(values, method=scheme, k=k)

        # Get colors
        self.colors = get_color_scheme(cmap, n_colors=k, reverse=reverse_colors)

        # Default styles
        if style is None:
            style = {"fillOpacity": 0.7, "weight": 1, "color": "black"}
        if highlight_style is None:
            highlight_style = {"fillOpacity": 0.9, "weight": 3, "color": "white"}

        self.style = style
        self.highlight_style = highlight_style

        # Add data to map
        self._add_choropleth_layer(popup_columns)

        # Add legend
        if legend:
            legend_title = legend_title or column
            self._add_legend(legend_title)

        logger.info(f"Created choropleth map for column '{column}' with {k} classes")

    def _add_choropleth_layer(self, popup_columns: Optional[List[str]] = None):
        """Add choropleth layer to map."""
        # Prepare popup columns
        if popup_columns is None:
            popup_columns = [self.column]

        # Create style function
        def style_function(feature):
            """Style based on data value."""
            value = feature["properties"].get(self.column)

            if value is None or np.isnan(value):
                color = self.nan_color
            else:
                color = value_to_color(value, self.bin_edges, self.colors, self.nan_color)

            return {**self.style, "fillColor": color}

        # Create highlight function
        def highlight_function(feature):
            """Highlight style on hover."""
            return self.highlight_style

        # Add GeoJson layer
        folium.GeoJson(
            self.gdf,
            name="Choropleth",
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=popup_columns,
                aliases=[col.replace("_", " ").title() for col in popup_columns],
                localize=True,
            ),
        ).add_to(self.map)

    def _add_legend(self, title: str):
        """Add legend to map."""
        legend_html = create_legend_html(self.bin_edges, self.colors, title=title)

        # Create legend element
        legend_macro = folium.Element(
            f"""
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    z-index: 1000;">
            {legend_html}
        </div>
        """
        )

        self.map.get_root().html.add_child(legend_macro)

    def add_tile_layer(self, tiles: str, name: str):
        """
        Add an additional tile layer.

        Args:
            tiles: Tile layer name or URL template
            name: Layer name for control
        """
        folium.TileLayer(tiles=tiles, name=name).add_to(self.map)
        logger.debug(f"Added tile layer: {name}")

    def add_layer_control(self):
        """Add layer control for toggling layers."""
        folium.LayerControl().add_to(self.map)
        logger.debug("Added layer control")

    def fit_bounds(self):
        """Fit map to data bounds."""
        bounds = self.gdf.total_bounds  # [minx, miny, maxx, maxy]
        self.map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        logger.debug("Fitted map to data bounds")

    def save(self, filepath: str):
        """
        Save map to HTML file.

        Args:
            filepath: Output file path
        """
        self.map.save(filepath)
        logger.info(f"Saved choropleth map to {filepath}")

    def _repr_html_(self):
        """Return HTML representation for Jupyter notebooks."""
        return self.map._repr_html_()

    def get_classification_info(self) -> Dict[str, Any]:
        """
        Get information about the data classification.

        Returns:
            Dictionary with classification details:
                - scheme: Classification method
                - k: Number of classes
                - bin_edges: Bin edge values
                - colors: Color list
                - counts: Number of features per bin
        """
        # Count features per bin
        counts = [np.sum(self.bin_indices == i) for i in range(self.k)]

        return {
            "scheme": self.scheme,
            "k": self.k,
            "bin_edges": self.bin_edges,
            "colors": self.colors,
            "counts": counts,
        }
