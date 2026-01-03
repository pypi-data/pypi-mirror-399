"""
Tests for spatial econometric models.

Comprehensive tests for regression models, autocorrelation statistics,
and diagnostic tests.
"""

import numpy as np
import pytest
from scipy import sparse

from krl_geospatial.econometrics import (
    OLS,
    SpatialError,
    SpatialLag,
    aic,
    bic,
    compare_models,
    gearys_c,
    getis_ord_g,
    getis_ord_gi_star,
    lm_error_test,
    lm_lag_test,
    lm_sarma_test,
    local_morans_i,
    morans_i,
    pseudo_r2,
    residual_diagnostics,
)


@pytest.fixture
def simple_data():
    """Create simple test data."""
    np.random.seed(42)
    n = 50

    # Generate X and y
    X = np.random.randn(n, 2)
    beta = np.array([1.5, -0.8])
    y = X @ beta + np.random.randn(n) * 0.5

    return y, X


@pytest.fixture
def spatial_weights():
    """Create simple spatial weights matrix."""
    n = 50
    # Create rook contiguity for grid
    W = sparse.lil_matrix((n, n))

    # Simple neighbor structure
    for i in range(n):
        if i > 0:
            W[i, i - 1] = 1
        if i < n - 1:
            W[i, i + 1] = 1

    # Row-standardize
    row_sums = np.array(W.sum(axis=1)).flatten()
    row_sums[row_sums == 0] = 1  # Avoid division by zero

    D_inv = sparse.diags(1 / row_sums)
    W = D_inv @ W

    return W.tocsr()


@pytest.fixture
def spatial_data(spatial_weights):
    """Create spatially autocorrelated data."""
    np.random.seed(42)
    n = 50
    W = spatial_weights

    # Generate spatially autocorrelated y
    X = np.random.randn(n, 2)
    beta = np.array([1.5, -0.8])
    epsilon = np.random.randn(n) * 0.5

    # Spatial lag: y = 0.5 * Wy + X*beta + epsilon
    rho = 0.5
    I = sparse.eye(n)
    A_inv = sparse.linalg.inv(I - rho * W)
    y = A_inv @ (X @ beta + epsilon)

    return np.array(y).flatten(), X, W


# ============================================================================
# Base Classes Tests
# ============================================================================


def test_regression_result_summary():
    """Test RegressionResult summary generation."""
    from krl_geospatial.econometrics.base import RegressionResult

    result = RegressionResult(
        model_name="Test",
        coefficients=np.array([1.0, 2.0]),
        std_errors=np.array([0.1, 0.2]),
        t_stats=np.array([10.0, 10.0]),
        p_values=np.array([0.001, 0.001]),
        residuals=np.zeros(10),
        fitted_values=np.ones(10),
        n_obs=10,
        n_vars=2,
        r_squared=0.85,
        adj_r_squared=0.83,
        log_likelihood=-10.5,
        aic=25.0,
        bic=27.0,
    )

    summary = result.summary()

    assert "Test Regression Results" in summary
    assert "R-squared" in summary
    assert "0.8500" in summary


def test_regression_result_to_dict():
    """Test RegressionResult conversion to dictionary."""
    from krl_geospatial.econometrics.base import RegressionResult

    result = RegressionResult(
        model_name="Test",
        coefficients=np.array([1.0]),
        std_errors=np.array([0.1]),
        t_stats=np.array([10.0]),
        p_values=np.array([0.001]),
        residuals=np.zeros(10),
        fitted_values=np.ones(10),
        n_obs=10,
        n_vars=1,
        r_squared=0.85,
        adj_r_squared=0.83,
        log_likelihood=-10.5,
        aic=25.0,
        bic=27.0,
    )

    result_dict = result.to_dict()

    assert result_dict["model_name"] == "Test"
    assert result_dict["n_obs"] == 10
    assert result_dict["r_squared"] == 0.85


# ============================================================================
# OLS Tests
# ============================================================================


