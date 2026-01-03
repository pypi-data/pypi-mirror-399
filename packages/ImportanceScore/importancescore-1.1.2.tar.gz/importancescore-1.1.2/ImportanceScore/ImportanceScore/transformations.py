# transformations.py
"""
This module provides a collection of pure, self-contained transformation
functions for the feature preprocessing pipeline.

Each function represents a single "strategy" that can be orchestrated by the
FeaturePreprocessor. They accept a logger to report progress and are driven
by a dedicated configuration block.
"""

import logging
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import (QuantileTransformer, PowerTransformer, MinMaxScaler,
                                   RobustScaler, StandardScaler)

from ImportanceScore.text_weight_scoring import apply_text_weights


# --- Transformation Strategies ---

def apply_feature_interactions(
        df: pd.DataFrame, config: List[Dict], logger: logging.Logger
) -> pd.DataFrame:
    """Creates new features based on the 'feature_interactions' config."""
    if not config:
        return df

    logger.info("➡️ Applying feature interactions...")
    for rule in config:
        output_col = rule.get("output_column")
        input_cols = rule.get("input_columns")

        if rule.get("method") == "logical_or":
            if not all(col in df.columns for col in input_cols):
                logger.warning(f"  - Skipping '{output_col}': one or more input columns missing.")
                continue

            combined_series = df[input_cols].any(axis=1)
            df[output_col] = combined_series.astype(int)
            num_created = df[output_col].sum()
            logger.info(
                f"  • Created feature '{output_col}' from {input_cols} for {num_created} rows."
                )
    return df



def apply_one_hot_encoding(
        df: pd.DataFrame, config: Dict[str, Any], logger: logging.Logger
) -> Tuple[pd.DataFrame, List[str]]: # <-- CHANGE 1: Update return signature
    """
    Performs one-hot encoding and returns the transformed DataFrame and the
    names of the newly created dummy columns.
    """
    one_hot_columns = config.get("columns", [])
    if not one_hot_columns:
        logger.info("➡️ No one-hot encoding.")
        return df, [] # Return an empty list

    logger.info(f"➡️ One hot encoding columns: {one_hot_columns}")

    new_dummy_columns = [] # <-- CHANGE 2: Create a list to track new columns
    original_df = df.copy() # Keep a copy before dropping columns

    for col in one_hot_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' for one-hot encoding not found in DataFrame.")

        dummies = pd.get_dummies(df[col], prefix=col, dtype=int)
        new_dummy_columns.extend(dummies.columns.tolist()) # Add new names to the list
        df = pd.concat([df, dummies], axis=1)
        logger.info(f"  • Encoded '{col}' into {len(dummies.columns)} new columns.")

    final_df = df.drop(columns=one_hot_columns, errors="ignore")
    return final_df, new_dummy_columns


def apply_fillna(
        df: pd.DataFrame, config: Dict[str, Any], suppress_warnings_for: List[str],
        logger: logging.Logger, category: str
) -> pd.DataFrame:
    """Validates and fills missing values based on the 'fillna' config block."""
    logger.info("➡️ Validating and filling NaNs...")

    for col, fill_value in config.items():
        if col in df.columns:
            # 1. Check if the column actually has any NaN values to fill.
            if df[col].isnull().any():
                # 2. Count how many NaNs exist *before* filling.
                nan_count = df[col].isnull().sum()

                # 3. Perform the fillna operation.
                df[col] = df[col].fillna(fill_value)

                # 4. Log the detailed result.
                log_fill_value = f"'{fill_value}'" if isinstance(fill_value, str) else fill_value
                logger.info(f"  • Filled {nan_count} NaN row(s) in '{col}' with: {log_fill_value}")

                # Mark that at least one operation was performed.
                any_rows_filled = True

    unhandled_nan_columns = [
            col for col in df.columns
            if col not in suppress_warnings_for and df[col].isnull().any()
        ]

    if unhandled_nan_columns:
        # Create a detailed, multi-line error message that is a mini-guide.
        error_message = (
            f"After running fill Nans, there is still missing data in column(s): {unhandled_nan_columns}.\n\n"
            f"      To fix this, edit the configuration file\n\n"
            f"      Add the above column(s) and a default value to the 'fillna' section.\n"
            f"      For example:\n\n"
            f"      fillna:\n"
        )
        # Dynamically create the example snippet based on the missing columns.
        for col in unhandled_nan_columns:
            # Check if the column is likely text to suggest a smart default.
            if 'name' in col or 'text' in col:
                default_suggestion = '""' # Suggest empty string for text
            else:
                default_suggestion = 0 # Suggest 0 for numbers
            error_message += f"        {col}: {default_suggestion}\n"

        raise ValueError(error_message)

    logger.info("  ✅ All missing values fixed.")

    return df


