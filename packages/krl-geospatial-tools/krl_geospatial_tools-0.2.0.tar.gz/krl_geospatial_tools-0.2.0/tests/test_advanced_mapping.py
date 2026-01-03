"""
Tests for advanced mapping features (bubble, flow, heatmap, export, static).

Tests the Phase 2 Week 7-8 implementations.
"""

import os
import tempfile

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

from krl_geospatial.mapping import (
    BubbleMap,
    DensityHeatmap,
    FlowMap,
    GridDensity,
    MapExporter,
    StaticMap,
    export_geodataframe,
    export_to_geojson,
)


@pytest.fixture
def point_gdf():
    """Create a GeoDataFrame with point geometries."""
    np.random.seed(42)
    n = 30

    data = {
        "geometry": [
            Point(x, y)
            for x, y in zip(np.random.uniform(-122, -121, n), np.random.uniform(37, 38, n))
        ],
        "value": np.random.rand(n) * 100,
        "size_val": np.random.rand(n) * 50 + 10,
        "category": np.random.choice(["A", "B", "C"], n),
        "name": [f"Point {i}" for i in range(n)],
    }

    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def line_gdf():
    """Create a GeoDataFrame with line geometries."""
    np.random.seed(42)
    n = 10

    lines = []
    flows = []

    for i in range(n):
        x1, y1 = np.random.uniform(-122, -121), np.random.uniform(37, 38)
        x2, y2 = np.random.uniform(-122, -121), np.random.uniform(37, 38)
        lines.append(LineString([(x1, y1), (x2, y2)]))
        flows.append(np.random.rand() * 100 + 10)

    data = {
        "geometry": lines,
        "flow": flows,
        "origin": [f"City {i}" for i in range(n)],
        "destination": [f"City {i+1}" for i in range(n)],
    }

    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def polygon_gdf():
    """Create a GeoDataFrame with polygon geometries."""
    np.random.seed(42)

    polygons = []
    values = []

    for i in range(3):
        for j in range(3):
            x0, y0 = -122 + i * 0.3, 37 + j * 0.3
            poly = Polygon([(x0, y0), (x0 + 0.25, y0), (x0 + 0.25, y0 + 0.25), (x0, y0 + 0.25)])
            polygons.append(poly)
            values.append(np.random.rand() * 100)

    data = {"geometry": polygons, "value": values, "name": [f"Region {i}" for i in range(9)]}

    return gpd.GeoDataFrame(data, crs="EPSG:4326")


class TestBubbleMap:
    """Test BubbleMap class."""

    def test_init_basic(self, point_gdf):
        """Test basic bubble map initialization."""
        m = BubbleMap(point_gdf, size_column="value")

        assert m.map is not None
        assert m.size_column == "value"
        assert len(m.sizes) == len(point_gdf)

    def test_init_with_color(self, point_gdf):
        """Test bubble map with color column."""
        m = BubbleMap(point_gdf, size_column="value", color_column="size_val", cmap="Reds", k=3)

        assert m.color_column == "size_val"
        assert m.bin_indices is not None
        assert m.bin_edges is not None
        assert len(m.colors) == 3

    def test_size_scaling_linear(self, point_gdf):
        """Test linear size scaling."""
        m = BubbleMap(point_gdf, size_column="value", size_scale="linear")

        assert m.sizes.min() >= m.min_radius
        assert m.sizes.max() <= m.max_radius

    def test_size_scaling_sqrt(self, point_gdf):
        """Test square root size scaling."""
        m = BubbleMap(point_gdf, size_column="value", size_scale="sqrt")

        assert m.sizes.min() >= m.min_radius
        assert m.sizes.max() <= m.max_radius

    def test_size_scaling_log(self, point_gdf):
        """Test logarithmic size scaling."""
        m = BubbleMap(point_gdf, size_column="value", size_scale="log")

        assert m.sizes.min() >= m.min_radius
        assert m.sizes.max() <= m.max_radius

    def test_invalid_size_column(self, point_gdf):
        """Test error with invalid size column."""
        with pytest.raises(ValueError, match="Size column 'invalid' not found"):
            BubbleMap(point_gdf, size_column="invalid")

    def test_invalid_color_column(self, point_gdf):
        """Test error with invalid color column."""
        with pytest.raises(ValueError, match="Color column 'invalid' not found"):
            BubbleMap(point_gdf, size_column="value", color_column="invalid")

    def test_save(self, point_gdf):
        """Test saving bubble map to file."""
        m = BubbleMap(point_gdf, size_column="value")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "bubble_map.html")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

    def test_cluster_mode(self, point_gdf):
        """Test bubble map with clustering."""
        m = BubbleMap(point_gdf, size_column="value", cluster=True)

        assert m.map is not None


