import os
from pathlib import Path
import sys

import joblib
from joblib import dump
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, \
    RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (mean_squared_error, mean_absolute_error, r2_score, confusion_matrix,
                             ConfusionMatrixDisplay, )
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.svm import SVC, SVR

from ImportanceScore.weighted_linear_model import WeightedLinearModel


class ImportanceModel:
    def __init__(self, X, y, labeled_mask, model, model_name, original_df):
        self.X = X
        self.y = y
        self.labeled_mask = labeled_mask
        self.model = model
        self.model_name = model_name
        self.original_df = original_df
        self.is_classifier = hasattr(model, "predict_proba") or hasattr(model, "classes_")
        # Extract feature names from DataFrame
        self.feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else [f"f{i}" for i
                                                                                     in range(
                X.shape[1]
            )]

    def evaluate(self, save_path=None, display_plots=True):
        """
        Evaluate the model. For supervised models, run train/test split and scoring.
        For rule-based models, just generate predictions and return summary stats.

        Args:
            save_path (str or Path, optional): Path to save the trained model.
            display_plots (bool): Whether to display/save feature importance plots.

        Returns:
            dict: Evaluation metrics including MSE, MAE, and R2.
        """
        if self.y is None:
            # Rule-based model; only return predictions
            y_pred = self.model.predict(self.X)
            result = {
                "rule_based": True, "predictions": y_pred.tolist(), "num_items": len(y_pred),
            }
            if save_path:
                dump(self.model, save_path)
                if getattr(self.model, "verbose", False):
                    print(f"💾 Rule-based model saved to: {save_path}")
            return result

        # Supervised training
        X_train, X_test, y_train, y_test = self._train_test_split()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        # Calculate standard metrics
        results = {
            "model": self.model_name, "mse": mean_squared_error(y_test, y_pred),
            "mae": mean_absolute_error(y_test, y_pred), "r2": r2_score(y_test, y_pred),
        }

        # Save top N errors to CSV
        try:
            error_df = pd.DataFrame(X_test.copy())
            error_df["target"] = y_test
            error_df["predicted"] = y_pred.round(2)
            error_df["error"] = (y_test - y_pred).abs().round(2)

            # Restore osm_id and item_name using the original DataFrame if available
            if self.original_df is not None:
                meta_cols = ["osm_id", "item_name"]
                meta_df = self.original_df.loc[X_test.index, meta_cols]
                error_df = pd.concat(
                    [meta_df.reset_index(drop=True), error_df.reset_index(drop=True)], axis=1
                )

            top_errors = error_df.sort_values("error", ascending=False).head(30)
            top_errors.to_csv("logs/top_errors.csv", index=False)
            print("📄 Saved top 30 prediction errors to logs/top_errors.csv")
        except Exception as e:
            print(f"⚠️ Failed to save top_errors.csv: {e}")

        # Feature importance output
        if hasattr(self.model, "feature_importances_"):
            print("\n📊 Feature Importance:")
            feature_names = getattr(
                self, "feature_names", [f"f{i}" for i in range(len(self.X.columns))]
            )
            importances = self.model.feature_importances_
            for name, score in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
                print(f"  {name:<20} {score:.3f}")
            print()

            #if display_plots:
            #    self._plot_feature_importance(True, "logs/importance.png")

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(self.model, save_path)
            print(f"✅ Model saved to {save_path}")

        return results

    def predict(self, X_new):
        if not self.model:
            raise RuntimeError("Model has not been trained.")
        return self.model.predict(X_new)

    def _train_test_split(self):
        X_labeled = self.X[self.labeled_mask]
        y_labeled = self.y[self.labeled_mask]

        if self.is_classifier and len(np.unique(y_labeled)) > 1:
            sss = StratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
            train_idx, test_idx = next(sss.split(X_labeled, y_labeled))
            return (X_labeled.iloc[train_idx], X_labeled.iloc[test_idx], y_labeled.iloc[train_idx],
                    y_labeled.iloc[test_idx],)
        else:
            return train_test_split(X_labeled, y_labeled, test_size=0.25, random_state=42)

    def _plot_confusion_matrix(self, y_true, y_pred):
        cm = confusion_matrix(y_true, y_pred)
        ConfusionMatrixDisplay(cm).plot()
        plt.title(f"{self.model_name} Confusion Matrix")
        plt.show()

    def _plot_feature_importance(self, show: bool = False, output_path: str = None):
        importances = self.model.feature_importances_
        sorted_idx = np.argsort(importances)

        plt.figure(figsize=(10, 6))
        plt.barh(self.X.columns[sorted_idx], importances[sorted_idx])
        plt.title(f"{self.model_name} Feature Importances")

        if output_path:
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
        elif show:
            plt.show()
        else:
            plt.close()


