
CATEGORY_TIER_SCHEMA = {
    'type': 'dict',
    'required': True,
    'schema': {
        'tier_id': {'type': 'integer', 'required': True},
        'minimum': {'type': 'number', 'required': True},
    }
}

GEOTIER_CONFIG_SCHEMA = {
    'config_type': {'type': 'string', 'required': True, 'allowed': ["GeoTierConfig"]},
    'id_column': {'type': 'string', 'required': True},
    'score_column': {'type': 'string', 'required': True},
    'classification': {
        'type': 'string', 'required': False, 'default': 'percentile',
        'allowed': ['percentile', 'score']
    },
    'output_tier_column': {'type': 'string', 'required': True},
    'output_raw_tier_column': {'type': 'string', 'required': True},
    'spatial_separation': {'type': 'boolean', 'required': False, 'default': True},
    'default_tier_id': {'type': 'integer', 'required': False, 'default': 0},
    'ignore_scores_below': {'type': 'float', 'required': False, 'default': 0.0},
    'approximate_distance': {'type': 'boolean', 'required': False, 'default': False},
    'density_modifier': {'type': 'float', 'required': False, 'default': 1.0},
    'tiers': {'type': 'list', 'required': True, 'schema': CATEGORY_TIER_SCHEMA},
}

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

TEXT_WEIGHTS_SCHEMA = {
    "text_weights": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "weight": {"type": "integer", "required": True},
                "description": {"type": "string", "required": True, "empty": False},
                "contains": {
                    "type": "list", "required": False,
                    "schema": {"type": "string", "empty": False}
                },
                "match": {
                    "type": "list", "required": False,
                    "schema": {"type": "string", "empty": False}
                },
            },
        },
    }
}