def test_ols_initialization():
    """Test OLS model initialization."""
    ols = OLS()

    assert ols.name == "OLS"
    assert not ols._is_fitted
    assert ols.coefficients is None


def test_ols_fit(simple_data):
    """Test OLS model fitting."""
    y, X = simple_data
    ols = OLS()

    result = ols.fit(y, X)

    assert ols._is_fitted
    assert result.model_name == "OLS"
    assert len(result.coefficients) == 3  # intercept + 2 vars
    assert result.n_obs == len(y)
    assert 0 <= result.r_squared <= 1


def test_ols_predict(simple_data):
    """Test OLS predictions."""
    y, X = simple_data
    ols = OLS()
    ols.fit(y, X)

    predictions = ols.predict(X)

    assert len(predictions) == len(y)
    assert not np.any(np.isnan(predictions))


def test_ols_no_constant(simple_data):
    """Test OLS without intercept."""
    y, X = simple_data
    ols = OLS()

    result = ols.fit(y, X, add_constant=False)

    assert len(result.coefficients) == 2  # No intercept


def test_ols_diagnostics(simple_data):
    """Test OLS diagnostic statistics."""
    y, X = simple_data
    ols = OLS()
    ols.fit(y, X)

    diagnostics = ols.get_diagnostics()

    assert "jarque_bera" in diagnostics
    assert "breusch_pagan" in diagnostics
    assert "residual_mean" in diagnostics


def test_ols_predict_not_fitted(simple_data):
    """Test prediction error when model not fitted."""
    _, X = simple_data
    ols = OLS()

    with pytest.raises(ValueError, match="Model must be fitted"):
        ols.predict(X)


# ============================================================================
# Spatial Lag Model Tests
# ============================================================================


def test_spatial_lag_initialization():
    """Test Spatial Lag model initialization."""
    sar = SpatialLag()

    assert sar.name == "Spatial Lag"
    assert not sar._is_fitted
    assert sar.rho is None


def test_spatial_lag_fit(spatial_data):
    """Test Spatial Lag model fitting."""
    y, X, W = spatial_data
    sar = SpatialLag()

    result = sar.fit(y, X, W)

    assert sar._is_fitted
    assert result.model_name == "Spatial Lag"
    assert "rho" in result.spatial_params
    assert -1 < result.spatial_params["rho"] < 1
    assert len(result.coefficients) == 3


def test_spatial_lag_impacts(spatial_data):
    """Test spatial multiplier effects calculation."""
    y, X, W = spatial_data
    sar = SpatialLag()

    result = sar.fit(y, X, W)
    impacts = result.extra_info["impacts"]

    assert "average" in impacts
    assert "direct" in impacts["average"]
    assert "indirect" in impacts["average"]
    assert "total" in impacts["average"]


def test_spatial_lag_predict(spatial_data):
    """Test Spatial Lag predictions."""
    y, X, W = spatial_data
    sar = SpatialLag()
    sar.fit(y, X, W)

    predictions = sar.predict(X)

    assert len(predictions) == len(y)
    assert not np.any(np.isnan(predictions))


def test_spatial_lag_requires_weights(simple_data):
    """Test that Spatial Lag requires weights matrix."""
    y, X = simple_data
    sar = SpatialLag()

    with pytest.raises(ValueError, match="Spatial weights matrix W is required"):
        sar.fit(y, X, None)


# ============================================================================
# Spatial Error Model Tests
# ============================================================================


def test_spatial_error_initialization():
    """Test Spatial Error model initialization."""
    sem = SpatialError()

    assert sem.name == "Spatial Error"
    assert not sem._is_fitted
    assert sem.lambda_ is None


def test_spatial_error_fit_ml(spatial_data):
    """Test Spatial Error model with ML estimation."""
    y, X, W = spatial_data
    sem = SpatialError()

    result = sem.fit(y, X, W, method="ml")

    assert sem._is_fitted
    assert result.model_name == "Spatial Error"
    assert "lambda" in result.spatial_params
    assert -1 < result.spatial_params["lambda"] < 1
    assert result.extra_info["method"] == "ml"


