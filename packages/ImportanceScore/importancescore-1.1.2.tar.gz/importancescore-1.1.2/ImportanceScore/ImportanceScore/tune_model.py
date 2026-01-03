# tune_model.py
"""
This script uses Optuna to perform hyperparameter tuning for a given model.

It systematically searches for the best combination of model parameters
by running multiple training trials and evaluating them with cross-validation.
The final output is the set of best parameters found.
"""

import argparse
import sys

import optuna
from sklearn.model_selection import cross_val_score

from ImportanceScore.data_loader import MODEL_CONFIG_SCHEMA, CLASSIFICATION_SCHEMA, DataLoader
from ImportanceScore.features import FeaturePreprocessor
from ImportanceScore.manifest import Manifest
from ImportanceScore.model import get_model
from ImportanceScore.project_paths import ProjectPaths


def objective(trial, args, model_config, classification_config, X, y):
    """
    This is the objective function that Optuna tries to optimize.
    It defines the search space and trains a model for one trial.
    """
    model_name = model_config["model"]

    # --- 1. Define the Hyperparameter Search Space ---
    # This is where you define which parameters to tune and their possible ranges.
    if model_name in ["GBR", "XGB", "LGBM"]:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            # Add other parameters like 'subsample', 'colsample_bytree', etc.
        }
    elif model_name == "RFR":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000, step=50),
            "max_depth": trial.suggest_int("max_depth", 5, 30),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        }
    else:
        print(f"Tuning is not configured for model type: {model_name}")
        return float('inf')  # Return a bad score

    # --- 2. Train the Model with the Trial's Parameters ---
    # Create a temporary config with the suggested params for this trial.
    trial_config = model_config.copy()
    trial_config["model_params"] = params

    model = get_model(model_name, config=trial_config, weights=classification_config)

    # --- 3. Evaluate the Model using Cross-Validation ---
    # We use cross-validation to get a robust estimate of the model's performance.
    # The scoring metric should be negative because Optuna minimizes.
    score = cross_val_score(
        model, X, y, n_jobs=-1, cv=3, scoring='neg_mean_squared_error'
    ).mean()

    return score


def main():
    """Orchestrates the tuning process."""
    parser = argparse.ArgumentParser(description="Tune model hyperparameters.")
    parser.add_argument("segment", help="The segment to use for tuning data.")
    parser.add_argument("category", help="The category to tune.")
    args = parser.parse_args()

    # --- 1. Load Data and Configs (same as train_model.py) ---
    paths = ProjectPaths(args.segment, args.category)

    # --- 2. Load Artifacts and Live Configuration ---
    manifest = Manifest()

    try:
        print(f"Load Model config: {paths.model_config}")
        model_config = manifest.load_config(paths.model_config, MODEL_CONFIG_SCHEMA)

        print(f"Load Classification config: {paths.classification_config}")
        classification_config = manifest.load_config(
            paths.classification_config, CLASSIFICATION_SCHEMA
            )

        # We need the full labeled dataset for tuning.
        loader = DataLoader(model_config)
        df = loader.load_and_merge_data(paths.features, paths.targets)

        preprocessor = FeaturePreprocessor(model_config, args.category, model_config["model"])
        X, y, labeled_mask = preprocessor.transform(df, training=True)

        # Use only the labeled data for tuning.
        X_labeled = X[labeled_mask]
        y_labeled = y[labeled_mask]

    except (FileNotFoundError, ValueError) as e:
        print(f"   ❌ Error during setup: {e}")
        sys.exit(1)

    # --- 2. Run the Optuna Study ---
    study = optuna.create_study(direction="maximize")  # Maximize because neg_mse is negative
    study.optimize(
        lambda trial: objective(
            trial, args, model_config, classification_config, X_labeled, y_labeled
            ), n_trials=50  # Number of different parameter combinations to try
    )

    # --- 3. Print the Results ---
    print("\n✅ Tuning complete!")
    print(f"   - Best trial score (neg_mse): {study.best_value}")
    print("   - Best parameters found:\n")
    print("model_params:")
    for key, value in study.best_params.items():
        print(f"       {key}: {value}")

    print("\n➡️ Next Step: Copy this block into ")
    print(f"   your '{args.category}_model.yml' file and run train_model.py.")


if __name__ == "__main__":
    main()
