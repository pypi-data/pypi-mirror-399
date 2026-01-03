# data_loader.py

import sys

import pandas as pd

from ImportanceScore.model import get_target_column


class DataLoader:
    """
    Handles loading, validating, and merging of feature and target datasets.

    This class encapsulates the data loading logic, using a configuration
    dictionary to dynamically handle different data schemas and requirements.
    """

    def __init__(self, model_config: dict):
        """
        Initializes the DataLoader with a model configuration.

        Args:
            model_config (dict): A dictionary containing model settings, including
                                 the `id_column` and `regressor_target`.
        """
        if not isinstance(model_config, dict):
            raise TypeError("model_config must be a dictionary.")

        self.config = model_config
        self.id_column = self.config['id_column']
        self.name_key = self.config['name_column']
        self.model_name = self.config['model']
        self.target_column = get_target_column(self.config, self.model_name)

    @staticmethod
    def _safe_read_csv(path, dtype=None, required_cols=None, label=None):
        """Internal method to safely read a CSV with validation."""
        try:
            df = pd.read_csv(path, dtype=dtype)
        except Exception as e:
            print(f"  ❌ Error loading {label}: {path}. {e}")
            sys.exit(1)

        if required_cols:
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                print(f"  ❌ {label or path} is missing required columns: {missing}")
                sys.exit(1)
        return df

    def _validate_input_files(self, df_features, df_targets):
        """Internal method to ensure required columns exist in dataframes."""
        required_target_cols = [self.id_column, self.target_column]
        for col in required_target_cols:
            if col not in df_targets.columns:
                raise ValueError(f"Missing '{col}' in targets file.")
        if self.id_column not in df_features.columns:
            raise ValueError(f"Missing '{self.id_column}' in features file.")

    def load_and_merge_data(self, features_path: str, targets_path: str) -> pd.DataFrame:
        """
        Loads, validates, and merges feature and target data.

        Args:
            features_path (str): Path to the features CSV.
            targets_path (str): Path to the targets CSV.

        Returns:
            pd.DataFrame: A merged DataFrame ready for preprocessing.
        """
        required_final_cols = [self.id_column, self.name_key, self.target_column]

        df_features = self._safe_read_csv(
            features_path, dtype={self.id_column: str}, required_cols=[self.id_column],
            label="Features CSV"
        )
        df_targets = self._safe_read_csv(
            targets_path, dtype={self.id_column: str},
            required_cols=[self.id_column, self.target_column], label="Targets CSV"
        )

        try:
            if self.name_key in df_targets.columns:
                df_targets = df_targets.drop(columns=[self.name_key])

            self._validate_input_files(df_features, df_targets)
            df = pd.merge(df_features, df_targets, on=self.id_column, how="left")

            missing = [col for col in required_final_cols if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns after merge: {', '.join(missing)}")

            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)


# Schema for Model config
MODEL_CONFIG_SCHEMA = {
    'config_type': {'type': 'string','required': True,'allowed': ["ModelConfig"] },
    'anomaly_group_key': {'type': 'string', 'required': False},
    'model': {
        'type': 'string', 'required': True,
        'allowed': ['WLM', 'RFR', 'GBT', 'LOGR', 'SVM', 'SVR', 'LR']
    },
    'id_column': {'type': 'string', 'required': True},
    'name_column': {'type': 'string', 'required': True},
    'regressor_target': {'type': 'string', 'required': True},
    'base_score_column': {'type': 'string', 'required': False},

    'scaling': {
        'type': 'dict', 'required': False, 'schema': {
            'min': {'type': 'number', 'required': True},
            'max': {'type': 'number', 'required': True},
        }
    },

    'text_weight_columns': {
        'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []
    }, 'one_hot_columns': {
        'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []
    }, 'fillna': {
        'type': 'dict', 'required': False, 'valuesrules': {'type': ['number', 'string', 'boolean']}
    }, 'conditional_adjustment': {
        'type': 'dict', 'required': False, 'default': {}
    }, 'ignore_columns': {
        'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'default': []
    }, 'output_columns': {
        'type': 'list', 'schema': {'type': 'string'}, 'required': True
    },

    'feature_interactions': {
        'type': 'list', 'required': False, 'schema': {
            'type': 'dict', 'schema': {
                'output_column': {'type': 'string', 'required': True},
                'input_columns': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                'method': {'type': 'string', 'allowed': ['logical_or'], 'required': True}
            }
        }
    },

    #  clip_outliers
    'clip_outliers': {
        'type': 'dict', 'required': False, 'valuesrules': {
            'type': 'dict', 'schema': {
                'method': {'type': 'string', 'allowed': ['IQR', 'threshold'], 'required': True},

                # Parameters for the 'IQR' method
                'factor': {'type': 'number', 'required': False, 'default': 1.5},

                # Parameters for the new 'threshold' method
                'min': {'type': 'number', 'required': False},
                'max': {'type': 'number', 'required': False},
            }
        }
    },

    #  scaler section
    'scaler': {
        'type': 'dict', 'required': False, 'valuesrules': {
            'type': 'string',
            'allowed': ['standard', 'minmax', 'robust', 'power', 'sublinear', 'quantile', 'none']
        }
    },

    'smoothing': {
        'type': 'dict', 'required': False, 'schema': {
            'method': {'type': 'string', 'allowed': ['sigmoid', 'none'], 'required': True},
            'midpoint': {'type': 'number', 'required': False},
            'steepness': {'type': 'number', 'required': False}
        }
    }
}



CLASSIFICATION_SCHEMA = {
    'config_type': {'type': 'string','required': True,'allowed': ["Classification"] },
    'keys': {'type': 'dict', 'required': True},
    'output_tag': {'type': 'string', 'required': True},
    'score_key': {'type': 'string', 'required': True},
    'style': {'type': 'string', 'required': False},
    'features': {'type': 'list', 'required': True},
    'require_name': {
        'type': 'boolean',
        'required': False, # It's an optional setting
        'default': True    # A sensible default: usually we want named features
    },

    'debug_ids': {
        'type': 'list', 'schema': {'type': 'integer'},  # assuming node_row IDs are integers
        'required': False,
    },

    'enrichment': {
        'type': 'list',
        'required': False,
        'schema': {
            'type': 'dict',
            'schema': {
                'file_suffix': {'type': 'string', 'required': True},
                'columns': {
                    'type': 'list',
                    'required': True,
                    'schema': {'type': 'string'}
                }
            }
        }
    },
}