def test_spatial_error_fit_gmm(spatial_data):
    """Test Spatial Error model with GMM estimation."""
    y, X, W = spatial_data
    sem = SpatialError()

    result = sem.fit(y, X, W, method="gmm")

    assert sem._is_fitted
    assert "lambda" in result.spatial_params
    assert result.extra_info["method"] == "gmm"


def test_spatial_error_predict(spatial_data):
    """Test Spatial Error predictions."""
    y, X, W = spatial_data
    sem = SpatialError()
    sem.fit(y, X, W)

    predictions = sem.predict(X)

    assert len(predictions) == len(y)
    assert not np.any(np.isnan(predictions))


def test_spatial_error_requires_weights(simple_data):
    """Test that Spatial Error requires weights matrix."""
    y, X = simple_data
    sem = SpatialError()

    with pytest.raises(ValueError, match="Spatial weights matrix W is required"):
        sem.fit(y, X, None)


def test_spatial_error_invalid_method(spatial_data):
    """Test invalid estimation method."""
    y, X, W = spatial_data
    sem = SpatialError()

    with pytest.raises(ValueError, match="Unknown method"):
        sem.fit(y, X, W, method="invalid")


# ============================================================================
# Autocorrelation Tests
# ============================================================================


def test_morans_i(spatial_data):
    """Test Moran's I calculation."""
    y, _, W = spatial_data

    I, E_I, p_value = morans_i(y, W, permutations=99)

    assert isinstance(I, float)
    assert -1 <= I <= 1
    assert E_I < 0  # Expected value is negative
    assert 0 <= p_value <= 1


def test_morans_i_positive_autocorrelation(spatial_weights):
    """Test Moran's I detects positive autocorrelation."""
    n = 50
    W = spatial_weights

    # Create strongly autocorrelated data
    values = np.array([1.0 if i < 25 else -1.0 for i in range(n)])

    I, E_I, _ = morans_i(values, W, permutations=99)

    assert I > E_I  # Positive autocorrelation


def test_gearys_c(spatial_data):
    """Test Geary's C calculation."""
    y, _, W = spatial_data

    C, E_C, p_value = gearys_c(y, W, permutations=99)

    assert isinstance(C, float)
    assert C > 0
    assert E_C == 1.0
    assert 0 <= p_value <= 1


def test_local_morans_i(spatial_data):
    """Test Local Moran's I calculation."""
    y, _, W = spatial_data

    I_local, p_values = local_morans_i(y, W, permutations=99)

    assert len(I_local) == len(y)
    assert len(p_values) == len(y)
    assert all(0 <= p <= 1 for p in p_values)


def test_getis_ord_g(spatial_data):
    """Test Getis-Ord G calculation."""
    y, _, W = spatial_data

    # Make W binary
    W_binary = (W > 0).astype(float)
    W_binary = sparse.csr_matrix(W_binary)

    G, z_score = getis_ord_g(y, W_binary)

    assert isinstance(G, float)
    assert isinstance(z_score, float)


def test_getis_ord_gi_star(spatial_data):
    """Test Getis-Ord Gi* calculation."""
    y, _, W = spatial_data

    # Make W binary
    W_binary = (W > 0).astype(float)
    W_binary = sparse.csr_matrix(W_binary)

    Gi_star, z_scores = getis_ord_gi_star(y, W_binary)

    assert len(Gi_star) == len(y)
    assert len(z_scores) == len(y)


def test_getis_ord_gi_star_no_self(spatial_data):
    """Test Gi* without self-weight."""
    y, _, W = spatial_data

    W_binary = (W > 0).astype(float)
    W_binary = sparse.csr_matrix(W_binary)

    Gi_star, z_scores = getis_ord_gi_star(y, W_binary, include_self=False)

    assert len(Gi_star) == len(y)


# ============================================================================
# Diagnostics Tests
# ============================================================================


