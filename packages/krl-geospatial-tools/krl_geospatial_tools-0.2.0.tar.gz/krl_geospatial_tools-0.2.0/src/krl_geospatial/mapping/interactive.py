"""
Interactive map creation using Folium.

This module provides classes for creating interactive web maps with markers,
popups, and various tile layers.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import folium
import geopandas as gpd
from folium import plugins
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from shapely.geometry import Point

logger = get_logger(__name__)


class InteractiveMap:
    """
    Interactive web map using Folium.

    Create interactive maps with markers, popups, polygons, and various
    tile layers. Export to HTML or display in Jupyter notebooks.

    Example:
        ```python
        from krl_geospatial.mapping import InteractiveMap
        import geopandas as gpd

        # Load data
        gdf = gpd.read_file("cities.shp")

        # Create map
        m = InteractiveMap(location=[40, -100], zoom_start=4)

        # Add markers
        m.add_markers(gdf, popup_columns=['name', 'population'])

        # Add layer control
        m.add_layer_control()

        # Save to HTML
        m.save("map.html")
        ```

    Attributes:
        map: Folium Map object
        location: Center location [lat, lon]
        zoom_start: Initial zoom level
    """

    def __init__(
        self,
        location: Optional[List[float]] = None,
        zoom_start: int = 10,
        tiles: str = "OpenStreetMap",
        width: str = "100%",
        height: str = "100%",
        **kwargs: Any,
    ):
        """
        Initialize an interactive map.

        Args:
            location: Center location [lat, lon]. If None, will auto-center on first data added.
            zoom_start: Initial zoom level (1-18)
            tiles: Tile layer ('OpenStreetMap', 'Stamen Terrain', 'Stamen Toner',
                   'CartoDB positron', 'CartoDB dark_matter')
            width: Map width (CSS format)
            height: Map height (CSS format)
            **kwargs: Additional arguments passed to folium.Map
        """
        self.location = location or [0, 0]
        self.zoom_start = zoom_start
        self.tiles = tiles

        self.map = folium.Map(
            location=self.location,
            zoom_start=zoom_start,
            tiles=tiles,
            width=width,
            height=height,
            **kwargs,
        )

        self._auto_centered = False
        logger.info(f"Initialized InteractiveMap at {self.location}, zoom={zoom_start}")

    def add_markers(
        self,
        gdf: gpd.GeoDataFrame,
        popup_columns: Optional[List[str]] = None,
        icon_color: str = "blue",
        icon: str = "info-sign",
        cluster: bool = False,
        name: str = "Markers",
        **kwargs: Any,
    ) -> "InteractiveMap":
        """
        Add point markers to the map.

        Args:
            gdf: GeoDataFrame with Point geometries
            popup_columns: Columns to include in popup (None = all columns)
            icon_color: Marker color ('red', 'blue', 'green', 'purple', 'orange',
                        'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
                        'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue',
                        'lightgreen', 'gray', 'black', 'lightgray')
            icon: Icon name (from Bootstrap or Font Awesome)
            cluster: If True, cluster nearby markers
            name: Layer name (for layer control)
            **kwargs: Additional arguments passed to folium.Marker

        Returns:
            self: InteractiveMap for method chaining

        Example:
            ```python
            m = InteractiveMap()
            m.add_markers(cities_gdf, popup_columns=['name', 'pop'], cluster=True)
            ```
        """
        if not all(gdf.geometry.geom_type == "Point"):
            logger.warning(
                "add_markers expects Point geometries. Non-point geometries will be skipped."
            )

        # Auto-center on first data if not manually set
        if not self._auto_centered and self.location == [0, 0]:
            bounds = gdf.total_bounds
            center_y = (bounds[1] + bounds[3]) / 2
            center_x = (bounds[0] + bounds[2]) / 2
            self.location = [center_y, center_x]
            self.map.location = self.location
            self._auto_centered = True
            logger.info(f"Auto-centered map at {self.location}")

        # Create feature group or marker cluster
        if cluster:
            feature_group = plugins.MarkerCluster(name=name)
        else:
            feature_group = folium.FeatureGroup(name=name)

        # Add markers
        for idx, row in gdf.iterrows():
            if row.geometry.geom_type != "Point":
                continue

            # Create popup HTML
            if popup_columns:
                popup_html = "<br>".join(
                    [f"<b>{col}:</b> {row[col]}" for col in popup_columns if col in gdf.columns]
                )
            else:
                # Include all non-geometry columns
                popup_html = "<br>".join(
                    [f"<b>{col}:</b> {row[col]}" for col in gdf.columns if col != "geometry"]
                )

            # Create marker
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=icon_color, icon=icon),
                **kwargs,
            ).add_to(feature_group)

        feature_group.add_to(self.map)
        logger.info(f"Added {len(gdf)} markers to map")

        return self

    def add_polygons(
        self,
        gdf: gpd.GeoDataFrame,
        style: Optional[Dict[str, Any]] = None,
        highlight_style: Optional[Dict[str, Any]] = None,
        popup_columns: Optional[List[str]] = None,
        name: str = "Polygons",
        **kwargs: Any,
    ) -> "InteractiveMap":
        """
        Add polygons to the map.

        Args:
            gdf: GeoDataFrame with Polygon/MultiPolygon geometries
            style: Style dictionary (fillColor, fillOpacity, color, weight, opacity)
            highlight_style: Style for hover highlight
            popup_columns: Columns to include in popup
            name: Layer name (for layer control)
            **kwargs: Additional arguments passed to folium.GeoJson

        Returns:
            self: InteractiveMap for method chaining

        Example:
            ```python
            m = InteractiveMap()
            m.add_polygons(
                counties_gdf,
                style={'fillColor': 'blue', 'fillOpacity': 0.3},
                popup_columns=['name', 'area']
            )
            ```
        """
        # Auto-center if needed
        if not self._auto_centered and self.location == [0, 0]:
            bounds = gdf.total_bounds
            center_y = (bounds[1] + bounds[3]) / 2
            center_x = (bounds[0] + bounds[2]) / 2
            self.location = [center_y, center_x]
            self.map.location = self.location
            self._auto_centered = True

        # Default styles
        default_style = {
            "fillColor": "blue",
            "fillOpacity": 0.3,
            "color": "black",
            "weight": 1,
            "opacity": 1.0,
        }
        default_highlight = {"fillColor": "yellow", "fillOpacity": 0.5, "color": "red", "weight": 2}

        style = {**default_style, **(style or {})}
        highlight_style = {**default_highlight, **(highlight_style or {})}

        # Create popup fields function
        def create_popup(feature):
            if popup_columns:
                props = feature["properties"]
                html = "<br>".join(
                    [f"<b>{col}:</b> {props.get(col, 'N/A')}" for col in popup_columns]
                )
                return folium.Popup(html, max_width=300)
            return None

        # Add GeoJson layer
        folium.GeoJson(
            gdf,
            name=name,
            style_function=lambda x: style,
            highlight_function=lambda x: highlight_style,
            popup=folium.GeoJsonPopup(fields=popup_columns) if popup_columns else None,
            **kwargs,
        ).add_to(self.map)

        logger.info(f"Added {len(gdf)} polygons to map")

        return self

    def add_heatmap(
        self,
        gdf: gpd.GeoDataFrame,
        intensity_column: Optional[str] = None,
        radius: int = 15,
        blur: int = 15,
        name: str = "Heatmap",
        **kwargs: Any,
    ) -> "InteractiveMap":
        """
        Add a heatmap layer.

        Args:
            gdf: GeoDataFrame with Point geometries
            intensity_column: Column to use for intensity (None = equal weights)
            radius: Radius of each point in pixels
            blur: Blur radius
            name: Layer name
            **kwargs: Additional arguments passed to folium.plugins.HeatMap

        Returns:
            self: InteractiveMap for method chaining

        Example:
            ```python
            m = InteractiveMap()
            m.add_heatmap(crime_gdf, intensity_column='severity')
            ```
        """
        if not all(gdf.geometry.geom_type == "Point"):
            raise ValueError("Heatmap requires Point geometries")

        # Prepare data
        if intensity_column:
            heat_data = [
                [row.geometry.y, row.geometry.x, row[intensity_column]] for _, row in gdf.iterrows()
            ]
        else:
            heat_data = [[row.geometry.y, row.geometry.x] for _, row in gdf.iterrows()]

        # Add heatmap
        plugins.HeatMap(heat_data, name=name, radius=radius, blur=blur, **kwargs).add_to(self.map)

        logger.info(f"Added heatmap with {len(gdf)} points")

        return self

    def add_tile_layer(
        self, tiles: str, name: Optional[str] = None, **kwargs: Any
    ) -> "InteractiveMap":
        """
        Add an additional tile layer.

        Args:
            tiles: Tile layer name or URL
            name: Layer name for control
            **kwargs: Additional arguments passed to folium.TileLayer

        Returns:
            self: InteractiveMap for method chaining
        """
        folium.TileLayer(tiles=tiles, name=name or tiles, **kwargs).add_to(self.map)
        logger.info(f"Added tile layer: {name or tiles}")
        return self

    def add_layer_control(self, **kwargs: Any) -> "InteractiveMap":
        """
        Add layer control to toggle layers.

        Args:
            **kwargs: Additional arguments passed to folium.LayerControl

        Returns:
            self: InteractiveMap for method chaining
        """
        folium.LayerControl(**kwargs).add_to(self.map)
        logger.info("Added layer control")
        return self

    def fit_bounds(self, gdf: gpd.GeoDataFrame) -> "InteractiveMap":
        """
        Fit map bounds to GeoDataFrame extent.

        Args:
            gdf: GeoDataFrame to fit bounds to

        Returns:
            self: InteractiveMap for method chaining
        """
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        self.map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        logger.info("Fit map bounds to data")
        return self

    def save(self, filepath: Union[str, Path]) -> None:
        """
        Save map to HTML file.

        Args:
            filepath: Path to output HTML file

        Example:
            ```python
            m = InteractiveMap()
            m.add_markers(gdf)
            m.save("output.html")
            ```
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        self.map.save(str(filepath))
        logger.info(f"Saved map to {filepath}")

    def _repr_html_(self) -> str:
        """Return HTML representation for Jupyter notebooks."""
        return self.map._repr_html_()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"InteractiveMap(location={self.location}, zoom={self.zoom_start})"