# The registry  stores the class constructor, not a pre-built instance.
# This decouples the registry from the specific instantiation requirements of each model.
MODEL_REGISTRY = {
    "RF": {
        "class": RandomForestClassifier,
        "params": {"n_estimators": 100, "random_state": 42, "class_weight": "balanced"},
        "task": "classification",
    }, "GBT": {
        "class": GradientBoostingClassifier, "params": {"random_state": 42},
        "task": "classification",
    }, "LOGR": {
        "class": LogisticRegression, "params": {"max_iter": 500, "class_weight": "balanced"},
        "task": "classification",
    }, "SVM": {
        "class": SVC, "params": {"probability": True, "class_weight": "balanced"},
        "task": "classification",
    }, "RFR": {
        "class": RandomForestRegressor, "params": {"n_estimators": 100, "random_state": 42},
        "task": "regression",
    }, "SVR": {
        "class": SVR, "params": {}, "task": "regression",
    }, "LR": {
        "class": LinearRegression, "params": {}, "task": "regression",
    }, "WLM": {
        "class": WeightedLinearModel,  # Store the class itself
        "params": {},  # WLM parameters are provided dynamically
        "task": "rule_based",
    }, "GBR": {
        "class": GradientBoostingRegressor,
        "params": {"n_estimators": 200, "learning_rate": 0.05, "max_depth": 4, "random_state": 42},
        "task": "regression",
    },
}


def get_model_choices(task_type: str = "all"):
    if task_type not in {"classification", "regression", "all"}:
        raise ValueError("task_type must be one of 'classification', 'regression', or 'all'.")

    return [name for name, meta in MODEL_REGISTRY.items() if
            task_type == "all" or meta["task"] == task_type]


def get_model(model_name: str, config: dict = None, weights: dict = None):
    """
    Acts as a factory to construct and return a model instance.
    It correctly injects all necessary parameters from the configuration files.
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Invalid model '{model_name}'. Choose from: {get_model_choices('all')}")

    model_info = MODEL_REGISTRY[model_name]
    model_class = model_info["class"]
    model_instance = None

    try:
        if model_name == "WLM":
            config = config or {}
            weights = weights or {}

            base_score_column = config.get('base_score_column')
            feature_weights = weights.get('features')

            # Read the 'intercept' from the model config, defaulting to 0.0.
            intercept_value = config.get('intercept', 0.0)

            model_instance = model_class(
                feature_coefficients=feature_weights,  # Renamed for clarity
                base_score_column=base_score_column, intercept=intercept_value,
                # Pass the intercept here
                max_contribution=config.get("max_contribution"), verbose=config.get("verbose", True)
            )
        else:
            default_params = model_info.get("params", {})
            model_instance = model_class(**default_params)

        # Consistently attach the metadata to the instance after creation.
        setattr(model_instance, 'model_name', model_name)

        # Add version number
        model_version = getattr(model_class, '__version__', '0.0')  # Default for sklearn models
        setattr(model_instance, 'version', model_version)
        return model_instance

    except (ValueError, TypeError) as e:
        print(f"   ❌ Error: Failed to initialize model '{model_name}'. {e}")
        sys.exit(1)


def get_model_type(model_name: str):
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Invalid model name '{model_name}'. Choose from: {get_model_choices('all')}"
        )
    return MODEL_REGISTRY[model_name]["task"]


def get_target_column(config, model_name: str):
    model_type = get_model_type(model_name)
    if model_type == "classification":
        return config["classifier_target"]
    else:
        return config["regressor_target"]


def get_model_path(dataset_type: str, model_name: str, training: bool = False):
    model_path = Path("models", f"{dataset_type}_model.joblib")

    if training:
        model_path.parent.mkdir(parents=True, exist_ok=True)

    return model_path