class TestFlowMap:
    """Test FlowMap class."""

    def test_init_basic(self, line_gdf):
        """Test basic flow map initialization."""
        m = FlowMap(line_gdf, flow_column="flow")

        assert m.map is not None
        assert m.flow_column == "flow"
        assert len(m.widths) == len(line_gdf)

    def test_width_calculation(self, line_gdf):
        """Test flow width calculation."""
        m = FlowMap(line_gdf, flow_column="flow")

        assert m.widths.min() >= m.min_width
        assert m.widths.max() <= m.max_width

    def test_curved_flows(self, line_gdf):
        """Test curved flow lines."""
        m = FlowMap(line_gdf, flow_column="flow", curve=True, curve_weight=0.3)

        assert m.curve is True
        assert m.curve_weight == 0.3

    def test_with_arrows(self, line_gdf):
        """Test flows with arrows."""
        m = FlowMap(line_gdf, flow_column="flow", arrows=True)

        assert m.arrows is True
        assert m.arrow_size > 0

    def test_color_mapping(self, line_gdf):
        """Test flow map with color mapping."""
        m = FlowMap(line_gdf, flow_column="flow", color_column="origin", cmap="Set1")

        assert m.color_map is not None

    def test_invalid_flow_column(self, line_gdf):
        """Test error with invalid flow column."""
        with pytest.raises(ValueError, match="Flow column 'invalid' not found"):
            FlowMap(line_gdf, flow_column="invalid")

    def test_save(self, line_gdf):
        """Test saving flow map to file."""
        m = FlowMap(line_gdf, flow_column="flow")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "flow_map.html")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0


class TestDensityHeatmap:
    """Test DensityHeatmap class."""

    def test_init_basic(self, point_gdf):
        """Test basic density heatmap initialization."""
        m = DensityHeatmap(point_gdf)

        assert m.map is not None
        assert m.radius == 15
        assert m.blur == 10

    def test_with_intensity(self, point_gdf):
        """Test heatmap with intensity column."""
        m = DensityHeatmap(point_gdf, intensity_column="value")

        assert m.intensity_column == "value"

    def test_custom_params(self, point_gdf):
        """Test heatmap with custom parameters."""
        m = DensityHeatmap(point_gdf, radius=25, blur=15, min_opacity=0.3, max_opacity=0.9)

        assert m.radius == 25
        assert m.blur == 15

    def test_custom_gradient(self, point_gdf):
        """Test heatmap with custom color gradient."""
        gradient = {0.0: "green", 0.5: "yellow", 1.0: "red"}
        m = DensityHeatmap(point_gdf, gradient=gradient)

        assert m.map is not None

    def test_invalid_intensity_column(self, point_gdf):
        """Test error with invalid intensity column."""
        with pytest.raises(ValueError, match="Intensity column 'invalid' not found"):
            DensityHeatmap(point_gdf, intensity_column="invalid")

    def test_save(self, point_gdf):
        """Test saving heatmap to file."""
        m = DensityHeatmap(point_gdf)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "heatmap.html")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0


class TestGridDensity:
    """Test GridDensity class."""

    def test_init_hexagon(self, point_gdf):
        """Test hexagonal grid density."""
        m = GridDensity(point_gdf, cell_size=5000, grid_type="hexagon")

        assert m.map is not None
        assert m.grid_type == "hexagon"
        assert m.grid_gdf is not None
        assert "density" in m.grid_gdf.columns

    def test_init_square(self, point_gdf):
        """Test square grid density."""
        m = GridDensity(point_gdf, cell_size=5000, grid_type="square")

        assert m.grid_type == "square"
        assert m.grid_gdf is not None

    def test_save(self, point_gdf):
        """Test saving grid density map."""
        m = GridDensity(point_gdf, cell_size=5000)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "grid_density.html")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0


