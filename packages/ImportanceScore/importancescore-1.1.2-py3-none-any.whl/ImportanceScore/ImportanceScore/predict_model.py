# predict_model.py
"""Runs predictions using a pre-trained, serialized model artifact.

This script is the primary entry point for using a trained `ImportanceScore` model.
It orchestrates the end-to-end prediction workflow:

1.  Loads a versioned model artifact (e.g., `model.joblib`).
2.  Loads the live preprocessing configuration from YAML files.
3.  Initializes a `BuildManifest` to track all file artifacts for reproducibility.
4.  Executes the feature preprocessing pipeline.
5.  Generates raw model scores.
6.  Optionally scales the scores and saves the final output.
7.  Saves a manifest file listing all inputs for the run.

This module is designed to be run as a command-line script.
"""

import argparse
from pathlib import Path
import sys
from typing import Dict, Any, Optional

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

from ImportanceScore.data_loader import MODEL_CONFIG_SCHEMA, CLASSIFICATION_SCHEMA
from ImportanceScore.features import FeaturePreprocessor
from ImportanceScore.manifest import Manifest
from ImportanceScore.weighted_linear_model import WeightedLinearModel
from YMLEditor.yaml_reader import ConfigLoader  # Using a generic YAML loader


# A soft dependency on SHAP is used for model explainability.
try:
    import shap
except ImportError:
    shap = None

# --- Module-level Constants ---
DEFAULT_SCORE_COLUMN_NAME = "score"
ROUNDING_PRECISION = 2


