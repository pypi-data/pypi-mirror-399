# weighted_linear_model.py
import sys
from typing import Dict, Optional, Tuple, Iterator, List

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted

MODE_FEATURE_VALUE = "value"
MODE_BASE_MULTIPLIER = "base_multiplier"
MODE_PRESENCE = "presence"
MODE_ASIS = "asis"
VALID_MODES = {MODE_FEATURE_VALUE, MODE_BASE_MULTIPLIER, MODE_PRESENCE, MODE_ASIS}


class WeightedLinearModel(BaseEstimator, RegressorMixin):
    """
    A rule-based regressor that computes scores by applying user-defined
    coefficients and modes to input features.
    """

    # Class-level version.
    # Increment this whenever you make a breaking change to the model's logic
    # or its required parameters.
    __version__ = "1.1"

    def __init__(
            self, feature_coefficients: List[Dict], base_score_column: Optional[str] = None,
            intercept: float = 0.0, max_contribution: Optional[float] = None, verbose: bool = True
    ):
        """Initializes the WeightedLinearModel."""
        self.feature_coefficients = feature_coefficients
        self.base_score_column = base_score_column
        self.intercept = intercept
        self.max_contribution = max_contribution
        self.verbose = verbose
        self._is_fitted = True # It's "fitted" by definition upon instantiation

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Computes weighted scores for input samples."""
        check_is_fitted(self, "_is_fitted")
        # Call compute but only keep the scores.
        try:
            scores, _ = self._compute_predictions(X)
        except Exception as e:
            print(f"  ⚠️ Warning: {e}")
            sys.exit(1)
        return scores

    def shap_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a detailed DataFrame of all raw features and their calculated contributions.
        This is the primary method for getting the full explanation table.
        """
        check_is_fitted(self, "_is_fitted")
        # Call compute and return the FULL explanation DataFrame.
        _, explanations = self._compute_predictions(X)
        return explanations

    def _compute_predictions(self, X: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Internal method to compute scores and the full explanation breakdown.
        """
        # builds explanations_df with all features and contributions.
        # rounds the output.
        # returns the full DataFrame.

        try:
            features_used = [f for f, _, _ in self._iter_feature_coefficients()]
        except Exception as e:
            raise ValueError(f"   {e}" )

        if self.verbose:
            print(
                f"\n🔵 WLM: intercept: {self.intercept}, base_score_column: "
                f"{self.base_score_column}"
            )
            print(f"➡️  Features used: {features_used}")

        if self.base_score_column and self.base_score_column not in X.columns:
            raise ValueError(f"Features CSV is missing required base_score_column '{self.base_score_column}' set in model config")

        # The `explanations_df` starts as a copy of ALL input features.
        explanations_df = X.copy()
        total_contribution = pd.Series(self.intercept, index=X.index)

        for feature, coefficient, mode in self._iter_feature_coefficients():
            if feature not in X.columns:
                if self.verbose:
                    print(f"  ⚠️ Warning: Column '{feature}' not found. Skipping.")
                # Add the empty contrib column so the schema is consistent.
                explanations_df[f"{feature}_X"] = 0
                continue

            base_score = X.get(self.base_score_column, pd.Series(0.0, index=X.index))
            contribution = self._get_feature_contribution(base_score, X[feature], coefficient, mode)
            explanations_df[f"{feature}_X"] = contribution
            total_contribution += contribution

        explanations_df["total_contribution"] = total_contribution

        contribution_columns = [c for c in explanations_df.columns if c.endswith('_contrib')] + [
            'total_contribution']
        explanations_df[contribution_columns] = explanations_df[contribution_columns].round(2)

        return total_contribution.to_numpy(), explanations_df

    def _get_feature_contribution(
            self, base_score: pd.Series, feature_value: pd.Series, coefficient: float, mode: str
    ) -> pd.Series:
        """Computes the contribution of a single feature (vectorized)."""
        is_present = (feature_value != 0) & (feature_value.notna())
        contribution = pd.Series(0.0, index=base_score.index)

        if mode == MODE_FEATURE_VALUE:
            contribution = coefficient * feature_value.astype(float)
        elif mode == MODE_BASE_MULTIPLIER:
            contribution = is_present * ((coefficient / 100.0) * base_score)
        elif mode == MODE_PRESENCE:
            contribution = is_present * coefficient

        if self.max_contribution is not None:
            contribution = contribution.clip(upper=self.max_contribution)
        return contribution

    def _iter_feature_coefficients(self) -> Iterator[Tuple[str, float, str]]:
        """Yields (feature, coefficient, mode) triples from the config."""
        for entry in self.feature_coefficients:
            if isinstance(entry, dict) and len(entry) == 1:
                feature, config = next(iter(entry.items()))
                try:
                    coefficient = config["coefficient"]
                    mode = config["mode"]
                    if mode not in VALID_MODES:
                        raise ValueError(f"Invalid mode '{mode}' for feature '{feature}'.")
                    yield feature, coefficient, mode
                except KeyError as e:
                    raise ValueError(f"Config error:  '{feature}' is missing key : {e}\n   Fix the _classification file")
            else:
                raise ValueError(f"Invalid feature coefficient entry: {entry}")

    def get_params(self, deep: bool = True) -> Dict:
        """Returns model parameters for scikit-learn compatibility."""
        return {
            "feature_coefficients": self.feature_coefficients,
            "base_score_column": self.base_score_column, "intercept": self.intercept,
            "max_contribution": self.max_contribution, "verbose": self.verbose,
        }

    def set_params(self, **params) -> "WeightedLinearModel":
        """Set model parameters for scikit-learn compatibility."""
        for key, value in params.items():
            setattr(self, key, value)
        return self

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """No-op for compatibility with scikit-learn pipelines."""
        self.feature_names_in_ = np.array(X.columns)
        self._is_fitted = True
        return self
