"""
Tests for the mapping module.

Tests interactive maps, choropleth visualizations, and color utilities.
"""

import os
import tempfile

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, Polygon

from krl_geospatial.mapping import (
    ChoroplethMap,
    ColorScheme,
    InteractiveMap,
    classify_values,
    get_color_scheme,
)


@pytest.fixture
def point_gdf():
    """Create a GeoDataFrame with point geometries."""
    np.random.seed(42)
    n = 20

    data = {
        "geometry": [
            Point(x, y)
            for x, y in zip(np.random.uniform(-122, -121, n), np.random.uniform(37, 38, n))
        ],
        "value": np.random.rand(n) * 100,
        "category": np.random.choice(["A", "B", "C"], n),
        "name": [f"Point {i}" for i in range(n)],
    }

    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def polygon_gdf():
    """Create a GeoDataFrame with polygon geometries."""
    np.random.seed(42)

    # Create grid of polygons
    polygons = []
    values = []
    names = []

    for i in range(4):
        for j in range(4):
            x0, y0 = -122 + i * 0.2, 37 + j * 0.2
            poly = Polygon([(x0, y0), (x0 + 0.18, y0), (x0 + 0.18, y0 + 0.18), (x0, y0 + 0.18)])
            polygons.append(poly)
            values.append(np.random.rand() * 100)
            names.append(f"Region {i}-{j}")

    data = {"geometry": polygons, "value": values, "name": names}

    return gpd.GeoDataFrame(data, crs="EPSG:4326")


class TestColorScheme:
    """Test color scheme utilities."""

    def test_color_scheme_enum(self):
        """Test ColorScheme enum values."""
        assert ColorScheme.BLUES.value == "Blues"
        assert ColorScheme.VIRIDIS.value == "viridis"
        assert ColorScheme.RDYLGN.value == "RdYlGn"
        assert ColorScheme.SET1.value == "Set1"

    def test_get_color_scheme(self):
        """Test getting colors from scheme."""
        colors = get_color_scheme("Blues", n_colors=5)

        assert len(colors) == 5
        assert all(c.startswith("#") for c in colors)
        assert all(len(c) == 7 for c in colors)

    def test_get_color_scheme_enum(self):
        """Test using ColorScheme enum."""
        colors = get_color_scheme(ColorScheme.REDS, n_colors=3)

        assert len(colors) == 3

    def test_get_color_scheme_reverse(self):
        """Test reversing color order."""
        colors_normal = get_color_scheme("Blues", n_colors=5)
        colors_reversed = get_color_scheme("Blues", n_colors=5, reverse=True)

        assert colors_normal[0] == colors_reversed[-1]
        assert colors_normal[-1] == colors_reversed[0]

    def test_get_color_scheme_invalid(self):
        """Test invalid scheme falls back to Blues."""
        colors = get_color_scheme("InvalidScheme", n_colors=5)

        assert len(colors) == 5
        # Should return Blues as fallback


class TestClassifyValues:
    """Test data classification utilities."""

    def test_classify_quantiles(self):
        """Test quantile classification."""
        values = np.arange(100, dtype=float)
        bins, edges = classify_values(values, method="quantiles", k=5)

        assert len(bins) == 100
        assert len(edges) == 5
        assert bins.min() == 0
        assert bins.max() == 4

    def test_classify_equal_interval(self):
        """Test equal interval classification."""
        values = np.arange(100, dtype=float)
        bins, edges = classify_values(values, method="equal_interval", k=4)

        assert len(bins) == 100
        assert len(edges) == 4

    def test_classify_with_nan(self):
        """Test classification with NaN values."""
        values = np.arange(100, dtype=float)
        values[::10] = np.nan  # Every 10th value is NaN

        bins, edges = classify_values(values, method="quantiles", k=5)

        assert len(bins) == 100
        assert np.sum(bins == -1) == 10  # NaN values get -1

    def test_classify_natural_breaks(self):
        """Test natural breaks classification."""
        # Create data with natural clusters
        values = np.concatenate(
            [np.random.normal(10, 1, 30), np.random.normal(50, 2, 30), np.random.normal(90, 1, 30)]
        )

        bins, edges = classify_values(values, method="natural_breaks", k=3)

        assert len(bins) == 90
        assert len(edges) == 3