class ModelPredictor:
    """Encapsulates the logic for running predictions with a pre-configured model.

    This class is responsible for the core prediction workflow. It is initialized
    with a pre-built model artifact and all necessary configurations, then
    orchestrates the steps of data loading, preprocessing, prediction, and
    output generation.

    Attributes:
        category (str): The category of the model (e.g., 'peaks').
        model (Any): A pre-trained, deserialized model object.
        model_name (str): The name of the model (e.g., 'WLM').
        score_column_name (str): The name for the final score column in the output.
        preprocessor (FeaturePreprocessor): An instance of the feature preprocessor.
    """

    def __init__(
            self, category: str, preprocessing_config: Dict[str, Any],
            output_config: Dict[str, Any], model: Any
    ):
        """Initializes the ModelPredictor with separated configurations.

        Args:
            category (str): The category of the model (e.g., 'peaks').
            preprocessing_config (Dict[str, Any]): Config for the FeaturePreprocessor.
            output_config (Dict[str, Any]): Config for the output stage.
            model (Any): A pre-trained, deserialized model object.
        """
        self.category = category
        self.preprocessing_config = preprocessing_config
        self.output_config = output_config
        self.model = model
        self.model_name = getattr(self.model, 'model_name', 'Unknown')
        self.score_column_name = self.output_config.get(
            "output_score_column", DEFAULT_SCORE_COLUMN_NAME
        )

        self.original_features_df: Optional[pd.DataFrame] = None
        self.preprocessed_features_df: Optional[pd.DataFrame] = None
        self.raw_predictions: Optional[pd.Series] = None
        self.explanation_df: Optional[pd.DataFrame] = None

        self.preprocessor = FeaturePreprocessor(
            self.preprocessing_config, self.category, self.model_name
        )


    def run_predictions(self, features_path: Path) -> None:
        """Loads data, preprocesses features, and generates raw model scores.

        This method orchestrates the primary prediction workflow. For the WLM, it
        uses an optimized internal method (`_compute_predictions`) to calculate
        both the scores and the full explanation table in a single pass, storing
        them on the instance to avoid redundant computation.

        Args:
            features_path (Path): The path to the input features CSV file.
        """
        join_key = self.preprocessing_config.get("join_key", "osm_id")
        self.original_features_df = pd.read_csv(features_path, dtype={join_key: str})

        self.preprocessed_features_df, _, _ = self.preprocessor.transform(
            self.original_features_df, training=False
        )

        print("➡️ Calculating predictions...")

        # --- STAGE 1: Compute Once, Use Twice ---
        # This block  gets both scores and explanations for the WLM
        # in a single pass, preventing redundant calculations.
        if hasattr(self.model, "_compute_predictions"):
            scores, explanations = self.model._compute_predictions(self.preprocessed_features_df)
            self.raw_predictions = pd.Series(scores)
            self.explanation_df = explanations
        else:
            y_pred = self.model.predict(self.preprocessed_features_df)
            self.raw_predictions = pd.Series(y_pred)

        self._validate_predictions()

        score_min = self.raw_predictions.min()
        score_mean = self.raw_predictions.mean()
        score_max = self.raw_predictions.max()
        print(
            f"  ✅ Generated {len(self.raw_predictions)} raw scores. "
            f"Distribution (min/mean/max): {score_min:.1f} / {score_mean:.1f} / {score_max:.1f}"
        )

    def _validate_predictions(self) -> None:
        """Checks for NaN values in raw predictions and fails fast if they exist."""
        if self.raw_predictions.isnull().any():
            invalid_count = self.raw_predictions.isnull().sum()
            error_message = f"""
   ❌ Error: Prediction failed for {invalid_count} item(s).
      The model produced invalid (NaN) scores. This is caused by unhandled
      missing values in the input features. Please update the 'fillna'
      section in '{self.category}_model.yml' to provide a default value.
    """
            print(error_message)
            sys.exit(1)

    def generate_explanation_report(self, explain_output_path: Path) -> None:
        """Generates a file with feature contributions explaining each score.

        This method acts as a router, dispatching to the appropriate explanation
        method based on the model type. For the WLM, it uses the pre-computed
        explanation table to avoid re-running the model.

        Args:
            explain_output_path (Path): The path to save the explanation CSV file.
        """
        print("➡️ Generating feature contribution report...")

        if self.explanation_df is not None:
            self._explain_with_native_method(explain_output_path)
        elif hasattr(self.model, "shap_values"):
            self._explain_with_native_method(explain_output_path)
        elif shap is not None:
            self._explain_with_shap_library(explain_output_path)
        else:
            print("   - Skipping SHAP contributions: 'shap' library is not installed.")

    def find_and_save_anomalies(self, anomaly_output_path: Path) -> None:
        """Finds and saves data anomalies with explanatory Z-scores.

        This method uses Isolation Forest to find anomalous rows, then enriches
        the output by calculating the Z-score for each feature relative to its
        peer group, instantly highlighting *why* a row is considered an anomaly.

        Args:
            anomaly_output_path (Path): The path to save the anomalies CSV file.
        """
        print("➡️ Finding and explaining potential data anomalies...")

        features_to_check = self.preprocessed_features_df
        if features_to_check.empty:
            print(" ⚠️  - Skipping anomaly detection: No data to process.")
            return

        iso_forest = IsolationForest(contamination='auto', random_state=42)
        predictions = iso_forest.fit_predict(features_to_check)
        anomaly_indices = [i for i, p in enumerate(predictions) if p == -1]

        if not anomaly_indices:
            print("   - No significant anomalies found.")
            return

        print(f"   - Found {len(anomaly_indices)} potential anomalies. Now calculating deviation scores...")

        # --- Calculate Z-Scores for Explanation ---
        # Combine original and preprocessed data for calculations.
        combined_df_with_duplicates = pd.concat([self.original_features_df, self.preprocessed_features_df], axis=1)

        # Use .loc to select unique columns, keeping the LAST occurrence
        # of any duplicates. Add .copy() to create a new, independent DataFrame
        # and prevent the SettingWithCopyWarning.
        combined_df = combined_df_with_duplicates.loc[:, ~combined_df_with_duplicates.columns.duplicated(keep='last')].copy()

        zscore_cols = []

        grouping_key = self.anomaly_group_key

        if grouping_key and grouping_key in combined_df.columns:
            print(f"   - Grouping peers by '{grouping_key}' to calculate deviation.")

            for col in features_to_check.columns:
                zscore_col_name = f"{col}_zscore"
                group_mean = combined_df.groupby(grouping_key)[col].transform('mean')
                group_std = combined_df.groupby(grouping_key)[col].transform('std')
                # This assignment is now safe because combined_df is explicitly a copy.
                combined_df[zscore_col_name] = (combined_df[col] - group_mean) / group_std.replace(0, 1)
                zscore_cols.append(zscore_col_name)
        else:
            # Provide a specific, actionable error message.
            print("\n  ⚠️  - WARNING: Cannot generate anomaly deviation scores. ")
            if not grouping_key:
                print("      - Reason: The 'anomaly_group_key' is not defined in your model's .yml config file.")
                print("      - To Fix: Add 'anomaly_group_key: <column_name>' to your config.  This column should include a way to group items (e.g. sub_category)")
            else: # The key was defined, but the column doesn't exist.
                print(f"      - Reason: The specified grouping key '{grouping_key}' was not found as a column in the input data.")
                print(f"      - Available columns are: {list(self.original_features_df.columns)}")
                print(f"      - To Fix: Check for a typo or ensure the column '{grouping_key}' is present in your features CSV.")
            print()

        # 1. Select the anomalous rows from the original data.
        #    This is still a slice, but we will not modify it directly.
        anomaly_base_df = self.original_features_df.iloc[anomaly_indices]

        # 2. Build the final report by explicitly constructing a new DataFrame.
        if zscore_cols:
            # Select the corresponding Z-score rows from the enriched combined_df.
            anomaly_zscores_df = combined_df.iloc[anomaly_indices][zscore_cols]

            # Create a list of the DataFrames to concatenate side-by-side.
            # Resetting the index on both ensures a clean, unambiguous alignment.
            frames_to_concat = [
                anomaly_base_df.reset_index(drop=True),
                anomaly_zscores_df.reset_index(drop=True)
            ]
            final_anomaly_df = pd.concat(frames_to_concat, axis=1)
        else:
            # If no z-scores were calculated, the final report is just the base data.
            # The .copy() here is the final signal to Pandas that this is a new object.
            final_anomaly_df = anomaly_base_df.copy()

        final_anomaly_df.to_csv(anomaly_output_path, index=False, float_format='%.2f')
        print(f"✅ Anomalies report saved to {anomaly_output_path}")

    def _explain_with_native_method(self, output_path: Path) -> None:
        """Generates explanations for models with a built-in method (e.g., WLM)."""
        print(f"   - Generating built-in contributions for '{self.model_name}'...")

        # Use the pre-computed explanation DataFrame to avoid re-running the model.
        explanation_df = self.explanation_df

        if "total_contribution" in explanation_df.columns:
            explanation_df.rename(
                columns={"total_contribution": self.score_column_name}, inplace=True
            )

        join_key = self.preprocessing_config.get("join_key", "osm_id")
        item_name_key = self.preprocessing_config.get("item_name_key", "item_name")
        metadata_cols = [join_key, item_name_key]

        valid_metadata_cols = [
            col for col in metadata_cols if col in self.original_features_df.columns
        ]

        # Identify all columns that represent a feature's contribution.
        # This includes the individual feature scores (ending in '_X') and the final score.
        contribution_cols = [col for col in explanation_df.columns if col.endswith('_X')]
        if self.score_column_name in explanation_df.columns:
            contribution_cols.append(self.score_column_name)

        # Round only the contribution columns to 1 decimal place for readability.
        explanation_df[contribution_cols] = explanation_df[contribution_cols].round(1)

        # Join the original metadata with the full explanation table.
        final_debug_df = self.original_features_df[valid_metadata_cols].join(explanation_df)
        final_debug_df.to_csv(output_path, index=False)
        print(f"✅ Debug contributions saved to {output_path}")

    def _explain_with_shap_library(self, output_path: Path) -> None:
        """Generates explanations for scikit-learn models using the SHAP library."""
        # TODO: Implement SHAP value computation for scikit-learn models.
        print(f"   - SHAP explanation for '{self.model_name}' is not yet implemented.")
        pass

    def save_results(self, output_path: Path) -> None:
        """Finalizes and saves the predicted scores to a CSV file.

        This method handles the final, optional scaling of the raw scores
        based on the `scaling` block in the configuration before saving the
        output.

        Args:
            output_path (Path): The path to save the final output CSV.
        """
        print("➡️ Finalizing output file...")
        output_columns = self.output_config.get("output_columns", [])
        output_df = self.original_features_df[output_columns].copy()

        final_scores = self.raw_predictions.copy()

        if scaling_config := self.output_config.get("scaling"):
            min_s = scaling_config['min']
            max_s = scaling_config['max']

            print(
                f"   - Scaling scores to the relative range [{min_s}, {max_s}] per 'scaling' config."
            )

            # --- Complex Logic: Handle scaling edge case ---
            # If all scores in the batch are identical, the min-max scaler would
            # produce NaNs due to division by zero. We handle this by mapping
            # all scores to the midpoint of the target range.
            if final_scores.min() == final_scores.max():
                midpoint = (min_s + max_s) / 2
                final_scores[:] = midpoint
            else:
                scaler = MinMaxScaler(feature_range=(min_s, max_s))
                scaled_values = scaler.fit_transform(final_scores.values.reshape(-1, 1))
                final_scores = pd.Series(scaled_values.flatten())

        output_df[self.score_column_name] = final_scores.round(ROUNDING_PRECISION)

        final_columns = output_columns + [self.score_column_name]
        print(f"   - Output features: {final_columns}")
        output_df[final_columns].to_csv(output_path, index=False)
        print(f"✅ Results saved to {output_path}")


