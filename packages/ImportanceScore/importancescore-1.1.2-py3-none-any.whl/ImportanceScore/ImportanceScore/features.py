# features.py
"""
This module provides a robust FeaturePreprocessor class that acts as a
data-driven orchestrator for the feature preprocessing pipeline.
"""
import logging
import sys
from typing import Tuple, Dict, Any, List

import pandas as pd

from ImportanceScore import transformations
from ImportanceScore.model import get_target_column


# --- Module-Level Helper for Logging ---
def _setup_logger(level) -> logging.Logger:
    """Initializes and configures the logger for the feature pipeline."""
    logger = logging.getLogger("__file__")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class FeaturePreprocessor:
    """
    Orchestrates the feature preprocessing pipeline by executing a configurable
    sequence of independent transformation strategies.
    """
    def __init__(self, model_config: Dict[str, Any], category: str, model_name: str):
        """Initializes the FeaturePreprocessor."""
        self.config = model_config
        self.category = category
        self.model_name = model_name
        self.target_col_name = get_target_column(self.config, self.model_name)
        self.logger = _setup_logger(4)

        # This property will store the names of columns created during one-hot encoding.
        self.one_hot_column_names: List[str] = []

        self.pipeline_steps = [
            ("feature_interactions", transformations.apply_feature_interactions),
            ("fillna", lambda df, cfg, log: transformations.apply_fillna(
                df, cfg, [self.target_col_name], log, self.category
            )),
            ("text_weight_columns", lambda df, cfg, log: transformations.apply_text_weight_scoring(
                df, {"columns": cfg}, self.category, log
            )),
            ("conditional_adjustment", transformations.apply_conditional_adjustment),
        ]

    def transform(
            self, raw_dataframe: pd.DataFrame, training: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Executes the full preprocessing pipeline in the correct order."""
        self.logger.info("\n🔷Preprocessing Features:\n")
        self.logger.info(f"   {len(raw_dataframe)}  records.")

        try:
            processed_df = raw_dataframe.copy()

            # --- Step 1: Handle the special case of one-hot encoding first ---
            one_hot_config = {"columns": self.config.get("one_hot_columns", [])}
            processed_df, self.one_hot_column_names = transformations.apply_one_hot_encoding(
                processed_df, one_hot_config, self.logger
            )

            # --- Step 2: Run the rest of the data-driven pipeline ---
            for config_key, transform_func in self.pipeline_steps:
                step_config = self.config.get(config_key, {})
                processed_df = transform_func(processed_df, step_config, self.logger)

            # --- Step 3: Post-Transformation Orchestration ---
            y, labeled_mask = self._extract_labels(processed_df, training)
            feature_matrix_X = self._prune_columns(processed_df)
            feature_matrix_X = transformations.clip_outliers(
                feature_matrix_X, self.config.get("clip_outliers", {}), self.logger
            )
            feature_matrix_X = transformations.scale_features(
                feature_matrix_X, self.config.get("scaler", {}), self.logger
            )
            self._validate_feature_coverage(feature_matrix_X)

            return feature_matrix_X, y, labeled_mask

        except (ValueError, KeyError) as e:
            self.logger.error(f"\n   ❌ Preprocessing Error: {e}")
            self.logger.error("      Processing stopped. Please correct the error above and rerun.")
            sys.exit(1)

    # --- Orchestration-Level Helper Methods ---

    def _extract_labels(self, df: pd.DataFrame, training: bool) -> Tuple[pd.Series, pd.Series]:
        """Extracts the target variable (y) and a mask of labeled rows."""
        if not training:
            return pd.Series([pd.NA] * len(df), dtype="Int64"), pd.Series([False] * len(df))

        if self.target_col_name not in df.columns:
            raise KeyError(
                f"Label column '{self.target_col_name}' is required for training but is missing."
            )

        dtype = "Int64" if self.config.get("task_type") == "classification" else "float64"
        y = df[self.target_col_name].astype(dtype)
        return y, y.notna()

    def _prune_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes ignored and non-numeric columns to create the feature matrix."""
        self.logger.info("➡️ Pruning columns to create feature matrix...")

        ignore_cols = self.config.get("ignore_columns", [])
        df.drop(columns=ignore_cols, errors="ignore", inplace=True)

        numeric_dtypes = ["int64", "float64", "bool"]
        non_numeric_cols = df.select_dtypes(exclude=numeric_dtypes).columns.tolist()
        df.drop(columns=non_numeric_cols, errors="ignore", inplace=True)

        self.logger.info(f"  • Ignored columns dropped: {ignore_cols}")
        self.logger.info(f"  • Non-numeric columns dropped: {non_numeric_cols or 'none'}")

        return df

    def _validate_feature_coverage(self, X: pd.DataFrame) -> None:
        """Validates that each feature column has some non-zero coverage."""
        self.logger.info("\n✳️ Feature column coverage:\n")
        for col in X.columns:
            _validate_tag(X, col, threshold=1, logger=self.logger)

        self.logger.info("\n")

# ---  Utility Functions ---

def _validate_tag(df: pd.DataFrame, column: str, threshold: float = None, logger=None) -> bool:
    """Ensures a given column has sufficient non-zero coverage."""
    if column not in df.columns:
        logger.info(f"❌ Column '{column}' not found for coverage validation.")
        return False

    pct_filled = df[column].fillna(0).ne(0).mean()

    if threshold is None:
        logger.info(f"↪ Column '{column}': {pct_filled:.0%} filled")
        return True

    is_valid = pct_filled >= (threshold / 100)
    status_emoji = "🆗" if is_valid else "⚠️"
    column_name = f"{column}:"
    logger.info(
        f"      {status_emoji} {column_name:<20} {pct_filled:>7.2%} filled"
    )
    return is_valid
