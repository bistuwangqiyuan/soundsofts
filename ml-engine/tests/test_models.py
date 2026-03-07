"""Tests for all 6 regression models."""

import numpy as np
import pytest

from src.models import LinearRegressionModel, SVRModel, RandomForestModel, XGBoostModel, LightGBMModel
from src.utils.metrics import compute_metrics


@pytest.fixture
def regression_data():
    np.random.seed(42)
    X = np.random.randn(200, 5).astype(np.float32)
    y = (2.0 * X[:, 0] + X[:, 1] + np.random.randn(200) * 0.1).astype(np.float32)
    return X[:150], y[:150], X[150:], y[150:]


class TestLinearRegression:
    def test_train_predict(self, regression_data):
        X_train, y_train, X_test, y_test = regression_data
        model = LinearRegressionModel()
        model.train(X_train, y_train)
        preds = model.predict(X_test)
        assert preds.shape == y_test.shape


class TestRandomForest:
    def test_mape_reasonable(self, regression_data):
        X_train, y_train, X_test, y_test = regression_data
        model = RandomForestModel(n_estimators=50)
        model.train(X_train, y_train)
        metrics = compute_metrics(y_test, model.predict(X_test))
        assert metrics["MAPE"] < 50

    def test_feature_importances(self, regression_data):
        X_train, y_train, _, _ = regression_data
        model = RandomForestModel(n_estimators=50)
        model.train(X_train, y_train)
        fi = model.feature_importances()
        assert len(fi) == X_train.shape[1]


class TestXGBoost:
    def test_train_predict(self, regression_data):
        X_train, y_train, X_test, y_test = regression_data
        model = XGBoostModel(n_estimators=50)
        model.train(X_train, y_train)
        assert model.predict(X_test).shape == y_test.shape


class TestLightGBM:
    def test_train_predict(self, regression_data):
        X_train, y_train, X_test, y_test = regression_data
        model = LightGBMModel(n_estimators=50)
        model.train(X_train, y_train)
        assert model.predict(X_test).shape == y_test.shape


class TestSVR:
    def test_train_predict(self, regression_data):
        X_train, y_train, X_test, y_test = regression_data
        model = SVRModel()
        model.train(X_train, y_train)
        assert model.predict(X_test).shape == y_test.shape


class TestMetrics:
    def test_perfect_prediction(self):
        y = np.array([1.0, 2.0, 3.0])
        m = compute_metrics(y, y)
        assert m["MAE"] == 0.0
        assert m["MAPE"] == 0.0
        assert m["R2"] == 1.0
