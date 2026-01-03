"""Tests for spatial interpolation methods."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from krl_geospatial.interpolation import (
    IDW,
    OrdinaryKriging,
    RegularizedSpline,
    ThinPlateSpline,
    UniversalKriging,
)


@pytest.fixture
def training_data():
    """Create training data with spatial trend."""
    np.random.seed(42)

    x = np.linspace(0, 10, 20)
    y = np.linspace(0, 10, 20)
    X, Y = np.meshgrid(x, y)

    x_flat = X.ravel()
    y_flat = Y.ravel()

    # Linear trend + noise
    values = 10 + 0.5 * x_flat + 0.3 * y_flat + np.random.normal(0, 0.5, len(x_flat))

    geometry = [Point(xi, yi) for xi, yi in zip(x_flat, y_flat)]
    gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

    return gdf


@pytest.fixture
def test_data():
    """Create test locations."""
    x_test = np.linspace(0, 10, 10)
    y_test = np.linspace(0, 10, 10)
    X, Y = np.meshgrid(x_test, y_test)

    x_flat = X.ravel()
    y_flat = Y.ravel()

    geometry = [Point(xi, yi) for xi, yi in zip(x_flat, y_flat)]
    gdf = gpd.GeoDataFrame(geometry=geometry)

    return gdf


class TestOrdinaryKriging:
    """Tests for ordinary kriging."""

    def test_init_default(self):
        """Test default initialization."""
        ok = OrdinaryKriging()
        assert ok.variogram_model == "spherical"
        assert ok.variogram_parameters is None

    def test_init_with_model(self):
        """Test initialization with specific model."""
        ok = OrdinaryKriging(variogram_model="exponential")
        assert ok.variogram_model == "exponential"

    def test_fit(self, training_data):
        """Test fitting kriging model."""
        ok = OrdinaryKriging()
        ok.fit(training_data, "value")

        assert ok.X_train_ is not None
        assert ok.y_train_ is not None
        assert ok.variogram_params_ is not None
        assert "sill" in ok.variogram_params_
        assert "range" in ok.variogram_params_

    def test_predict(self, training_data, test_data):
        """Test prediction."""
        ok = OrdinaryKriging()
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert len(predictions) == len(test_data)
        assert not np.isnan(predictions).any()

    def test_predict_with_variance(self, training_data, test_data):
        """Test prediction with variance."""
        ok = OrdinaryKriging()
        ok.fit(training_data, "value")
        predictions, variances = ok.predict(test_data, return_variance=True)

        assert len(predictions) == len(test_data)
        assert len(variances) == len(test_data)
        assert all(variances >= 0)

    def test_spherical_variogram(self, training_data, test_data):
        """Test spherical variogram model."""
        ok = OrdinaryKriging(variogram_model="spherical")
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_exponential_variogram(self, training_data, test_data):
        """Test exponential variogram model."""
        ok = OrdinaryKriging(variogram_model="exponential")
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_gaussian_variogram(self, training_data, test_data):
        """Test gaussian variogram model."""
        ok = OrdinaryKriging(variogram_model="gaussian")
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_linear_variogram(self, training_data, test_data):
        """Test linear variogram model."""
        ok = OrdinaryKriging(variogram_model="linear")
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_n_closest(self, training_data, test_data):
        """Test using n_closest neighbors."""
        ok = OrdinaryKriging(n_closest=10)
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_custom_variogram_params(self, training_data, test_data):
        """Test with custom variogram parameters."""
        params = {"sill": 1.0, "range": 5.0, "nugget": 0.1}
        ok = OrdinaryKriging(variogram_parameters=params)
        ok.fit(training_data, "value")
        predictions = ok.predict(test_data)

        assert ok.variogram_params_ == params
        assert len(predictions) == len(test_data)

    def test_exact_interpolation(self, training_data):
        """Test exact interpolation at training points."""
        ok = OrdinaryKriging()
        ok.fit(training_data, "value")

        # Predict at training locations
        predictions = ok.predict(training_data.head(5))
        actual = training_data.head(5)["value"].values

        # Should be very close to actual values
        np.testing.assert_allclose(predictions, actual, rtol=0.1)


class TestUniversalKriging:
    """Tests for universal kriging."""

    def test_init_default(self):
        """Test default initialization."""
        uk = UniversalKriging()
        assert uk.trend == "linear"

    def test_init_quadratic(self):
        """Test initialization with quadratic trend."""
        uk = UniversalKriging(trend="quadratic")
        assert uk.trend == "quadratic"

    def test_fit_linear(self, training_data):
        """Test fitting with linear trend."""
        uk = UniversalKriging(trend="linear")
        uk.fit(training_data, "value")

        assert hasattr(uk, "_trend_params")
        assert uk.X_train_ is not None

    def test_fit_quadratic(self, training_data):
        """Test fitting with quadratic trend."""
        uk = UniversalKriging(trend="quadratic")
        uk.fit(training_data, "value")

        assert hasattr(uk, "_trend_params")

    def test_predict(self, training_data, test_data):
        """Test prediction with trend."""
        uk = UniversalKriging()
        uk.fit(training_data, "value")
        predictions = uk.predict(test_data)

        assert len(predictions) == len(test_data)
        assert not np.isnan(predictions).any()

    def test_detrending(self, training_data):
        """Test that detrending works."""
        uk = UniversalKriging()
        uk.fit(training_data, "value")

        # Residuals should have lower variance than original
        residual_var = np.var(uk.y_train_)
        original_var = np.var(training_data["value"])

        assert residual_var <= original_var


class TestIDW:
    """Tests for inverse distance weighting."""

    def test_init_default(self):
        """Test default initialization."""
        idw = IDW()
        assert idw.power == 2.0
        assert idw.radius is None

    def test_init_with_params(self):
        """Test initialization with parameters."""
        idw = IDW(power=3.0, radius=5.0, n_closest=10)
        assert idw.power == 3.0
        assert idw.radius == 5.0
        assert idw.n_closest == 10

    def test_fit(self, training_data):
        """Test fitting."""
        idw = IDW()
        idw.fit(training_data, "value")

        assert idw.X_train_ is not None
        assert idw.y_train_ is not None

    def test_predict(self, training_data, test_data):
        """Test prediction."""
        idw = IDW()
        idw.fit(training_data, "value")
        predictions = idw.predict(test_data)

        assert len(predictions) == len(test_data)
        assert not np.isnan(predictions).any()

    def test_power_parameter(self, training_data, test_data):
        """Test different power parameters."""
        idw1 = IDW(power=1.0)
        idw1.fit(training_data, "value")
        pred1 = idw1.predict(test_data)

        idw2 = IDW(power=3.0)
        idw2.fit(training_data, "value")
        pred2 = idw2.predict(test_data)

        # Different powers should give different results
        assert not np.allclose(pred1, pred2)

    def test_radius_filter(self, training_data, test_data):
        """Test radius filtering."""
        idw = IDW(radius=2.0)
        idw.fit(training_data, "value")
        predictions = idw.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_n_closest(self, training_data, test_data):
        """Test n_closest parameter."""
        idw = IDW(n_closest=5)
        idw.fit(training_data, "value")
        predictions = idw.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_exact_at_training(self, training_data):
        """Test exact interpolation at training points."""
        idw = IDW()
        idw.fit(training_data, "value")

        # Predict at training locations
        predictions = idw.predict(training_data.head(5))
        actual = training_data.head(5)["value"].values

        # Should be exact at training points
        np.testing.assert_allclose(predictions, actual, rtol=1e-5)

    def test_anisotropy(self, training_data, test_data):
        """Test anisotropic distance."""
        idw = IDW(anisotropy_angle=45, anisotropy_ratio=2.0)
        idw.fit(training_data, "value")
        predictions = idw.predict(test_data)

        assert len(predictions) == len(test_data)

    def test_cross_validate(self, training_data):
        """Test cross-validation."""
        idw = IDW()
        rmse, mae, predictions = idw.cross_validate(training_data, "value")

        assert rmse > 0
        assert mae > 0
        assert len(predictions) == len(training_data)


class TestThinPlateSpline:
    """Tests for thin plate spline."""

    def test_init_default(self):
        """Test default initialization."""
        tps = ThinPlateSpline()
        assert tps.smoothing == 0.0

    def test_init_with_smoothing(self):
        """Test initialization with smoothing."""
        tps = ThinPlateSpline(smoothing=0.1)
        assert tps.smoothing == 0.1

    def test_fit(self, training_data):
        """Test fitting."""
        tps = ThinPlateSpline()
        tps.fit(training_data, "value")

        assert tps.X_train_ is not None
        assert tps.weights_ is not None

    def test_predict(self, training_data, test_data):
        """Test prediction."""
        tps = ThinPlateSpline()
        tps.fit(training_data, "value")
        predictions = tps.predict(test_data)

        assert len(predictions) == len(test_data)
        assert not np.isnan(predictions).any()

    def test_exact_interpolation(self, training_data):
        """Test exact interpolation with no smoothing."""
        tps = ThinPlateSpline(smoothing=0.0)
        tps.fit(training_data, "value")

        # Predict at training locations
        predictions = tps.predict(training_data.head(10))
        actual = training_data.head(10)["value"].values

        # Should be very close with no smoothing
        np.testing.assert_allclose(predictions, actual, rtol=0.01)

    def test_smoothing_effect(self, training_data):
        """Test that smoothing reduces exactness."""
        # Exact interpolation
        tps0 = ThinPlateSpline(smoothing=0.0)
        tps0.fit(training_data, "value")
        pred0 = tps0.predict(training_data.head(5))

        # Smoothed interpolation
        tps1 = ThinPlateSpline(smoothing=1.0)
        tps1.fit(training_data, "value")
        pred1 = tps1.predict(training_data.head(5))

        actual = training_data.head(5)["value"].values

        # Smoothed should have larger errors
        err0 = np.abs(pred0 - actual).mean()
        err1 = np.abs(pred1 - actual).mean()

        assert err1 >= err0


class TestRegularizedSpline:
    """Tests for regularized spline."""

    def test_init_default(self):
        """Test default initialization."""
        rs = RegularizedSpline()
        assert rs.tension == 0.0
        assert rs.smoothing == 0.0

    def test_init_with_params(self):
        """Test initialization with parameters."""
        rs = RegularizedSpline(tension=0.5, smoothing=0.1)
        assert rs.tension == 0.5
        assert rs.smoothing == 0.1

    def test_fit(self, training_data):
        """Test fitting."""
        rs = RegularizedSpline()
        rs.fit(training_data, "value")

        assert rs.X_train_ is not None
        assert rs.weights_ is not None

    def test_predict(self, training_data, test_data):
        """Test prediction."""
        rs = RegularizedSpline()
        rs.fit(training_data, "value")
        predictions = rs.predict(test_data)

        assert len(predictions) == len(test_data)
        assert not np.isnan(predictions).any()

    def test_tension_effect(self, training_data, test_data):
        """Test effect of tension parameter."""
        # No tension
        rs0 = RegularizedSpline(tension=0.0)
        rs0.fit(training_data, "value")
        pred0 = rs0.predict(test_data)

        # High tension
        rs1 = RegularizedSpline(tension=2.0)
        rs1.fit(training_data, "value")
        pred1 = rs1.predict(test_data)

        # Should give different results
        assert not np.allclose(pred0, pred1)

    def test_combined_tension_smoothing(self, training_data, test_data):
        """Test combining tension and smoothing."""
        rs = RegularizedSpline(tension=0.5, smoothing=0.1)
        rs.fit(training_data, "value")
        predictions = rs.predict(test_data)

        assert len(predictions) == len(test_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
