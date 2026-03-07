from .base_model import BaseModel
from .linear_regression import LinearRegressionModel
from .svr_model import SVRModel
from .random_forest import RandomForestModel
from .xgboost_model import XGBoostModel
from .lightgbm_model import LightGBMModel
from .cnn_1d import CNN1DModel

ALL_MODELS: dict[str, type[BaseModel]] = {
    "linear_regression": LinearRegressionModel,
    "svr": SVRModel,
    "random_forest": RandomForestModel,
    "xgboost": XGBoostModel,
    "lightgbm": LightGBMModel,
    "cnn_1d": CNN1DModel,
}

__all__ = [
    "BaseModel", "LinearRegressionModel", "SVRModel", "RandomForestModel",
    "XGBoostModel", "LightGBMModel", "CNN1DModel", "ALL_MODELS",
]
