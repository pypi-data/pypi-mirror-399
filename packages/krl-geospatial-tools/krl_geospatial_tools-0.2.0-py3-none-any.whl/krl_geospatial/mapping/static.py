"""
Static map generation using matplotlib for publication-quality maps.

This module provides tools for creating static, publication-ready maps
using matplotlib, perfect for papers, reports, and presentations.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from matplotlib import cm
from matplotlib.colors import Normalize

from .utils import classify_values, get_color_scheme

logger = get_logger(__name__)


class StaticMap:
    """
    Static map generator using matplotlib.

    Creates publication-ready static maps with customizable styling,
    legends, scale bars, and north arrows.

    Attributes:
        fig: Matplotlib Figure object
        ax: Matplotlib Axes object

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.mapping import StaticMap

        # Load data
        counties = gpd.read_file('counties.shp')

        # Create static map
        m = StaticMap(figsize=(12, 8))
        m.add_polygons(
            counties,
            column='population',
            cmap='YlOrRd',
            legend=True,
            title='Population by County'
        )

        # Save to file
        m.save('population_map.png', dpi=300)
        ```
    """

    def __init__(
        self, figsize: Tuple[float, float] = (10, 8), dpi: int = 100, facecolor: str = "white"
    ):
        """
        Initialize static map.

        Args:
            figsize: Figure size (width, height) in inches
            dpi: Resolution (dots per inch)
            facecolor: Background color
        """
        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=dpi)
        self.fig.patch.set_facecolor(facecolor)
        self.ax.set_aspect("equal")

        # Remove axes
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)

        logger.debug(f"Initialized StaticMap with figsize={figsize}")

    def add_polygons(
        self,
        gdf: gpd.GeoDataFrame,
        column: Optional[str] = None,
        cmap: str = "viridis",
        classification: str = "quantiles",
        k: int = 5,
        edgecolor: str = "black",
        linewidth: float = 0.5,
        alpha: float = 0.7,
        legend: bool = False,
        legend_title: Optional[str] = None,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
    ) -> None:
        """
        Add polygon layer.

        Args:
            gdf: GeoDataFrame with polygon geometries
            column: Column to visualize (choropleth)
            cmap: Color map
            classification: Classification method
            k: Number of classes
            edgecolor: Edge color
            linewidth: Edge line width
            alpha: Transparency (0-1)
            legend: Show legend
            legend_title: Custom legend title
            vmin: Minimum value for color scale
            vmax: Maximum value for color scale
        """
        if column:
            # Choropleth map
            values = gdf[column].values

            if vmin is None:
                vmin = np.nanmin(values)
            if vmax is None:
                vmax = np.nanmax(values)

            norm = Normalize(vmin=vmin, vmax=vmax)
            cmap_obj = cm.get_cmap(cmap)

            gdf.plot(
                ax=self.ax,
                column=column,
                cmap=cmap,
                norm=norm,
                edgecolor=edgecolor,
                linewidth=linewidth,
                alpha=alpha,
                legend=legend,
                legend_kwds={"label": legend_title or column},
            )
        else:
            # Simple polygon map
            gdf.plot(
                ax=self.ax,
                edgecolor=edgecolor,
                linewidth=linewidth,
                facecolor="lightgray",
                alpha=alpha,
            )

        logger.debug(f"Added {len(gdf)} polygons to static map")

    def add_points(
        self,
        gdf: gpd.GeoDataFrame,
        column: Optional[str] = None,
        size: Union[float, str] = 10,
        color: str = "red",
        cmap: Optional[str] = None,
        marker: str = "o",
        alpha: float = 0.7,
        edgecolor: str = "black",
        linewidth: float = 0.5,
        legend: bool = False,
    ) -> None:
        """
        Add point layer.

        Args:
            gdf: GeoDataFrame with point geometries
            column: Column for color values
            size: Marker size (fixed or column name)
            color: Marker color
            cmap: Color map if column provided
            marker: Marker style
            alpha: Transparency
            edgecolor: Edge color
            linewidth: Edge line width
            legend: Show legend
        """
        # Extract coordinates
        x = gdf.geometry.x
        y = gdf.geometry.y

        # Determine sizes
        if isinstance(size, str) and size in gdf.columns:
            sizes = gdf[size].values
        else:
            sizes = size

        # Plot points
        if column and cmap:
            scatter = self.ax.scatter(
                x,
                y,
                s=sizes,
                c=gdf[column].values,
                cmap=cmap,
                marker=marker,
                alpha=alpha,
                edgecolors=edgecolor,
                linewidths=linewidth,
            )

            if legend:
                plt.colorbar(scatter, ax=self.ax, label=column)
        else:
            self.ax.scatter(
                x,
                y,
                s=sizes,
                color=color,
                marker=marker,
                alpha=alpha,
                edgecolors=edgecolor,
                linewidths=linewidth,
            )

        logger.debug(f"Added {len(gdf)} points to static map")

    def add_lines(
        self,
        gdf: gpd.GeoDataFrame,
        column: Optional[str] = None,
        linewidth: Union[float, str] = 1.0,
        color: str = "blue",
        cmap: Optional[str] = None,
        alpha: float = 0.7,
    ) -> None:
        """
        Add line layer.

        Args:
            gdf: GeoDataFrame with line geometries
            column: Column for color values
            linewidth: Line width (fixed or column name)
            color: Line color
            cmap: Color map if column provided
            alpha: Transparency
        """
        if column and cmap:
            gdf.plot(ax=self.ax, column=column, cmap=cmap, linewidth=linewidth, alpha=alpha)
        else:
            gdf.plot(ax=self.ax, color=color, linewidth=linewidth, alpha=alpha)

        logger.debug(f"Added {len(gdf)} lines to static map")

    def add_basemap(
        self, source: str = "OpenStreetMap", zoom: int = 10, attribution: bool = True
    ) -> None:
        """
        Add basemap from web tiles.

        Requires contextily package.

        Args:
            source: Basemap source
            zoom: Zoom level
            attribution: Show attribution text

        Raises:
            ImportError: If contextily not installed
        """
        try:
            import contextily as ctx
        except ImportError:
            raise ImportError("Basemap requires: pip install contextily")

        # Get current bounds
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Add basemap
        ctx.add_basemap(self.ax, source=source, zoom=zoom, attribution=attribution)

        # Restore bounds
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        logger.debug(f"Added {source} basemap")

    def add_scale_bar(
        self, location: str = "lower right", length_km: float = 10, linewidth: float = 3
    ) -> None:
        """
        Add scale bar.

        Args:
            location: Position ('lower right', 'upper left', etc.)
            length_km: Scale bar length in kilometers
            linewidth: Line width
        """
        # This is a simplified version - full implementation would need
        # to calculate actual distances based on CRS and latitude
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle

        # Get axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Calculate position
        if "right" in location:
            x = xlim[1] - 0.15 * (xlim[1] - xlim[0])
        else:
            x = xlim[0] + 0.05 * (xlim[1] - xlim[0])

        if "lower" in location:
            y = ylim[0] + 0.05 * (ylim[1] - ylim[0])
        else:
            y = ylim[1] - 0.05 * (ylim[1] - ylim[0])

        # Approximate scale (this is simplified)
        scale_width = 0.1 * (xlim[1] - xlim[0])

        # Draw scale bar
        self.ax.plot([x, x + scale_width], [y, y], "k-", linewidth=linewidth)

        # Add text
        self.ax.text(
            x + scale_width / 2,
            y - 0.01 * (ylim[1] - ylim[0]),
            f"{length_km} km",
            ha="center",
            va="top",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        logger.debug("Added scale bar")

    def add_north_arrow(self, location: str = "upper right", size: float = 0.05) -> None:
        """
        Add north arrow.

        Args:
            location: Position ('upper right', 'lower left', etc.)
            size: Arrow size as fraction of plot
        """
        from matplotlib.patches import FancyArrow

        # Get axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Calculate position
        if "right" in location:
            x = xlim[1] - 0.08 * (xlim[1] - xlim[0])
        else:
            x = xlim[0] + 0.08 * (xlim[1] - xlim[0])

        if "upper" in location:
            y = ylim[1] - 0.1 * (ylim[1] - ylim[0])
        else:
            y = ylim[0] + 0.1 * (ylim[1] - ylim[0])

        # Arrow dimensions
        arrow_length = size * (ylim[1] - ylim[0])
        arrow_width = arrow_length * 0.3

        # Draw arrow
        arrow = FancyArrow(
            x,
            y,
            0,
            arrow_length,
            width=arrow_width,
            head_width=arrow_width * 2,
            head_length=arrow_length * 0.3,
            fc="black",
            ec="black",
        )
        self.ax.add_patch(arrow)

        # Add "N" text
        self.ax.text(
            x, y + arrow_length * 1.2, "N", ha="center", va="bottom", fontsize=14, fontweight="bold"
        )

        logger.debug("Added north arrow")

    def set_title(self, title: str, fontsize: int = 16, fontweight: str = "bold") -> None:
        """
        Set map title.

        Args:
            title: Title text
            fontsize: Font size
            fontweight: Font weight
        """
        self.ax.set_title(title, fontsize=fontsize, fontweight=fontweight, pad=20)

    def set_extent(self, bounds: Union[List[float], Tuple[float, float, float, float]]) -> None:
        """
        Set map extent.

        Args:
            bounds: [minx, miny, maxx, maxy]
        """
        self.ax.set_xlim(bounds[0], bounds[2])
        self.ax.set_ylim(bounds[1], bounds[3])

    def tight_layout(self) -> None:
        """Apply tight layout to figure."""
        self.fig.tight_layout()

    def save(
        self, filepath: str, dpi: Optional[int] = None, bbox_inches: str = "tight", **kwargs
    ) -> None:
        """
        Save map to file.

        Args:
            filepath: Output file path
            dpi: Resolution (overrides initialization dpi)
            bbox_inches: Bounding box for saved figure
            **kwargs: Additional arguments for savefig()
        """
        self.fig.savefig(
            filepath, dpi=dpi or self.fig.dpi, bbox_inches=bbox_inches, facecolor="white", **kwargs
        )

        logger.info(f"Saved static map to {filepath}")

    def show(self) -> None:
        """Display map in interactive window."""
        plt.show()

    def close(self) -> None:
        """Close the figure."""
        plt.close(self.fig)
