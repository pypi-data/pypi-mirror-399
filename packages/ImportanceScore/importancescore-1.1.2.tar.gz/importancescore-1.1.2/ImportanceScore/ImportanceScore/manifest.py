# src/artifacts.py
"""
This module provides tools for creating a build manifest that includes all config
files used for this build.  That list can be committed to git to archive this build.
"""
from pathlib import Path
from typing import Set, Dict, Any

import joblib
from YMLEditor.yaml_reader import ConfigLoader

from ImportanceScore.project_paths import ProjectPaths


class Manifest:
    """
    Tracks all configuration and model files used in a run.  Saves the
    file list.
    """
    _file_list: Set[Path] = set()  # Single Class variable for all instances

    def load_config(self, path: Path, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Reads a YAML file, tracks its path automatically, and returns its contents.
        It passes any additional keyword arguments directly to the underlying
        ConfigLoader.read() method.

        Args:
            path (Path): The path to the YAML configuration file.
            schema (Dict[str, Any]): The validation schema for the file.
            **kwargs: Additional keyword arguments to pass to ConfigLoader.read(),
                      such as 'root_node' or 'block_descriptor'.

        Returns:
            A dictionary containing the validated configuration.
        """
        self._add_file(path)

        loader = ConfigLoader(schema)
        # Unpack the kwargs dict to pass them as keyword arguments.
        return loader.read(path, **kwargs)

    def load_joblib(self, model_path):
        self._add_file(model_path)
        if not model_path.is_file():
            raise FileNotFoundError(
                f"Model artifact not found at '{model_path}'. "
                "Please run train_model.py to create it."
            )
        try:
            job = joblib.load(model_path)
        except Exception as e:
            # Catch errors specifically from joblib.load and provide a rich message.
            msg = (f"\n   ❌ Error: Failed to load the model artifact from '{model_path}'.\n"
            f"      The file may be corrupted or was created with an incompatible library version.\n"
            f"      Underlying error: {e}")
            raise ValueError(msg)
        return job

    def save(self, segment, category):
        """
        Creates a .txt file listing all tracked artifacts and prints the
        corresponding git commit command to the console.
        """
        paths = ProjectPaths(segment, category)
        paths.manifest_dir.mkdir(parents=True, exist_ok=True)

        # Write the simple list of files to the manifest file
        with open(paths.manifest, 'w') as f:
            for file_path in sorted(list(self._file_list)):
                f.write(f"{file_path}\n")

        print(f"✅ Build Manifest saved to {paths.manifest}.")

    def _add_file(self, path: Path):
        """Adds a file  to be included in the manifest."""
        self._file_list.add(path)
