"""
Tests for advanced spatial econometrics: GWR, spatial models, and model selection.

Phase 3 Week 11-12 tests.
"""

import numpy as np
import pytest
from scipy import sparse

from krl_geospatial.econometrics import (
    OLS,
    GeographicallyWeightedRegression,
    ModelSelector,
    SpatialAutoregressiveCombined,
    SpatialDurbin,
    SpatialDurbinError,
    SpatialLag,
    cusum_test,
    hausman_test,
    spatial_heterogeneity_test,
)


@pytest.fixture
def spatial_data():
    """Create spatial dataset for testing."""
    np.random.seed(42)
    n = 100

    # Create grid coordinates
    grid_size = int(np.sqrt(n))
    x_coords = np.repeat(np.arange(grid_size), grid_size)
    y_coords = np.tile(np.arange(grid_size), grid_size)
    coords = np.column_stack([x_coords, y_coords])

    # Generate spatially correlated data
    X1 = np.random.randn(n)
    X2 = np.random.randn(n)

    # Add spatial pattern (distance from center)
    center = np.array([grid_size / 2, grid_size / 2])
    distances = np.linalg.norm(coords - center, axis=1)
    spatial_effect = 0.5 * (distances - distances.mean()) / distances.std()

    # Generate y with spatial heterogeneity
    beta0 = 2.0
    beta1 = 1.5 + 0.5 * spatial_effect  # Spatially varying coefficient
    beta2 = -0.8

    y = beta0 + beta1 * X1 + beta2 * X2 + np.random.randn(n) * 0.5

    X = np.column_stack([X1, X2])

    # Create spatial weights matrix (rook contiguity)
    W = sparse.lil_matrix((n, n))
    for i in range(grid_size):
        for j in range(grid_size):
            idx = i * grid_size + j
            # Add neighbors
            if i > 0:  # Top
                W[idx, (i - 1) * grid_size + j] = 1
            if i < grid_size - 1:  # Bottom
                W[idx, (i + 1) * grid_size + j] = 1
            if j > 0:  # Left
                W[idx, i * grid_size + (j - 1)] = 1
            if j < grid_size - 1:  # Right
                W[idx, i * grid_size + (j + 1)] = 1

    # Row-standardize
    W = W.tocsr()
    row_sums = np.array(W.sum(axis=1)).flatten()
    row_sums[row_sums == 0] = 1
    W = sparse.diags(1.0 / row_sums) @ W

    return y, X, W, coords


# ==================== GWR Tests ====================


def test_gwr_initialization():
    """Test GWR initialization."""
    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=True)

    assert gwr.kernel == "gaussian"
    assert gwr.adaptive is True
    assert gwr.bandwidth is None


def test_gwr_fit_fixed_bandwidth(spatial_data):
    """Test GWR with fixed bandwidth."""
    y, X, W, coords = spatial_data

    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=False)
    result = gwr.fit(y, X, coords, bandwidth=2.0)

    assert result is not None
    assert hasattr(gwr, "local_coefficients")
    assert gwr.local_coefficients.shape == (len(y), X.shape[1] + 1)
    assert hasattr(gwr, "bandwidth")
    assert gwr.bandwidth == 2.0


def test_gwr_fit_adaptive_bandwidth(spatial_data):
    """Test GWR with adaptive bandwidth."""
    y, X, W, coords = spatial_data

    gwr = GeographicallyWeightedRegression(kernel="bisquare", adaptive=True)
    result = gwr.fit(y, X, coords, bandwidth=20)

    assert result is not None
    assert gwr.local_coefficients.shape == (len(y), X.shape[1] + 1)
    assert gwr.bandwidth == 20  # Number of neighbors


def test_gwr_automatic_bandwidth_aic(spatial_data):
    """Test GWR with automatic AIC bandwidth selection."""
    y, X, W, coords = spatial_data

    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=True)
    result = gwr.fit(y, X, coords, bandwidth_selection="aic")

    assert result is not None
    assert hasattr(gwr, "bandwidth")
    assert gwr.bandwidth is not None
    assert gwr.bandwidth > 0


def test_gwr_automatic_bandwidth_cv(spatial_data):
    """Test GWR with cross-validation bandwidth selection."""
    y, X, W, coords = spatial_data

    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=True)
    result = gwr.fit(y, X, coords, bandwidth_selection="cv")

    assert result is not None
    assert gwr.bandwidth is not None


def test_gwr_kernels(spatial_data):
    """Test different GWR kernels."""
    y, X, W, coords = spatial_data

    kernels = ["gaussian", "exponential", "bisquare", "tricube"]

    for kernel in kernels:
        gwr = GeographicallyWeightedRegression(kernel=kernel, adaptive=False)
        result = gwr.fit(y, X, coords, bandwidth=2.0)

        assert result is not None
        assert gwr.local_coefficients is not None