class TestMapExporter:
    """Test MapExporter class."""

    def test_init_folium(self):
        """Test initializing with folium map."""
        import folium

        m = folium.Map()
        exporter = MapExporter(m)

        assert exporter.map_type == "folium"

    def test_to_html(self):
        """Test HTML export."""
        import folium

        m = folium.Map()
        exporter = MapExporter(m)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "map.html")
            exporter.to_html(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

    def test_unsupported_map_type(self):
        """Test error with unsupported map type."""
        with pytest.raises(TypeError):
            MapExporter("not a map")


class TestExportFunctions:
    """Test export utility functions."""

    def test_export_geodataframe_geojson(self, point_gdf):
        """Test exporting GeoDataFrame to GeoJSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "data.geojson")
            export_geodataframe(point_gdf, filepath)

            assert os.path.exists(filepath)

            # Read back and verify
            gdf_read = gpd.read_file(filepath)
            assert len(gdf_read) == len(point_gdf)

    def test_export_geodataframe_shapefile(self, point_gdf):
        """Test exporting GeoDataFrame to Shapefile."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "data.shp")
            export_geodataframe(point_gdf, filepath)

            assert os.path.exists(filepath)

    def test_export_to_geojson(self, point_gdf):
        """Test export_to_geojson function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "data.geojson")
            export_to_geojson(point_gdf, filepath)

            assert os.path.exists(filepath)

            # Verify it's valid GeoJSON
            gdf_read = gpd.read_file(filepath)
            assert len(gdf_read) == len(point_gdf)

    def test_export_to_geojson_drop_columns(self, point_gdf):
        """Test exporting with dropped columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "data.geojson")
            export_to_geojson(point_gdf, filepath, drop_columns=["category"])

            gdf_read = gpd.read_file(filepath)
            assert "category" not in gdf_read.columns


class TestStaticMap:
    """Test StaticMap class."""

    def test_init(self):
        """Test static map initialization."""
        m = StaticMap(figsize=(10, 8))

        assert m.fig is not None
        assert m.ax is not None

    def test_add_polygons_simple(self, polygon_gdf):
        """Test adding simple polygons."""
        m = StaticMap()
        m.add_polygons(polygon_gdf)

        assert m.ax is not None

    def test_add_polygons_choropleth(self, polygon_gdf):
        """Test adding choropleth polygons."""
        m = StaticMap()
        m.add_polygons(polygon_gdf, column="value", cmap="Reds", legend=True)

        assert m.ax is not None

    def test_add_points(self, point_gdf):
        """Test adding points."""
        m = StaticMap()
        m.add_points(point_gdf, size=50, color="red")

        assert m.ax is not None

    def test_add_points_with_column(self, point_gdf):
        """Test adding points with color column."""
        m = StaticMap()
        m.add_points(point_gdf, column="value", cmap="viridis", legend=True)

        assert m.ax is not None

    def test_add_lines(self, line_gdf):
        """Test adding lines."""
        m = StaticMap()
        m.add_lines(line_gdf, linewidth=2, color="blue")

        assert m.ax is not None

    def test_set_title(self):
        """Test setting title."""
        m = StaticMap()
        m.set_title("Test Map", fontsize=16)

        assert m.ax.get_title() == "Test Map"

    def test_set_extent(self, polygon_gdf):
        """Test setting extent."""
        m = StaticMap()
        bounds = polygon_gdf.total_bounds
        m.set_extent(bounds)

        xlim = m.ax.get_xlim()
        ylim = m.ax.get_ylim()

        assert xlim[0] == bounds[0]
        assert xlim[1] == bounds[2]
        assert ylim[0] == bounds[1]
        assert ylim[1] == bounds[3]

    def test_save_png(self, polygon_gdf):
        """Test saving to PNG."""
        m = StaticMap()
        m.add_polygons(polygon_gdf, column="value", cmap="Blues")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "map.png")
            m.save(filepath, dpi=100)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

        m.close()

    def test_save_svg(self, polygon_gdf):
        """Test saving to SVG."""
        m = StaticMap()
        m.add_polygons(polygon_gdf)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "map.svg")
            m.save(filepath)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

        m.close()

    def test_save_pdf(self, polygon_gdf):
        """Test saving to PDF."""
        m = StaticMap()
        m.add_polygons(polygon_gdf)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "map.pdf")
            m.save(filepath, dpi=300)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

        m.close()


def test_integration_bubble_export(point_gdf):
    """Test creating and exporting bubble map."""
    m = BubbleMap(point_gdf, size_column="value", color_column="size_val", cmap="YlOrRd")

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "bubble_export.html")
        m.save(filepath)

        assert os.path.exists(filepath)

        # Test exporting with MapExporter
        exporter = MapExporter(m.map)
        html_path = os.path.join(tmpdir, "bubble_exported.html")
        exporter.to_html(html_path)

        assert os.path.exists(html_path)


def test_integration_static_multi_layer(point_gdf, polygon_gdf):
    """Test static map with multiple layers."""
    m = StaticMap(figsize=(12, 10))

    # Add polygons
    m.add_polygons(polygon_gdf, column="value", cmap="Blues", alpha=0.5)

    # Add points
    m.add_points(point_gdf, size="size_val", color="red", alpha=0.7)

    # Set title
    m.set_title("Multi-layer Static Map")

    # Set extent
    m.set_extent(polygon_gdf.total_bounds)

    # Save
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "multi_layer.png")
        m.save(filepath)

        assert os.path.exists(filepath)

    m.close()
