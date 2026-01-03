# train_model.py

import argparse
import os
from pathlib import Path
import sys
from typing import List, Dict

import joblib
import numpy as np
import pandas as pd

# Assuming these components are in the specified library structure
from ImportanceScore.data_loader import MODEL_CONFIG_SCHEMA, CLASSIFICATION_SCHEMA, DataLoader
from ImportanceScore.features import FeaturePreprocessor
from ImportanceScore.model import (ImportanceModel, get_model, get_model_type)
from YMLEditor.yaml_reader import ConfigLoader  # Using a generic YAML loader


def train(
        category: str,
        model_name: str,
        config: Dict,
        wlm_config: Dict,
        file_paths: Dict[str, Path],
) -> (Dict, Dict):
    """
    Trains a model using pre-loaded configurations and explicit file paths.

    Args:
        category: The category of the model (e.g., 'peaks', 'poi').
        model_name: Name of the model architecture to use (e.g., 'WLM', 'LGBMRegressor').
        config: The parsed model configuration dictionary.
        wlm_config: The parsed classification/weights configuration dictionary.
        file_paths: A dictionary of all required file paths.

    Returns:
        A tuple containing:
        - A dictionary of evaluation results from the model.
        - A dictionary of adaptive thresholds for quality metrics.
    """
    model_type = get_model_type(model_name)
    preprocessor = FeaturePreprocessor(config, category, model_name)

    if model_type == "rule_based":
        # Weighted Linear Model (WLM) requires a classification config for weights.
        df = pd.read_csv(file_paths["features_path"])
        y = None
        labeled_mask = np.ones(len(df), dtype=bool)
        X, _, _ = preprocessor.transform(df, training=False)

        model = get_model(model_name, config=config, weights=wlm_config)
        mdl = ImportanceModel(X, y, labeled_mask, model, model_name, original_df=df)
    else:
        # Scikit-learn Regressor or Classifier.
        print("➡️ Loading and merging features and targets...")
        loader = DataLoader(config)
        df = loader.load_and_merge_data(
            file_paths["features_path"], file_paths["targets_path"]
        )

        X, y, labeled_mask = preprocessor.transform(df, training=True)
        num_labeled_samples = labeled_mask.sum()
        min_samples_for_split = 8

        if num_labeled_samples < min_samples_for_split:
            print("\n   ❌ Error: Not enough training data to proceed.")
            print(f"      - Found only {num_labeled_samples} labeled samples.")
            print(f"      - A minimum of {min_samples_for_split} is required.")
            print("\n      **ACTION REQUIRED:** Ensure target and feature files can be joined.")
            sys.exit(1)

        print(f"  ✅ Found {num_labeled_samples} labeled samples for training.")
        warn_unused_one_hot_columns(X, labeled_mask, preprocessor.one_hot_column_names)

        print("➡️ Training supervised model...")
        model = get_model(model_name, config=config)
        mdl = ImportanceModel(X, y, labeled_mask, model, model_name, original_df=df)

    # Use the explicit output path for saving the model
    results = mdl.evaluate(save_path=file_paths["output_path"])
    thresholds = compute_adaptive_thresholds(y[labeled_mask]) if y is not None else None
    return results, thresholds


def compute_adaptive_thresholds(y_true: pd.Series) -> dict:
    """Computes evaluation metric thresholds based on the range of target values."""
    if not y_true.any():
        return None
    y_range = y_true.max() - y_true.min()
    return {
        "r2": [0.90, 0.75, 0.50],
        "mse": [0.01, 0.04, 0.10] if y_range <= 1 else [0.01*y_range**2, 0.04*y_range**2, 0.10*y_range**2],
        "mae": [0.05, 0.15, 0.30] if y_range <= 1 else [0.04*y_range, 0.12*y_range, 0.25*y_range],
    }


def quality_indicator(metric: str, value: float, thresholds: dict) -> tuple[str, str]:
    """Returns an emoji and label based on the metric's value against thresholds."""
    if not thresholds:
        return " ", " "
    quality_levels = [("🟢", "Excellent"), ("🔵", "Good"), ("⚪", "OK"), ("⚠️", "Low")]
    limits = thresholds.get(metric)
    if not limits:
        return " ", " "
    # For R-squared, higher is better
    if metric == "r2":
        if value >= limits[0]: return quality_levels[0]
        if value >= limits[1]: return quality_levels[1]
        if value >= limits[2]: return quality_levels[2]
        return quality_levels[3]
    # For error metrics, lower is better
    else:
        if value <= limits[0]: return quality_levels[0]
        if value <= limits[1]: return quality_levels[1]
        if value <= limits[2]: return quality_levels[2]
        return quality_levels[3]