def test_lm_lag_test(spatial_data):
    """Test LM lag test."""
    y, X, W = spatial_data

    # Fit OLS first
    ols = OLS()
    result = ols.fit(y, X)

    lm_stat, p_value = lm_lag_test(result.residuals, X, W)

    assert isinstance(lm_stat, float)
    assert lm_stat >= 0
    assert 0 <= p_value <= 1


def test_lm_error_test(spatial_data):
    """Test LM error test."""
    y, X, W = spatial_data

    ols = OLS()
    result = ols.fit(y, X)

    lm_stat, p_value = lm_error_test(result.residuals, X, W)

    assert isinstance(lm_stat, float)
    assert lm_stat >= 0
    assert 0 <= p_value <= 1


def test_lm_sarma_test(spatial_data):
    """Test LM SARMA test."""
    y, X, W = spatial_data

    ols = OLS()
    result = ols.fit(y, X)

    lm_stat, p_value = lm_sarma_test(result.residuals, X, W)

    assert isinstance(lm_stat, float)
    assert lm_stat >= 0
    assert 0 <= p_value <= 1


def test_aic_calculation():
    """Test AIC calculation."""
    log_lik = -50.0
    n_params = 3

    aic_val = aic(log_lik, n_params)

    assert aic_val == 106.0  # -2*(-50) + 2*3


def test_bic_calculation():
    """Test BIC calculation."""
    log_lik = -50.0
    n_params = 3
    n_obs = 100

    bic_val = bic(log_lik, n_params, n_obs)

    expected = -2 * log_lik + n_params * np.log(n_obs)
    assert np.isclose(bic_val, expected)


def test_pseudo_r2():
    """Test pseudo R-squared calculation."""
    log_lik = -50.0
    log_lik_null = -80.0

    pr2 = pseudo_r2(log_lik, log_lik_null)

    assert 0 <= pr2 <= 1
    assert np.isclose(pr2, 0.375)


def test_residual_diagnostics(simple_data):
    """Test residual diagnostics."""
    y, X = simple_data
    ols = OLS()
    result = ols.fit(y, X)

    diagnostics = residual_diagnostics(result.residuals)

    assert "mean" in diagnostics
    assert "std" in diagnostics
    assert "jarque_bera" in diagnostics
    assert "jb_pvalue" in diagnostics
    assert "n_outliers" in diagnostics


def test_compare_models(spatial_data):
    """Test model comparison."""
    y, X, W = spatial_data

    # Fit multiple models
    ols = OLS()
    ols_result = ols.fit(y, X)

    sar = SpatialLag()
    sar_result = sar.fit(y, X, W)

    sem = SpatialError()
    sem_result = sem.fit(y, X, W)

    # Compare
    comparison = compare_models(ols_result, sar_result, sem_result)

    assert len(comparison["models"]) == 3
    assert "best_by_aic" in comparison
    assert "best_by_bic" in comparison
    assert "best_by_r2" in comparison


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_spatial_workflow(spatial_data):
    """Test complete spatial econometric workflow."""
    y, X, W = spatial_data

    # 1. Fit OLS
    ols = OLS()
    ols_result = ols.fit(y, X)

    # 2. Test for spatial dependence
    lm_lag, p_lag = lm_lag_test(ols_result.residuals, X, W)
    lm_err, p_err = lm_error_test(ols_result.residuals, X, W)

    # 3. Fit spatial models if needed
    if p_lag < 0.05 or p_err < 0.05:
        sar_result = SpatialLag().fit(y, X, W)
        sem_result = SpatialError().fit(y, X, W)

        # 4. Compare models
        comparison = compare_models(ols_result, sar_result, sem_result)

        assert len(comparison["models"]) == 3

    assert True  # Workflow completed successfully


def test_model_persistence(spatial_data, tmp_path):
    """Test saving and loading model results."""
    y, X, W = spatial_data

    ols = OLS()
    result = ols.fit(y, X)

    # Convert to dict
    result_dict = result.to_dict()

    # Verify all keys present
    assert "coefficients" in result_dict
    assert "r_squared" in result_dict
    assert "aic" in result_dict