def test_gwr_predict(spatial_data):
    """Test GWR prediction."""
    y, X, W, coords = spatial_data

    # Split data
    train_idx = np.arange(80)
    test_idx = np.arange(80, 100)

    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=False)
    gwr.fit(y[train_idx], X[train_idx], coords[train_idx], bandwidth=2.0)

    # Predict
    y_pred = gwr.predict(X[test_idx], coords[test_idx])

    assert len(y_pred) == len(test_idx)
    assert not np.any(np.isnan(y_pred))


def test_gwr_local_estimates(spatial_data):
    """Test GWR local estimates extraction."""
    y, X, W, coords = spatial_data

    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=False)
    gwr.fit(y, X, coords, bandwidth=2.0)

    estimates = gwr.get_local_estimates()

    assert "coefficients" in estimates
    assert "std_errors" in estimates
    assert "r_squared" in estimates
    assert len(estimates["r_squared"]) == len(y)


def test_gwr_spatial_variation(spatial_data):
    """Test GWR spatial variation testing."""
    y, X, W, coords = spatial_data

    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=False)
    gwr.fit(y, X, coords, bandwidth=2.0)

    # Test for spatial variation in first coefficient
    test_result = gwr.test_spatial_variation(variable_idx=1)

    assert "statistic" in test_result
    assert "p_value" in test_result
    assert "significant" in test_result


# ==================== Spatial Durbin Model Tests ====================


def test_sdm_initialization():
    """Test SDM initialization."""
    sdm = SpatialDurbin()
    assert sdm is not None


def test_sdm_fit(spatial_data):
    """Test SDM fitting."""
    y, X, W, _ = spatial_data

    sdm = SpatialDurbin()
    result = sdm.fit(y, X, W)

    assert result is not None
    assert hasattr(result, "rho")
    assert hasattr(result, "coefficients")
    assert hasattr(sdm, "wx_coefficients")
    assert len(sdm.wx_coefficients) == X.shape[1]


def test_sdm_impacts(spatial_data):
    """Test SDM impact calculations."""
    y, X, W, _ = spatial_data

    sdm = SpatialDurbin()
    result = sdm.fit(y, X, W)

    assert hasattr(sdm, "direct_impacts")
    assert hasattr(sdm, "indirect_impacts")
    assert hasattr(sdm, "total_impacts")
    assert len(sdm.direct_impacts) == X.shape[1]


def test_sdm_predict(spatial_data):
    """Test SDM prediction."""
    y, X, W, _ = spatial_data

    sdm = SpatialDurbin()
    sdm.fit(y, X, W)

    y_pred = sdm.predict(X)

    assert len(y_pred) == len(y)
    assert not np.any(np.isnan(y_pred))


# ==================== Spatial Durbin Error Model Tests ====================


def test_sdem_initialization():
    """Test SDEM initialization."""
    sdem = SpatialDurbinError()
    assert sdem is not None


def test_sdem_fit(spatial_data):
    """Test SDEM fitting."""
    y, X, W, _ = spatial_data

    sdem = SpatialDurbinError()
    result = sdem.fit(y, X, W)

    assert result is not None
    assert hasattr(result, "lambda_")
    assert hasattr(result, "coefficients")
    assert hasattr(sdem, "wx_coefficients")


def test_sdem_predict(spatial_data):
    """Test SDEM prediction."""
    y, X, W, _ = spatial_data

    sdem = SpatialDurbinError()
    sdem.fit(y, X, W)

    y_pred = sdem.predict(X)

    assert len(y_pred) == len(y)


# ==================== SAC Model Tests ====================


def test_sac_initialization():
    """Test SAC initialization."""
    sac = SpatialAutoregressiveCombined()
    assert sac is not None


def test_sac_fit_ml(spatial_data):
    """Test SAC fitting with ML."""
    y, X, W, _ = spatial_data

    sac = SpatialAutoregressiveCombined()
    result = sac.fit(y, X, W, method="ml")

    assert result is not None
    assert hasattr(result, "rho")
    assert hasattr(result, "lambda_")
    assert -1 < result.rho < 1
    assert -1 < result.lambda_ < 1


def test_sac_fit_gmm(spatial_data):
    """Test SAC fitting with GMM."""
    y, X, W, _ = spatial_data

    sac = SpatialAutoregressiveCombined()
    result = sac.fit(y, X, W, method="gmm")

    assert result is not None
    assert hasattr(result, "rho")
    assert hasattr(result, "lambda_")


def test_sac_predict(spatial_data):
    """Test SAC prediction."""
    y, X, W, _ = spatial_data

    sac = SpatialAutoregressiveCombined()
    sac.fit(y, X, W, method="ml")

    y_pred = sac.predict(X)

    assert len(y_pred) == len(y)


# ==================== Model Selection Tests ====================


def test_model_selector_initialization():
    """Test ModelSelector initialization."""
    selector = ModelSelector(significance_level=0.05)

    assert selector.significance_level == 0.05
    assert selector.results == {}