def apply_text_weight_scoring(
        df: pd.DataFrame, config: Dict[str, Any], category: str, logger: logging.Logger
) -> pd.DataFrame:
    """Applies text-based scoring based on the 'text_weight_columns' config block."""
    text_weight_cols = config.get("columns", [])
    if not text_weight_cols:
        return df

    logger.info("➡️ Applying text weights:")
    # Pass logger if the downstream function supports it, otherwise pass verbose=True
    apply_text_weights(df, text_weight_cols, category, "config")
    return df


def apply_conditional_adjustment(
        df: pd.DataFrame, config: Dict[str, Any], logger: logging.Logger
) -> pd.DataFrame:
    """Conditionally adjusts a numeric column based on the 'conditional_adjustment' config."""
    if not config:
        return df

    logger.info("➡️ Applying conditional adjustments...")
    try:
        flag_col, target_col = config["flag_col"], config["target_col"]
        new_col, factor = config["new_col"], config["factor"]

        if flag_col not in df or target_col not in df:
            missing = [col for col in [flag_col, target_col] if col not in df]
            raise ValueError(f"Missing required columns for conditional scaling: {missing}")

        modified_rows_mask = (df[flag_col] == 1)
        modified_count = modified_rows_mask.sum()
        df[new_col] = np.where(modified_rows_mask, df[target_col] * factor, df[target_col])

        logger.info(f"  • Conditionally scaled {modified_count} rows in '{target_col}'.")
    except KeyError as e:
        logger.warning(f"  - Skipping conditional adjustment: Missing required key {e} in config.")
    except Exception as e:
        logger.warning(f"  - Skipping conditional adjustment: An error occurred: {e}")
    return df


def clip_outliers(
        df: pd.DataFrame, config: Dict[str, Any], logger: logging.Logger
) -> pd.DataFrame:
    """Clips outliers using methods defined in the 'clip_outliers' config block."""
    if not config:
        logger.info("➡️ No outliers clipped.")
        return df

    logger.info("➡️ Clipping outliers...")
    for col, spec in config.items():
        if col not in df.columns:
            continue

        method = spec.get("method")
        original_min, original_max = df[col].min(), df[col].max()
        clipped_series = df[col].copy()

        if method == "IQR":
            factor = spec.get("factor", 1.5)
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound, upper_bound = q1 - factor * iqr, q3 + factor * iqr
            clipped_series = df[col].clip(lower_bound, upper_bound)
        elif method == "threshold":
            min_val, max_val = spec.get("min"), spec.get("max")
            clipped_series = df[col].clip(lower=min_val, upper=max_val)

        num_clipped = (df[col] != clipped_series).sum()
        if num_clipped > 0:
            new_min, new_max = clipped_series.min(), clipped_series.max()
            logger.info(
                f"  • {col} ({method}): Clipped {num_clipped} values. "
                f"Range changed from [{original_min:.2f}, {original_max:.2f}] "
                f"to [{new_min:.2f}, {new_max:.2f}]."
            )
        df[col] = clipped_series
    return df


def scale_features(
        X: pd.DataFrame, config: Dict[str, Any], logger: logging.Logger
) -> pd.DataFrame:
    """Applies feature scaling based on the 'scaler' config block."""
    if not config:
        return X

    logger.info("➡️ Scaling numeric features...")
    is_binary = X.apply(lambda col: set(col.dropna().unique()).issubset({0, 1}))
    non_binary_cols = [col for col in X.columns if not is_binary.get(col, False)]

    scalers = {
        "standard": StandardScaler, "minmax": MinMaxScaler, "robust": RobustScaler,
        "quantile": QuantileTransformer, "power": PowerTransformer
    }

    for col, scale_type in config.items():
        if col in non_binary_cols and col in X.columns:
            if scale_type == "sublinear":
                X[col] = X[col].apply(lambda x: x ** 0.4 if pd.notnull(x) and x >= 0 else x)
                logger.info(f"  • Scaled '{col}' using sublinear exponent (x**0.4).")
            elif (scaler_cls := scalers.get(scale_type)):
                X[[col]] = scaler_cls().fit_transform(X[[col]])
                logger.info(f"  • Scaled '{col}' using '{scale_type}' scaler.")
    return X
