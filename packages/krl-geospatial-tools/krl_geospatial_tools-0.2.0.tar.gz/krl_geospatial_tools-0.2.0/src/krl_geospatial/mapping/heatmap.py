"""
Density heatmap visualization using kernel density estimation.

This module provides heatmap capabilities for visualizing point density
patterns and hotspots.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import folium
import geopandas as gpd
import numpy as np
from folium.plugins import HeatMap
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)

logger = get_logger(__name__)


class DensityHeatmap:
    """
    Density heatmap visualization.

    Creates smooth density surfaces from point data using kernel density
    estimation. Useful for identifying hotspots and concentration patterns.

    Attributes:
        map: Underlying folium Map object

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.mapping import DensityHeatmap

        # Load point data
        incidents = gpd.read_file('crime_incidents.shp')

        # Create density heatmap
        m = DensityHeatmap(
            incidents,
            intensity_column='severity',
            radius=15,
            blur=10,
            gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
        )

        # Save to file
        m.save('crime_density.html')
        ```
    """

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        intensity_column: Optional[str] = None,
        radius: int = 15,
        blur: int = 10,
        max_zoom: int = 18,
        min_opacity: float = 0.2,
        max_opacity: float = 0.8,
        gradient: Optional[Dict[float, str]] = None,
        location: Optional[List[float]] = None,
        zoom_start: int = 10,
        tiles: str = "OpenStreetMap",
    ):
        """
        Initialize density heatmap.

        Args:
            gdf: GeoDataFrame with point geometries
            intensity_column: Column for intensity weighting (optional)
            radius: Radius of influence for each point (pixels)
            blur: Amount of blur to apply
            max_zoom: Maximum zoom level for heatmap
            min_opacity: Minimum opacity
            max_opacity: Maximum opacity
            gradient: Custom color gradient {position: color}
            location: Map center [lat, lon]
            zoom_start: Initial zoom level
            tiles: Base tile layer
        """
        self.gdf = gdf.copy()
        self.intensity_column = intensity_column
        self.radius = radius
        self.blur = blur

        # Validate intensity column
        if intensity_column and intensity_column not in self.gdf.columns:
            raise ValueError(f"Intensity column '{intensity_column}' not found")

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

        # Prepare data for HeatMap
        heat_data = self._prepare_heat_data()

        # Default gradient if not provided
        if gradient is None:
            gradient = {0.0: "blue", 0.5: "lime", 0.7: "yellow", 1.0: "red"}

        # Add heatmap
        HeatMap(
            heat_data,
            radius=radius,
            blur=blur,
            max_zoom=max_zoom,
            min_opacity=min_opacity,
            max_opacity=max_opacity,
            gradient=gradient,
        ).add_to(self.map)

        logger.info(f"Created density heatmap with {len(self.gdf)} points")

    def _prepare_heat_data(self) -> List[List[float]]:
        """Prepare data for folium HeatMap plugin."""
        heat_data = []

        for idx, row in self.gdf.iterrows():
            point = row.geometry

            # Get coordinates [lat, lon]
            coords = [point.y, point.x]

            # Add intensity if column provided
            if self.intensity_column:
                intensity = row[self.intensity_column]
                if not np.isnan(intensity):
                    coords.append(float(intensity))

            heat_data.append(coords)

        return heat_data

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
        logger.info(f"Saved density heatmap to {filepath}")

    def _repr_html_(self):
        """Return HTML representation for Jupyter notebooks."""
        return self.map._repr_html_()


class GridDensity:
    """
    Grid-based density visualization.

    Creates hexagonal or square grid cells colored by point density.
    More discrete than kernel density, useful for administrative analysis.

    Attributes:
        map: Underlying folium Map object
        grid_gdf: GeoDataFrame with grid cells and densities

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.mapping import GridDensity

        # Load point data
        points = gpd.read_file('points.shp')

        # Create grid density map
        m = GridDensity(
            points,
            cell_size=1000,  # 1km cells
            grid_type='hexagon',
            cmap='YlOrRd'
        )

        # Save to file
        m.save('grid_density.html')
        ```
    """

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        cell_size: float,
        grid_type: str = "hexagon",
        cmap: str = "YlOrRd",
        classification: str = "quantiles",
        k: int = 5,
        opacity: float = 0.7,
        legend: bool = True,
        location: Optional[List[float]] = None,
        zoom_start: int = 10,
        tiles: str = "OpenStreetMap",
    ):
        """
        Initialize grid density map.

        Args:
            gdf: GeoDataFrame with point geometries
            cell_size: Grid cell size in meters
            grid_type: 'hexagon' or 'square'
            cmap: Color scheme
            classification: Classification method
            k: Number of classes
            opacity: Cell opacity
            legend: Show legend
            location: Map center [lat, lon]
            zoom_start: Initial zoom level
            tiles: Base tile layer
        """
        self.gdf = gdf.copy()
        self.cell_size = cell_size
        self.grid_type = grid_type

        # Check geometry type
        geom_types = self.gdf.geometry.geom_type.unique()
        if not all(gt == "Point" for gt in geom_types):
            logger.warning("Non-point geometries found, using centroids")
            self.gdf["geometry"] = self.gdf.geometry.centroid

        # Ensure projected CRS for cell_size calculation
        if self.gdf.crs and self.gdf.crs.to_epsg() == 4326:
            # Reproject to Web Mercator for grid creation
            logger.info("Reprojecting to Web Mercator for grid creation")
            gdf_proj = self.gdf.to_crs(epsg=3857)
        else:
            gdf_proj = self.gdf.copy()

        # Create grid
        self.grid_gdf = self._create_grid(gdf_proj)

        # Count points in each cell
        self._count_points(gdf_proj)

        # Reproject grid back to WGS84 for folium
        self.grid_gdf = self.grid_gdf.to_crs(epsg=4326)

        # Initialize map
        if location is None:
            bounds = self.gdf.total_bounds
            location = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

        self.map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)

        # Create choropleth from grid
        from .choropleth import ChoroplethMap
        from .utils import classify_values, get_color_scheme, value_to_color

        # Classify densities
        values = self.grid_gdf["density"].values
        bin_indices, bin_edges = classify_values(values, method=classification, k=k)
        colors = get_color_scheme(cmap, n_colors=k)

        # Add grid cells
        for idx, row in self.grid_gdf.iterrows():
            density = row["density"]

            if density > 0:  # Only show cells with points
                color = value_to_color(density, bin_edges, colors)

                folium.GeoJson(
                    row.geometry,
                    style_function=lambda x, c=color: {
                        "fillColor": c,
                        "fillOpacity": opacity,
                        "color": "black",
                        "weight": 1,
                    },
                    tooltip=f"Density: {int(density)}",
                ).add_to(self.map)

        # Add legend
        if legend:
            from .utils import create_legend_html

            legend_html = create_legend_html(bin_edges, colors, title="Point Density")

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

        logger.info(f"Created grid density map with {len(self.grid_gdf)} cells")

    def _create_grid(self, gdf_proj: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Create hexagonal or square grid."""
        import math

        from shapely.geometry import Polygon

        bounds = gdf_proj.total_bounds
        minx, miny, maxx, maxy = bounds

        cells = []

        if self.grid_type == "hexagon":
            # Hexagonal grid
            width = self.cell_size
            height = self.cell_size * math.sqrt(3) / 2

            rows = int((maxy - miny) / height) + 1
            cols = int((maxx - minx) / width) + 1

            for row in range(rows):
                for col in range(cols):
                    # Offset every other row
                    offset = width / 2 if row % 2 == 1 else 0
                    x = minx + col * width + offset
                    y = miny + row * height

                    # Create hexagon
                    hex_points = []
                    for i in range(6):
                        angle = math.pi / 3 * i
                        px = x + width / 2 * math.cos(angle)
                        py = y + height / 2 * math.sin(angle)
                        hex_points.append((px, py))

                    cells.append(Polygon(hex_points))

        else:  # square
            rows = int((maxy - miny) / self.cell_size) + 1
            cols = int((maxx - minx) / self.cell_size) + 1

            for row in range(rows):
                for col in range(cols):
                    x = minx + col * self.cell_size
                    y = miny + row * self.cell_size

                    cell = Polygon(
                        [
                            (x, y),
                            (x + self.cell_size, y),
                            (x + self.cell_size, y + self.cell_size),
                            (x, y + self.cell_size),
                        ]
                    )
                    cells.append(cell)

        return gpd.GeoDataFrame({"geometry": cells}, crs=gdf_proj.crs)

    def _count_points(self, gdf_proj: gpd.GeoDataFrame):
        """Count points in each grid cell."""
        # Spatial join to count points
        joined = gpd.sjoin(self.grid_gdf, gdf_proj, how="left", predicate="contains")

        # Count points per cell
        counts = joined.groupby(joined.index).size()
        self.grid_gdf["density"] = 0
        self.grid_gdf.loc[counts.index, "density"] = counts.values

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
        bounds = self.grid_gdf.total_bounds
        self.map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        logger.debug("Fitted map to data bounds")

    def save(self, filepath: str):
        """
        Save map to HTML file.

        Args:
            filepath: Output file path
        """
        self.map.save(filepath)
        logger.info(f"Saved grid density map to {filepath}")

    def _repr_html_(self):
        """Return HTML representation for Jupyter notebooks."""
        return self.map._repr_html_()
