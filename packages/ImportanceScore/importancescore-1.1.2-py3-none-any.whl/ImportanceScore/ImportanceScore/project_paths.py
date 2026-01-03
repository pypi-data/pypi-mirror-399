# src/paths.py
"""
This module provides a centralized class for managing all file and directory
paths for the ImportanceScore project.

It acts as the single source of truth for the project's directory structure
and file naming conventions, ensuring consistency and making the system
easy to maintain.
"""

from pathlib import Path


class ProjectPaths:
    """
    A centralized manager for all project file and directory paths.
    """
    # --- Directory and Suffix Constants ---
    CONFIG_DIR_NAME = "config"
    MODELS_DIR_NAME = "models"
    DATA_DIR_NAME = "data"
    RAW_DIR_NAME = "raw"
    INTERIM_DIR_NAME = "interim"
    LOGS_DIR_NAME = "logs"
    MANIFEST_DIR_NAME = "archive"

    FEATURES_SUFFIX = "_features.csv"
    TARGETS_SUFFIX = "_targets.csv"
    MODEL_CONFIG_SUFFIX = "_model.yml"
    CLASSIFICATION_SUFFIX = "_classification.yml"
    SCORE_SUFFIX = "_score.csv"
    EXPLAIN_SUFFIX = "_explain.csv"
    MODEL_ARTIFACT_SUFFIX = "_model.joblib"
    MANIFEST_SUFFIX = "_manifest.txt"

    def __init__(self, segment: str, category: str):
        """
        Initializes the path manager for a specific segment and category.

        Args:
            segment (str): The data segment (e.g., 'yellowstone').
            category (str): The data category (e.g., 'poi').
        """
        self.segment = segment
        self.category = category

        # --- Base Directories ---
        self.config_dir = Path(self.CONFIG_DIR_NAME)
        self.models_dir = Path(self.MODELS_DIR_NAME)
        self.data_dir = Path(self.DATA_DIR_NAME)
        self.raw_data_dir = self.data_dir / self.RAW_DIR_NAME
        self.interim_data_dir = self.data_dir / self.INTERIM_DIR_NAME
        self.logs_dir = Path(self.LOGS_DIR_NAME)
        self.manifest_dir = Path(self.MANIFEST_DIR_NAME)

    # --- Properties for Fully Constructed Paths ---

    @property
    def model_config(self) -> Path:
        """Path to the model configuration YAML file."""
        return self.config_dir / f"{self.category}{self.MODEL_CONFIG_SUFFIX}"

    @property
    def classification_config(self) -> Path:
        """Path to the classification/WLM coefficients YAML file."""
        return self.config_dir / f"{self.category}{self.CLASSIFICATION_SUFFIX}"

    @property
    def features(self) -> Path:
        """Path to the input features CSV file for the segment."""
        return self.raw_data_dir / f"{self.segment}_{self.category}{self.FEATURES_SUFFIX}"

    @property
    def manifest(self) -> Path:
        """Path to the input features CSV file for the segment."""
        return self.manifest_dir / f"{self.segment}_{self.category}_manifest.txt"

    @property
    def targets(self) -> Path:
        """Path to the input targets CSV file for the category."""
        return self.raw_data_dir / f"{self.category}{self.TARGETS_SUFFIX}"

    @property
    def model_artifact(self) -> Path:
        """Path to the serialized .joblib model artifact."""
        return self.models_dir / f"{self.category}{self.MODEL_ARTIFACT_SUFFIX}"

    @property
    def score_output(self) -> Path:
        """Path to the final output score CSV file."""
        return self.interim_data_dir / f"{self.segment}_{self.category}{self.SCORE_SUFFIX}"

    @property
    def explain_output(self) -> Path:
        """Path to the optional explanation log file."""
        return self.logs_dir / f"{self.segment}_{self.category}{self.EXPLAIN_SUFFIX}"
