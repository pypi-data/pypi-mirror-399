"""
Map export utilities for various output formats.

This module provides export capabilities for saving maps to HTML, PNG,
SVG, PDF, and other formats.
"""

import os
from pathlib import Path
from typing import Optional, Union

import folium
import geopandas as gpd
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)

logger = get_logger(__name__)


class MapExporter:
    """
    Utility class for exporting maps to various formats.

    Supports exporting folium maps and static matplotlib maps to:
    - HTML (interactive)
    - PNG (raster image)
    - SVG (vector graphics)
    - PDF (document)
    - GeoJSON (data export)

    Example:
        ```python
        from krl_geospatial.mapping import InteractiveMap, MapExporter

        # Create map
        m = InteractiveMap(location=[37.7749, -122.4194])
        m.add_markers(gdf)

        # Export to multiple formats
        exporter = MapExporter(m.map)
        exporter.to_html('map.html')
        exporter.to_png('map.png', width=1200, height=800)
        ```
    """

    def __init__(self, map_obj: Union[folium.Map, "matplotlib.figure.Figure"]):
        """
        Initialize exporter.

        Args:
            map_obj: Folium Map or matplotlib Figure object
        """
        self.map_obj = map_obj
        self.map_type = self._detect_map_type()

        logger.debug(f"Initialized MapExporter for {self.map_type} map")

    def _detect_map_type(self) -> str:
        """Detect the type of map object."""
        if isinstance(self.map_obj, folium.Map):
            return "folium"
        elif hasattr(self.map_obj, "savefig"):  # matplotlib Figure
            return "matplotlib"
        else:
            raise TypeError(f"Unsupported map type: {type(self.map_obj)}")

    def to_html(self, filepath: str, inline: bool = False, cdn_links: bool = True) -> None:
        """
        Export to HTML file.

        Args:
            filepath: Output file path
            inline: Embed all resources inline (larger file)
            cdn_links: Use CDN links for libraries (smaller file)

        Raises:
            ValueError: If map type doesn't support HTML export
        """
        if self.map_type != "folium":
            raise ValueError("HTML export only supported for folium maps")

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        # Save HTML
        self.map_obj.save(filepath)

        logger.info(f"Exported map to HTML: {filepath}")

    def to_png(
        self, filepath: str, width: int = 1200, height: int = 800, dpi: int = 96, delay: int = 1
    ) -> None:
        """
        Export to PNG image.

        For folium maps, requires selenium and a webdriver (Chrome/Firefox).
        For matplotlib maps, uses native export.

        Args:
            filepath: Output file path
            width: Image width in pixels
            height: Image height in pixels
            dpi: Resolution (dots per inch) for matplotlib
            delay: Delay in seconds for folium map rendering

        Raises:
            ImportError: If required dependencies not installed
            ValueError: If export fails
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        if self.map_type == "folium":
            # Export folium map to PNG using selenium
            try:
                import tempfile
                import time

                import selenium
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
            except ImportError:
                raise ImportError(
                    "PNG export for folium maps requires: pip install selenium\n"
                    "Also install ChromeDriver: https://chromedriver.chromium.org/"
                )

            # Save to temporary HTML
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
                temp_html = f.name
                self.map_obj.save(temp_html)

            try:
                # Setup Chrome in headless mode
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(f"--window-size={width},{height}")

                driver = webdriver.Chrome(options=chrome_options)
                driver.get(f"file://{os.path.abspath(temp_html)}")

                # Wait for map to render
                time.sleep(delay)

                # Take screenshot
                driver.save_screenshot(filepath)
                driver.quit()

                logger.info(f"Exported folium map to PNG: {filepath}")

            finally:
                # Clean up temp file
                os.unlink(temp_html)

        elif self.map_type == "matplotlib":
            # Export matplotlib figure to PNG
            self.map_obj.savefig(
                filepath, format="png", dpi=dpi, bbox_inches="tight", facecolor="white"
            )

            logger.info(f"Exported matplotlib map to PNG: {filepath}")

    def to_svg(self, filepath: str) -> None:
        """
        Export to SVG vector graphics.

        Only supported for matplotlib maps currently.

        Args:
            filepath: Output file path

        Raises:
            ValueError: If map type doesn't support SVG export
        """
        if self.map_type != "matplotlib":
            raise ValueError("SVG export only supported for matplotlib maps")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        self.map_obj.savefig(filepath, format="svg", bbox_inches="tight")

        logger.info(f"Exported map to SVG: {filepath}")

    def to_pdf(self, filepath: str, dpi: int = 300) -> None:
        """
        Export to PDF document.

        For matplotlib maps, uses native PDF export.
        For folium maps, requires additional tools (wkhtmltopdf).

        Args:
            filepath: Output file path
            dpi: Resolution for matplotlib export

        Raises:
            ValueError: If export not supported for map type
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        if self.map_type == "matplotlib":
            self.map_obj.savefig(filepath, format="pdf", dpi=dpi, bbox_inches="tight")

            logger.info(f"Exported map to PDF: {filepath}")

        elif self.map_type == "folium":
            # Try using pdfkit/wkhtmltopdf
            try:
                import tempfile

                import pdfkit
            except ImportError:
                raise ImportError(
                    "PDF export for folium maps requires: pip install pdfkit\n"
                    "Also install wkhtmltopdf: https://wkhtmltopdf.org/"
                )

            # Save to temporary HTML
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
                temp_html = f.name
                self.map_obj.save(temp_html)

            try:
                # Convert HTML to PDF
                pdfkit.from_file(temp_html, filepath)
                logger.info(f"Exported folium map to PDF: {filepath}")
            finally:
                os.unlink(temp_html)