def display_results(results: Dict, thresholds: Dict):
    """Prints a formatted summary of the model evaluation results."""
    print("\n*️⃣ Evaluation Results:")
    model_name = list(results.keys())[0]
    res = results[model_name]

    if not res:
        print("  No evaluation results were generated.")
        return

    print(f"\n  Model: {model_name}")
    for name in ["MSE", "MAE", "R2", "ACCURACY"]:
        key = name.lower()
        if key in res:
            val = res[key]
            emoji, label = quality_indicator(key, val, thresholds)
            print(f"   {name:<8}: {val:>8.3f}  - {emoji} {label}")

    if "report" in res:
        for label, metrics in res["report"].items():
            if label.isdigit():
                print(
                    f"     Class {label}: P={metrics['precision']:.2f}, "
                    f"R={metrics['recall']:.2f}, F1={metrics['f1-score']:.2f}"
                )
    print()


def warn_unused_one_hot_columns(
        X: pd.DataFrame, labeled_mask: pd.Series, one_hot_column_names: List[str]
) -> None:
    """Warns if any one-hot encoded columns have no training samples."""
    if not one_hot_column_names:
        return
    training_data = X.loc[labeled_mask, one_hot_column_names]
    unused_columns = training_data.columns[training_data.sum() == 0].tolist()
    if unused_columns:
        print("⚠️ Warning: The following one-hot encoded columns had no training samples:")
        for col in unused_columns:
            print(f"   ⛔ {col}")


def main():
    """Orchestrates the model training process."""
    parser = argparse.ArgumentParser(
        description="Train an importance model with explicit file paths."
    )
    parser.add_argument("--features", type=Path, required=True, help="Path to features CSV file.")
    parser.add_argument("--targets", type=Path, help="Path to targets CSV file (required for non-WLM models).")
    parser.add_argument("--config", type=Path, required=True, help="Path to model config YAML.")
    parser.add_argument("--wlm-config", type=Path, help="Path to WLM YAML config.")
    parser.add_argument("--output", type=Path, required=True, help="Path to save the trained model file.")
    parser.add_argument("--category", type=str, required=True, help="Category name (e.g., 'poi').")
    parser.add_argument("--log-level", type=int, default=4, help="Set log level.")
    args = parser.parse_args()

    file_paths = {
        "features_path": args.features,
        "targets_path": args.targets,
        "model_config_path": args.config,
        "wlm_config_path": args.wlm_config,
        "output_path": args.output,
    }

    print("\n🔷Training Configuration")
    for name, path in file_paths.items():
        if path: # Only print paths that were provided
            path.parent.mkdir(parents=True, exist_ok=True)
            if name != "output_path":
                status = "✅" if path.exists() else "❌ (Not Found!)"
            else:
                status = ""
            print(f"  - {name:<18}: {path} {status}")
    print()

    try:
        print(f"Loading model config: {file_paths["model_config_path"]}")
        loader = ConfigLoader(MODEL_CONFIG_SCHEMA)
        model_config = loader.read(file_paths["model_config_path"])
        model_name = model_config.get("model")
        if not model_name:
            raise ValueError("'model' key not found in model config.")

        class_config = {}

        if get_model_type(model_name) == "rule_based":
            # ---  the "training" for WLM is simply to copy pre-configured weights into the model ---
            print(f"➡️ Building rule-based model: {model_name}")
            if not file_paths["wlm_config_path"]:
                raise ValueError("--wlm-config is required for WLM models.")
            file_paths["targets_path"].parent.mkdir(parents=True, exist_ok=True)
            file_paths["targets_path"].touch()

            print(f"   - Loading WLM weights from: {file_paths['wlm_config_path']}")
            loader = ConfigLoader(CLASSIFICATION_SCHEMA)
            class_config = loader.read(file_paths["wlm_config_path"])

            # Instantiate the model directly from the configs
            model = get_model(model_name, config=model_config, weights=class_config)

            save_path = file_paths["output_path"]
            print(f"   - Saving model")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(model, save_path)
            print(f"✅ Model saved to {save_path}")

            print("✅ WLM train complete.")
            # We are done, exit.
            sys.exit(0)

    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)

    print(f"➡️ Training with model: {model_name}")
    if get_model_type(model_name) == "rule_based":
        print("   (WLM training just validates data)")

    all_results = {}
    result, thresholds = train(
        args.category, model_name, model_config, class_config, file_paths
    )
    all_results[model_name] = result

    display_results(all_results, thresholds)
    print("Done")


if __name__ == "__main__":
    main()