class TestInteractiveMap:
    """Test InteractiveMap class."""

    def test_init_default(self):
        """Test map initialization with defaults."""
        m = InteractiveMap()

        assert m.map is not None
        assert hasattr(m, "location")
        assert hasattr(m, "zoom_start")

    def test_init_custom_location(self):
        """Test map with custom location."""
        m = InteractiveMap(location=[37.7749, -122.4194], zoom_start=10)

        assert m.location == [37.7749, -122.4194]
        assert m.zoom_start == 10

    def test_add_markers(self, point_gdf):
        """Test adding markers."""
        m = InteractiveMap()
        m.add_markers(point_gdf, popup_columns=["name", "value"])

        # Map should have markers
        assert m.map is not None

    def test_add_markers_with_clustering(self, point_gdf):
        """Test adding markers with clustering."""
        m = InteractiveMap()
        m.add_markers(point_gdf, cluster=True)

        assert m.map is not None

    def test_add_polygons(self, polygon_gdf):
        """Test adding polygons."""
        m = InteractiveMap()
        m.add_polygons(polygon_gdf, popup_columns=["name"])

        assert m.map is not None

    def test_add_polygons_with_style(self, polygon_gdf):
        """Test adding polygons with custom style."""
        m = InteractiveMap()
        style = {"fillColor": "blue", "fillOpacity": 0.5}
        m.add_polygons(polygon_gdf, style=style)

        assert m.map is not None

    def test_add_heatmap(self, point_gdf):
        """Test adding heatmap."""
        m = InteractiveMap()
        m.add_heatmap(point_gdf, intensity_column="value")

        assert m.map is not None

    def test_add_tile_layer(self):
        """Test adding tile layer."""
        m = InteractiveMap()
        m.add_tile_layer("CartoDB positron", "CartoDB")

        assert m.map is not None

    def test_add_layer_control(self, point_gdf):
        """Test adding layer control."""
        m = InteractiveMap()
        m.add_markers(point_gdf)
        m.add_layer_control()

        assert m.map is not None

    def test_fit_bounds(self, point_gdf):
        """Test fitting map to data bounds."""
        m = InteractiveMap()
        m.fit_bounds(point_gdf)

        assert m.map is not None

    def test_save(self, point_gdf):
        """Test saving map to HTML."""
        m = InteractiveMap()
        m.add_markers(point_gdf)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_map.html")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

    def test_repr_html(self):
        """Test HTML representation."""
        m = InteractiveMap()
        html = m._repr_html_()

        assert html is not None
        assert isinstance(html, str)