def export_geodataframe(
    gdf: gpd.GeoDataFrame, filepath: str, driver: Optional[str] = None, **kwargs
) -> None:
    """
    Export GeoDataFrame to various formats.

    Convenience function for exporting geographic data.

    Args:
        gdf: GeoDataFrame to export
        filepath: Output file path
        driver: GeoPandas driver (auto-detected from extension)
        **kwargs: Additional arguments for to_file()

    Example:
        ```python
        from krl_geospatial.mapping import export_geodataframe

        # Export to various formats
        export_geodataframe(gdf, 'data.geojson')
        export_geodataframe(gdf, 'data.shp')
        export_geodataframe(gdf, 'data.gpkg')
        ```
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    # Auto-detect driver from extension
    if driver is None:
        ext = Path(filepath).suffix.lower()
        driver_map = {
            ".geojson": "GeoJSON",
            ".json": "GeoJSON",
            ".shp": "ESRI Shapefile",
            ".gpkg": "GPKG",
            ".kml": "KML",
            ".parquet": "Parquet",
        }
        driver = driver_map.get(ext)

    # Export
    gdf.to_file(filepath, driver=driver, **kwargs)

    logger.info(f"Exported GeoDataFrame to {filepath}")


def export_to_geojson(
    gdf: gpd.GeoDataFrame, filepath: str, drop_columns: Optional[list] = None, precision: int = 6
) -> None:
    """
    Export GeoDataFrame to GeoJSON with options.

    Args:
        gdf: GeoDataFrame to export
        filepath: Output file path
        drop_columns: Columns to exclude
        precision: Coordinate precision (decimal places)
    """
    gdf_export = gdf.copy()

    if drop_columns:
        gdf_export = gdf_export.drop(columns=drop_columns)

    # Convert to WGS84 if needed
    if gdf_export.crs and gdf_export.crs.to_epsg() != 4326:
        logger.info("Reprojecting to WGS84 for GeoJSON")
        gdf_export = gdf_export.to_crs(epsg=4326)

    # Export
    gdf_export.to_file(filepath, driver="GeoJSON")

    logger.info(f"Exported to GeoJSON: {filepath}")