def main() -> None:
    """Orchestration layer: Handles I/O, config, and calls the main pipeline."""
    parser = argparse.ArgumentParser(description="Predict with a trained importance model.")
    parser.add_argument("--model", type=Path, required=True, help="Path to the trained model artifact (.joblib).")
    parser.add_argument("--features", type=Path, required=True, help="Path to the input features CSV file.")
    parser.add_argument("--config", type=Path, required=True, help="Path to the model configuration YAML file.")
    parser.add_argument("--output", type=Path, required=True, help="Path for the output scores CSV file.")
    parser.add_argument("--category", type=str, required=True, help="Category name (e.g., 'poi').")
    parser.add_argument("--explain", action="store_true", help="Generate a feature contribution report.")
    #parser.add_argument("--show-anomalies", action="store_true", help="Generate a report of data anomalies.")

    parser.add_argument("--log-level", type=int, default=4, help="Set log level.")
    args = parser.parse_args()

    explain_path = None
    if args.explain:
        out_p = args.output
        # Create a path like '.../my_output_explain.csv' from '.../my_output.csv'
        explain_path = out_p.with_name(f"{out_p.stem}_explain{out_p.suffix}")

    #anomaly_path = None
    #if args.show_anomalies:
    #    out_p = args.output
        # Create a path like '.../my_output_anomalies.csv'
    #    anomaly_path = out_p.with_name(f"{out_p.stem}_anomalies{out_p.suffix}")

    file_paths = {
        "model_path": args.model,
        "features_path": args.features,
        "config_path": args.config,
        "output_path": args.output,
        "explain_path": explain_path,
  #      "anomaly_path": anomaly_path,
    }

    # --- STAGE 1: Load Artifacts and Live Configuration ---
    try:
        for p in ["model_path", "features_path", "config_path"]:
            if not file_paths[p].exists():
                raise FileNotFoundError(f"Required file not found: {file_paths[p]}")

        print("➡️ Loading configuration and model artifact...")
        loader = ConfigLoader(MODEL_CONFIG_SCHEMA)
        live_config = loader.read(file_paths["config_path"])

        manifest = Manifest() # Used for loading artifacts
        model = manifest.load_joblib(file_paths["model_path"])

    except (FileNotFoundError, ValueError) as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)

    # --- STAGE 2: Version Validation ---
    model_name = getattr(model, 'model_name', 'Unknown')
    if model_name == "WLM":
        artifact_version = getattr(model, 'version', '0.0')
        current_format_version = WeightedLinearModel.__version__
        if artifact_version != current_format_version:
            print("\n   ⚠️  --- FORMAT VERSION MISMATCH WARNING ---")
            print(f"      The model artifact was created with format version {artifact_version},")
            print(f"      but the current version is  {current_format_version}.")
            print("      Results may be unexpected. It is highly recommended to")
            print(f"      re-run 'train_model.py' for the '{args.category}' category.")
            print("      ----------------------------------\n")

    # --- STAGE 3: Create Focused Configuration Objects for Dependency Injection ---
    preprocessing_config = live_config
    output_config = {
        "output_columns": live_config.get("output_columns", []),
        "scaling": live_config.get("scaling"),
        "output_score_column": live_config.get("output_score_column", "score")
    }

    # --- STAGE 4: Print Configuration Summary ---
    print("\n🔷Score Prediction Configuration:")
    print(f"   - Category: {args.category}")
    print(f"   - Model:    {file_paths['model_path']} (Name: {model_name})")
    print(f"   - Features: {file_paths['features_path']}")
    print(f"   - Config:   {file_paths['config_path']}")
    print(f"   - Output:   {file_paths['output_path']}")
    if args.explain:
        print(f"   - Explain:  {file_paths['explain_path']}")

    print()

    # --- STAGE 5: Instantiate the Predictor and Run the Pipeline ---
    try:
        predictor = ModelPredictor(args.category, preprocessing_config, output_config, model)
        predictor.run_predictions(file_paths["features_path"])

        if args.explain:
            predictor.generate_explanation_report(file_paths["explain_path"])

        predictor.save_results(file_paths["output_path"])
        print("\n✅ Prediction complete.")
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()