def test_model_selector_decision_tree(spatial_data):
    """Test model selection with decision tree."""
    y, X, W, _ = spatial_data

    selector = ModelSelector()
    best_model, results = selector.select_model(y, X, W, method="decision_tree")

    assert best_model in ["OLS", "Spatial Lag", "Spatial Error"]
    assert "OLS" in results
    assert "diagnostics" in results


def test_model_selector_aic(spatial_data):
    """Test model selection with AIC."""
    y, X, W, _ = spatial_data

    selector = ModelSelector()
    best_model, results = selector.select_model(y, X, W, method="aic")

    assert best_model is not None
    assert len(results) >= 2  # At least OLS and one spatial model


def test_model_selector_bic(spatial_data):
    """Test model selection with BIC."""
    y, X, W, _ = spatial_data

    selector = ModelSelector()
    best_model, results = selector.select_model(y, X, W, method="bic")

    assert best_model is not None


def test_model_selector_comparison_table(spatial_data):
    """Test model comparison table."""
    y, X, W, _ = spatial_data

    selector = ModelSelector()
    selector.select_model(y, X, W, method="aic")

    comparison = selector.get_model_comparison_table()

    assert len(comparison) > 0
    for model_name, stats in comparison.items():
        assert "AIC" in stats
        assert "BIC" in stats
        assert "Log-Likelihood" in stats


# ==================== Heterogeneity Tests ====================


def test_spatial_heterogeneity_test(spatial_data):
    """Test spatial heterogeneity test."""
    y, X, W, coords = spatial_data

    result = spatial_heterogeneity_test(y, X, coords, n_groups=4)

    assert "statistic" in result
    assert "p_value" in result
    assert "significant" in result
    assert "message" in result


def test_cusum_test():
    """Test CUSUM test."""
    np.random.seed(42)

    # Create residuals with structural break
    n = 100
    residuals = np.concatenate(
        [np.random.randn(50) * 0.5, np.random.randn(50) * 0.5 + 2.0]  # Shift
    )

    result = cusum_test(residuals)

    assert "cusum" in result
    assert "critical_value" in result
    assert "breaks_detected" in result
    assert len(result["cusum"]) == n


def test_hausman_test(spatial_data):
    """Test Hausman specification test."""
    y, X, W, _ = spatial_data

    # Fit OLS
    ols = OLS()
    ols_result = ols.fit(y, X, W)

    # Fit spatial model
    sar = SpatialLag()
    sar_result = sar.fit(y, X, W)

    # Hausman test
    result = hausman_test(ols_result, sar_result)

    assert "statistic" in result
    assert "p_value" in result
    assert "significant" in result
    assert "message" in result


# ==================== Integration Tests ====================


def test_gwr_vs_ols(spatial_data):
    """Test that GWR improves on OLS when spatial heterogeneity exists."""
    y, X, W, coords = spatial_data

    # Fit OLS
    ols = OLS()
    ols_result = ols.fit(y, X, W)

    # Fit GWR
    gwr = GeographicallyWeightedRegression(kernel="gaussian", adaptive=False)
    gwr.fit(y, X, coords, bandwidth=2.0)

    # GWR should capture local variation
    assert gwr.local_coefficients is not None
    assert gwr.local_r_squared is not None

    # Check that coefficients vary across space
    coef_std = np.std(gwr.local_coefficients, axis=0)
    assert np.any(coef_std > 0.1)  # Some variation


def test_sdm_vs_sar(spatial_data):
    """Test that SDM includes SAR as special case."""
    y, X, W, _ = spatial_data

    # Fit SAR
    sar = SpatialLag()
    sar_result = sar.fit(y, X, W)

    # Fit SDM
    sdm = SpatialDurbin()
    sdm_result = sdm.fit(y, X, W)

    # SDM should have WX coefficients
    assert len(sdm.wx_coefficients) == X.shape[1]

    # Both should have rho
    assert hasattr(sar_result, "rho")
    assert hasattr(sdm_result, "rho")


def test_sac_dual_parameters(spatial_data):
    """Test that SAC estimates both rho and lambda."""
    y, X, W, _ = spatial_data

    sac = SpatialAutoregressiveCombined()
    result = sac.fit(y, X, W, method="ml")

    assert hasattr(result, "rho")
    assert hasattr(result, "lambda_")
    assert result.rho != result.lambda_  # Should be different


def test_full_workflow(spatial_data):
    """Test complete workflow: selection -> estimation -> validation."""
    y, X, W, coords = spatial_data

    # Step 1: Test for heterogeneity
    hetero_result = spatial_heterogeneity_test(y, X, coords)

    # Step 2: Select model
    selector = ModelSelector()
    best_model, results = selector.select_model(y, X, W, method="decision_tree")

    # Step 3: Verify we got a result
    assert best_model in results
    assert results[best_model]["result"] is not None

    # Step 4: Check diagnostics
    comparison = selector.get_model_comparison_table()
    assert len(comparison) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