class TestChoroplethMap:
    """Test ChoroplethMap class."""

    def test_init_default(self, polygon_gdf):
        """Test choropleth initialization."""
        m = ChoroplethMap(polygon_gdf, column="value")

        assert m.gdf is not None
        assert m.column == "value"
        assert m.map is not None
        assert hasattr(m, "bin_indices")
        assert hasattr(m, "bin_edges")
        assert hasattr(m, "colors")

    def test_init_custom_scheme(self, polygon_gdf):
        """Test with custom classification scheme."""
        m = ChoroplethMap(polygon_gdf, column="value", scheme="equal_interval", k=4)

        assert m.scheme == "equal_interval"
        assert m.k == 4
        assert len(m.colors) == 4

    def test_init_custom_cmap(self, polygon_gdf):
        """Test with custom color scheme."""
        m = ChoroplethMap(polygon_gdf, column="value", cmap="Reds", k=5)

        assert len(m.colors) == 5

    def test_init_invalid_column(self, polygon_gdf):
        """Test with invalid column raises error."""
        with pytest.raises(ValueError, match="Column 'invalid' not found"):
            ChoroplethMap(polygon_gdf, column="invalid")

    def test_classification_info(self, polygon_gdf):
        """Test getting classification info."""
        m = ChoroplethMap(polygon_gdf, column="value", k=5)
        info = m.get_classification_info()

        assert "scheme" in info
        assert "k" in info
        assert "bin_edges" in info
        assert "colors" in info
        assert "counts" in info

        assert info["k"] == 5
        assert len(info["bin_edges"]) == 5
        assert len(info["colors"]) == 5
        assert len(info["counts"]) == 5
        assert sum(info["counts"]) == len(polygon_gdf)

    def test_add_tile_layer(self, polygon_gdf):
        """Test adding tile layer to choropleth."""
        m = ChoroplethMap(polygon_gdf, column="value")
        m.add_tile_layer("CartoDB positron", "CartoDB")

        assert m.map is not None

    def test_add_layer_control(self, polygon_gdf):
        """Test adding layer control."""
        m = ChoroplethMap(polygon_gdf, column="value")
        m.add_layer_control()

        assert m.map is not None

    def test_fit_bounds(self, polygon_gdf):
        """Test fitting to bounds."""
        m = ChoroplethMap(polygon_gdf, column="value")
        m.fit_bounds()

        assert m.map is not None

    def test_save(self, polygon_gdf):
        """Test saving choropleth to HTML."""
        m = ChoroplethMap(polygon_gdf, column="value")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_choropleth.html")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

    def test_repr_html(self, polygon_gdf):
        """Test HTML representation."""
        m = ChoroplethMap(polygon_gdf, column="value")
        html = m._repr_html_()

        assert html is not None
        assert isinstance(html, str)

    def test_with_nan_values(self, polygon_gdf):
        """Test choropleth with NaN values."""
        polygon_gdf_copy = polygon_gdf.copy()
        polygon_gdf_copy.loc[::2, "value"] = np.nan

        m = ChoroplethMap(polygon_gdf_copy, column="value", k=3)

        assert m.map is not None
        assert -1 in m.bin_indices  # NaN values get -1

    def test_reverse_colors(self, polygon_gdf):
        """Test reversing color order."""
        m1 = ChoroplethMap(polygon_gdf, column="value", cmap="Blues", k=5)
        m2 = ChoroplethMap(polygon_gdf, column="value", cmap="Blues", k=5, reverse_colors=True)

        assert m1.colors[0] == m2.colors[-1]
        assert m1.colors[-1] == m2.colors[0]

    def test_custom_legend_title(self, polygon_gdf):
        """Test custom legend title."""
        m = ChoroplethMap(polygon_gdf, column="value", legend_title="Custom Title")

        assert m.map is not None

    def test_no_legend(self, polygon_gdf):
        """Test choropleth without legend."""
        m = ChoroplethMap(polygon_gdf, column="value", legend=False)

        assert m.map is not None


def test_integration_multiple_layers(point_gdf, polygon_gdf):
    """Test adding multiple layers to same map."""
    m = InteractiveMap(location=[37.5, -121.5], zoom_start=9)

    # Add polygons
    m.add_polygons(polygon_gdf, popup_columns=["name"])

    # Add markers
    m.add_markers(point_gdf, popup_columns=["name", "value"])

    # Add heatmap
    m.add_heatmap(point_gdf, intensity_column="value")

    # Add controls
    m.add_layer_control()

    assert m.map is not None


def test_integration_save_load_cycle(polygon_gdf):
    """Test creating, saving, and verifying map file."""
    m = ChoroplethMap(polygon_gdf, column="value", scheme="quantiles", k=4, cmap="YlOrRd")

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_map.html")
        m.save(filepath)

        # Verify file exists and has content
        assert os.path.exists(filepath)

        with open(filepath, "r") as f:
            content = f.read()
            assert "folium" in content.lower()
            assert len(content) > 1000  # Should be substantial HTML
