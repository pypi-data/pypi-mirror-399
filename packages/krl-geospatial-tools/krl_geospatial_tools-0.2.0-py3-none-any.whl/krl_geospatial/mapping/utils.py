"""
Visualization utilities for color schemes, legends, and scales.

This module provides color schemes and classification methods for
choropleth maps and other visualizations.
"""

from enum import Enum
from typing import List, Optional, Tuple, Union

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from mapclassify import classify

logger = get_logger(__name__)


class ColorScheme(str, Enum):
    """
    Predefined color schemes for choropleth maps.

    Includes sequential, diverging, and qualitative schemes
    from ColorBrewer and matplotlib.
    """

    # Sequential (single hue)
    BLUES = "Blues"
    GREENS = "Greens"
    REDS = "Reds"
    ORANGES = "Oranges"
    PURPLES = "Purples"
    GREYS = "Greys"

    # Sequential (multi-hue)
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"

    # Diverging
    RDYLGN = "RdYlGn"
    RDBU = "RdBu"
    BRBG = "BrBG"
    PIYG = "PiYG"
    PRGN = "PRGn"
    RDGY = "RdGy"
    SPECTRAL = "Spectral"

    # Qualitative
    SET1 = "Set1"
    SET2 = "Set2"
    SET3 = "Set3"
    PAIRED = "Paired"
    ACCENT = "Accent"


def get_color_scheme(
    scheme: Union[str, ColorScheme], n_colors: int = 5, reverse: bool = False
) -> List[str]:
    """
    Get a list of hex colors from a color scheme.

    Args:
        scheme: Color scheme name (ColorScheme enum or string)
        n_colors: Number of colors to return
        reverse: If True, reverse the color order

    Returns:
        List of hex color strings

    Example:
        ```python
        from krl_geospatial.mapping import get_color_scheme

        # Get 5 blues
        colors = get_color_scheme('Blues', n_colors=5)

        # Get reversed reds
        colors = get_color_scheme('Reds', n_colors=7, reverse=True)
        ```
    """
    if isinstance(scheme, ColorScheme):
        scheme = scheme.value

    try:
        # Get colormap
        cmap = plt.get_cmap(scheme)

        # Sample colors
        indices = np.linspace(0, 1, n_colors)
        if reverse:
            indices = indices[::-1]

        colors = [mcolors.rgb2hex(cmap(i)) for i in indices]

        logger.debug(f"Generated {n_colors} colors from scheme '{scheme}'")
        return colors

    except Exception as e:
        logger.error(f"Failed to get color scheme '{scheme}': {e}")
        # Fallback to blues
        return get_color_scheme("Blues", n_colors=n_colors, reverse=reverse)


def classify_values(
    values: np.ndarray, method: str = "quantiles", k: int = 5
) -> Tuple[np.ndarray, List[float]]:
    """
    Classify values into bins for choropleth mapping.

    Args:
        values: Array of values to classify
        method: Classification method:
            - 'quantiles': Equal counts in each bin
            - 'equal_interval': Equal-width bins
            - 'natural_breaks': Jenks natural breaks
            - 'std_mean': Standard deviation around mean
            - 'fisher_jenks': Fisher-Jenks algorithm
        k: Number of classes

    Returns:
        Tuple of (bin_indices, bin_edges)
        - bin_indices: Array of bin assignments (0 to k-1)
        - bin_edges: List of bin edge values

    Example:
        ```python
        import numpy as np
        from krl_geospatial.mapping.utils import classify_values

        values = np.random.rand(100)
        bins, edges = classify_values(values, method='quantiles', k=5)
        ```
    """
    # Remove NaN values
    valid_mask = ~np.isnan(values)
    valid_values = values[valid_mask]

    if len(valid_values) == 0:
        logger.warning("No valid values to classify")
        return np.zeros_like(values, dtype=int), []

    # Map method names to mapclassify
    method_map = {
        "quantiles": "Quantiles",
        "equal_interval": "EqualInterval",
        "natural_breaks": "NaturalBreaks",
        "std_mean": "StdMean",
        "fisher_jenks": "FisherJenks",
    }

    if method not in method_map:
        logger.warning(f"Unknown method '{method}', using 'quantiles'")
        method = "quantiles"

    try:
        # Use mapclassify
        classifier = classify(valid_values, scheme=method_map[method], k=k)

        # Get bin edges
        bin_edges = classifier.bins.tolist()

        # Assign bins to all values (including NaN)
        bin_indices = np.full(len(values), -1, dtype=int)

        # Use searchsorted to find bins for valid values
        valid_bins = np.searchsorted(bin_edges, valid_values, side="right")
        valid_bins = np.clip(valid_bins, 0, k - 1)

        bin_indices[valid_mask] = valid_bins

        logger.info(f"Classified {len(valid_values)} values into {k} bins using '{method}'")

        return bin_indices, bin_edges

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        # Fallback to simple quantiles
        percentiles = np.linspace(0, 100, k + 1)[1:]
        bin_edges = np.percentile(valid_values, percentiles).tolist()
        valid_bins = np.searchsorted(bin_edges, valid_values)
        valid_bins = np.clip(valid_bins, 0, k - 1)

        bin_indices = np.full(len(values), -1, dtype=int)
        bin_indices[valid_mask] = valid_bins

        return bin_indices, bin_edges


def create_legend_html(
    bin_edges: List[float], colors: List[str], title: str = "Legend", format_string: str = "{:.2f}"
) -> str:
    """
    Create HTML for a map legend.

    Args:
        bin_edges: List of bin edge values
        colors: List of colors (hex strings)
        title: Legend title
        format_string: Format string for values

    Returns:
        HTML string for legend
    """
    html = f'<div style="background-color: white; padding: 10px; border: 2px solid gray;">'
    html += f'<h4 style="margin: 0 0 10px 0;">{title}</h4>'

    # Add color boxes with labels
    prev_edge = None
    for i, (edge, color) in enumerate(zip(bin_edges, colors)):
        if prev_edge is None:
            label = f"≤ {format_string.format(edge)}"
        else:
            label = f"{format_string.format(prev_edge)} - {format_string.format(edge)}"

        html += f'<div style="margin: 5px 0;">'
        html += f'<span style="display: inline-block; width: 20px; height: 20px; '
        html += f'background-color: {color}; border: 1px solid black; margin-right: 5px;"></span>'
        html += f"<span>{label}</span>"
        html += f"</div>"

        prev_edge = edge

    html += "</div>"

    return html


def value_to_color(
    value: float, bin_edges: List[float], colors: List[str], nan_color: str = "#808080"
) -> str:
    """
    Map a value to a color based on bins.

    Args:
        value: Value to map
        bin_edges: List of bin edge values
        colors: List of colors (hex strings)
        nan_color: Color for NaN/missing values

    Returns:
        Hex color string
    """
    if np.isnan(value):
        return nan_color

    bin_idx = np.searchsorted(bin_edges, value, side="right")
    bin_idx = min(bin_idx, len(colors) - 1)

    return colors[bin_idx]
