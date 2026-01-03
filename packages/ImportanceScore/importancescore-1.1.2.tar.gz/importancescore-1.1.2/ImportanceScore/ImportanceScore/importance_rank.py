# importance_rank.py
import argparse
from ImportanceScore import resources as pkg_resources
from pathlib import Path
import shutil
import sys
from typing import List

from cerberus import Validator
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QCloseEvent, QFont, QShortcut, QKeySequence
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout,
                               QPushButton, QMessageBox, QTextEdit, QHBoxLayout, QTabWidget,
                               QPlainTextEdit, QSplitter)
import yaml
from YMLEditor.yaml_reader import ConfigLoader

from LiteBuild.build_workers import BuildWorker
from LiteBuild.lite_build_controller import LiteBuildController
from csv_table import CsvTable
from custom_editor import PygmentsHighlighter
from importance_schema import (CLASSIFICATION_SCHEMA, MODEL_CONFIG_SCHEMA, GEOTIER_CONFIG_SCHEMA,
                               TEXT_WEIGHTS_SCHEMA)

# =============================================================================
#  MAIN APPLICATION WINDOW
# =============================================================================
class ImportanceRank(QMainWindow):
    def __init__(self, config_name="default", text_score_suffixes=None):
        super().__init__()
        # 1. Resolve LiteBuild Config File Path
        # If the user passed a path, use it.
        # If they passed "default", extract the LiteBuild Config resource to a temp file or user dir.
        if config_name == "default":
            self.config_name = self._ensure_default_config_exists()
        else:
            self.config_name = config_name

        self.setWindowTitle(f"Importance Ranking Editor: {self.config_name}")
        self.controller = LiteBuildController(self.config_name)

        # Build config_files_meta dynamically
        self.config_files_meta = [
            {"suffix": "classification", "schema": CLASSIFICATION_SCHEMA, "mandatory": True},
            {"suffix": "model", "schema": MODEL_CONFIG_SCHEMA, "mandatory": True},
            {"suffix": "tiers", "schema": GEOTIER_CONFIG_SCHEMA, "mandatory": True},
        ]
        # Add a tab for each text scoring file provided
        for suffix in text_score_suffixes:
            self.config_files_meta.append(
                {"suffix": f"{suffix}_weights", "schema": TEXT_WEIGHTS_SCHEMA, "mandatory": False}
            )

        self.editors = {}
        self._dirty_state = {}

        self.category_input = QLineEdit()
        self.region_input = QLineEdit()
        self.load_button = QPushButton("Load")
        self.save_button = QPushButton("Save")
        self.new_button = QPushButton("New")

        self.editor_tabs = QTabWidget()
        self.viewer_tabs = QTabWidget()

        # Runner widget UI elements
        self.runner_widget = QWidget()
        self.run_profile_button = QPushButton("Rank")
        self.console_output = QTextEdit()

        # --- columns to drop to the Scores table---
        hide_scores_columns = ["article_length", "item_name_score", "sub_category_score", "area",
            "wikipedia_X"]
        self.scores_tab = CsvTable()

        # --- columns to drop to the Ranks table---
        hide_ranks_columns = ["osm_category", "lon", "sub_category_score", "area", "wikipedia_X"]
        self.tiers_tab = CsvTable()

        self._setup_ui()
        self._connect_signals()

    def _ensure_default_config_exists(self) -> str:
        """Extracts the bundled LiteBuild config to config/LB_classify_OSM.yml."""
        # 1. Define Path
        target_path = Path("config/LB_classify_OSM.yml")

        # 2. Create config Directory if missing
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 3. Extract Resource
        if not target_path.exists():
            print("Extracting default workflow config...")
            import importlib.resources
            from ImportanceScore import resources as pkg_resources

            source_file = importlib.resources.files(pkg_resources).joinpath("LB_classify_OSM.yml")
            with importlib.resources.as_file(source_file) as source_path:
                shutil.copy(source_path, target_path)

        return str(target_path)

    def _setup_ui(self):
        # --- Top Toolbar ---
        top_layout = QHBoxLayout()

        top_layout.addWidget(QLabel("Region:"))
        top_layout.addWidget(self.region_input)
        top_layout.addWidget(QLabel("Category:"))
        top_layout.addWidget(self.category_input)

        self.load_button.setFixedWidth(80)
        top_layout.addWidget(self.load_button)

        self.save_button.setFixedWidth(80)
        top_layout.addWidget(self.save_button)

        self.new_button.setFixedWidth(80)
        self.new_button.clicked.connect(self.on_new_clicked) # Connect signal
        top_layout.addWidget(self.new_button)

        #  Rank Button
        self.run_profile_button.setText("▶ Rank")
        self.run_profile_button.setFixedWidth(100)
        # Optional: styling to make it stand out
        self.run_profile_button.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(self.run_profile_button)

        # --- Editor Tabs ---
        for meta in self.config_files_meta:
            suffix = meta["suffix"]
            editor = self._create_editor_tab(suffix)
            self.editors[suffix] = editor
            self.editor_tabs.addTab(editor, suffix.replace("_", " ").title())
            self._init_dirty_state(suffix)

        # --- Log Tab  ---
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Workflow Output:"))
        log_layout.addWidget(self.console_output)

        self.runner_widget.setLayout(log_layout)
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet(
            "QTextEdit { background-color: #2b2b2b; color: #f0f0f0; font-family: monospace; }"
        )
        self.editor_tabs.addTab(self.runner_widget, "Log")

        # --- Viewers ---
        self.viewer_tabs.addTab(self.scores_tab, "Scores")
        self.viewer_tabs.addTab(self.tiers_tab, "Ranks")

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.editor_tabs)
        splitter.addWidget(self.viewer_tabs)
        splitter.setSizes([400, 300])

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _init_dirty_state(self, suffix: str):
        if suffix not in self._dirty_state: self._dirty_state[suffix] = False

    def _validate_key(self, suffix: str):
        if suffix not in self._dirty_state: raise KeyError(f"Invalid key: '{suffix}'")

    def mark_dirty(self, suffix: str):
        self._validate_key(suffix)
        if not self._dirty_state[suffix]:
            self._dirty_state[suffix] = True
            index = list(self.editors.keys()).index(suffix)
            self.editor_tabs.setTabText(index, self.editor_tabs.tabText(index) + "*")

    def mark_clean(self, suffix: str):
        self._validate_key(suffix)
        if self._dirty_state[suffix]:
            self._dirty_state[suffix] = False
            index = list(self.editors.keys()).index(suffix)
            self.editor_tabs.setTabText(index, self.editor_tabs.tabText(index).rstrip("*"))

    def get_dirty(self, suffix: str) -> bool:
        self._validate_key(suffix)
        return self._dirty_state[suffix]

    def any_dirty(self) -> bool:
        return any(self._dirty_state.values())

    def _create_editor_tab(self, name: str):
        editor = QPlainTextEdit()
        font = QFont("monospace")
        editor.setFont(font)
        editor.setStyleSheet(
            "QPlainTextEdit { background-color: #272822; color: #F8F8F2; font-size: 14px; }"
            )
        PygmentsHighlighter(editor.document())
        editor.textChanged.connect(lambda name=name: self.mark_dirty(name))
        return editor

    def _connect_signals(self):
        self.load_button.clicked.connect(self.load)
        self.save_button.clicked.connect(self.save_all_files)
        self.category_input.returnPressed.connect(self.load)
        self.run_profile_button.clicked.connect(self.start_profile_build)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        self.controller.build_finished.connect(self.refresh_data_viewers)

        # ---  Keyboard Shortcut (Cmd+S / Ctrl+S) ---
        self.save_shortcut = QShortcut(QKeySequence.Save, self)
        self.save_shortcut.activated.connect(self.save_all_files)

        self.controller.build_started.connect(self.on_build_started)
        self.controller.build_finished.connect(self.on_build_finished)
        self.controller.build_finished.connect(self.refresh_data_viewers)  # Auto-refresh on finish
        self.controller.build_error.connect(self.on_build_error)
        self.controller.log_received.connect(self.update_console)

    def on_tab_changed(self, index: int):
        if self.any_dirty():
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Save changes?", QMessageBox.Save | QMessageBox.Cancel
                )
            if reply == QMessageBox.Save: self.save_all_files()

    def get_filename(self, category: str, suffix: str) -> Path:
        return Path("config") / f"{category}_{suffix}.yml"

    def on_new_clicked(self):
        """Creates a new category setup by copying templates."""
        category = self.category_input.text().strip()
        if not category:
            QMessageBox.warning(self, "Input Error", "Please enter a name for the new Category.")
            return

        msg = (f"Create new configuration files for category: '{category}'?\n\n"
               "This will copy templates (xx_*) to create your new config files.")
        if QMessageBox.question(self, "Create New Category", msg, QMessageBox.Ok | QMessageBox.Cancel) != QMessageBox.Ok:
            return

        # 1. Setup Directories & Imports
        config_dir = Path("config")
        for folder in ["build", "config", "models"]:
            Path(folder).mkdir(exist_ok=True)

        import importlib.resources
        try:
            from ImportanceScore import resources as pkg_resources
        except ImportError:
            QMessageBox.critical(self, "Import Error", "Could not import 'ImportanceScore.resources'.")
            return

        # 2. Build the Copy Plan (List of tuples: [source_name, dest_path])
        copy_plan = []

        # A. Category-Specific Files (xx_suffix.yml -> category_suffix.yml)
        for meta in self.config_files_meta:
            suffix = meta["suffix"]
            template = f"xx_{suffix}.yml"
            dest = config_dir / f"{category}_{suffix}.yml"
            copy_plan.append((template, dest))

        # B. Global Static Files (tier_separation.yml -> tier_separation.yml)
        copy_plan.append(("tier_separation.yml", config_dir / "tier_separation.yml"))
        copy_plan.append(("db_config.yml", config_dir / "db_config.yml"))
        copy_plan.append(("ignore_tags.yml", config_dir / "ignore_tags.yml"))

    # 3. Execute Copy
        created_files = []
        try:
            for template_name, dest_path in copy_plan:
                if dest_path.exists():
                    print(f"Skipping {dest_path.name} (Exists)")
                    continue

                if importlib.resources.is_resource(pkg_resources, template_name):
                    with importlib.resources.path(pkg_resources, template_name) as source:
                        shutil.copy(source, dest_path)
                        created_files.append(dest_path.name)
                else:
                    print(f"⚠️ Warning: Resource template '{template_name}' not found.")

            # 4. Report Results
            if created_files:
                QMessageBox.information(self, "Success",
                                        f"Created {len(created_files)} files in config/:\n" +
                                        "\n".join(created_files))
                self.load()
            else:
                QMessageBox.information(self, "No Changes", "No new files were created (files may already exist).")

        except Exception as e:
            QMessageBox.critical(self, "Error Creating Files", str(e))

    def refresh_data_viewers(self):
        """Reloads the data in the bottom viewer tabs."""
        category = self.category_input.text().strip()
        region = self.region_input.text().strip()

        if not category or not region:
            QMessageBox.warning(self, "Input Error", "Please provide a Category and Region.")
            return

        base_path = Path("build") / region / "interim"

        hide_scores_columns = ["article_length", "item_name_score", "sub_category_score", "area",
            "wikipedia_X"]
        scores_file = base_path / f"{region}_{category}_score_explain.csv"

        hide_ranks_columns = ["osm_category", "lon", "sub_category_score", "area", "wikipedia_X"]
        tiers_file = base_path / f"{region}_{category}_tiers.csv"

        self.tiers_tab.clear()
        self.scores_tab.load(scores_file, remove_columns=hide_scores_columns)
        self.tiers_tab.load(tiers_file, remove_columns=hide_ranks_columns)

    def load(self):
        if self.any_dirty():
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Save before loading?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
            if reply == QMessageBox.Save:
                if not self.save_all_files(): return
            elif reply == QMessageBox.Cancel:
                return

        for suffix in self.editors.keys():
            self.editors[suffix].setPlainText("")
            self.mark_clean(suffix)

        category = self.category_input.text().strip()
        if not category:
            print("LOAD - NO CATEGORY")
            return

        for meta in self.config_files_meta:
            suffix, schema, is_mandatory = meta["suffix"], meta["schema"], meta["mandatory"]
            editor = self.editors[suffix]
            file_name = self.get_filename(category, suffix)

            if file_name.exists():
                try:
                    print(f"Loading {file_name}")
                    loader = ConfigLoader(schema)
                    loader.read(file_name)
                    content = file_name.read_text(encoding='utf-8')
                    editor.setPlainText(content)
                except Exception as e:
                    print(f"Error {e}")
                    QMessageBox.critical(
                        self, "Validation Error", f"File '{file_name}' is invalid:\n{e}"
                        )
                    # Load content anyway so user can fix it
                    editor.setPlainText(file_name.read_text(encoding='utf-8'))
            else:
                if is_mandatory:
                    editor.setPlainText(f"# MANDATORY FILE NOT FOUND.")
                else:
                    editor.setPlainText(f"# Optional file not found.")

            self.mark_clean(suffix)

        try:
            self.refresh_data_viewers()
        except Exception as e:
            print(e)

    def save_all_files(self, prompt=True) -> bool:
        category = self.category_input.text().strip()
        region = self.region_input.text().strip()

        if not category:
            if prompt: QMessageBox.warning(self, "Input Error", "Cannot save without category.")
            return False

        any_file_saved = False

        for suffix, editor in self.editors.items():
            if self.get_dirty(suffix):
                file_name = self.get_filename(category, suffix)
                content = editor.toPlainText()
                meta = next(m for m in self.config_files_meta if m['suffix'] == suffix)
                schema = meta['schema']
                try:
                    data = yaml.safe_load(content)
                    v = Validator(schema)
                    if not v.validate(data):
                        raise ValueError(f"Schema validation failed:\n{yaml.dump(v.errors)}")
                except (yaml.YAMLError, ValueError) as e:
                    if prompt: QMessageBox.critical(
                        self, "Validation Error", f"Cannot save '{file_name}'.\n\n{e}"
                    )
                    return False
                try:
                    file_name.write_text(content, encoding='utf-8')
                    self.mark_clean(suffix)
                    any_file_saved = True # Mark that a save occurred
                except Exception as e:
                    if prompt: QMessageBox.critical(
                        self, "File Write Error", f"Could not save '{file_name}':\n{e}"
                    )
                    return False

        # If any file was successfully saved, touch the dependency  file.
        if any_file_saved:
            try:
                # This  file now represents the "last saved" time for this category's config
                marker_file = Path( f"build/{region}/interim/{region}_{category}_features.csv")
                marker_file.touch()
                print(f"--- Touched dependency: {marker_file} ---")
            except Exception as e:
                if prompt: QMessageBox.critical(self, "Marker File Error", f"Could not touch dependency marker file:\n{e}")

        return True


    def closeEvent(self, event: QCloseEvent):
        if self.controller.is_running():
            QMessageBox.warning(self, "Build in Progress", "Please wait for build to complete.")
            event.ignore();
            return
        if self.any_dirty():
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
            if reply == QMessageBox.Save:
                if not self.save_all_files():
                    event.ignore()
                else:
                    event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def start_profile_build(self):
        category, region = self.category_input.text().strip(), self.region_input.text().strip()
        if not region or not category:
            QMessageBox.warning(self, "Input Error", "Provide a valid Category and Region.")
            return

        self.editor_tabs.setCurrentWidget(self.runner_widget)

        # 1. Construct the hypothetical profile name
        profile_name = f"{region}_{category}"

        # 2. Check if it exists in the config file
        if self.controller.has_profile(profile_name):
            print(f"ℹ️ Using profile '{profile_name}'. ")
            # Use Profile mode (variables are defined inside the profile)
            self._execute_build(BuildWorker, profile_name=profile_name, cli_vars={})
        else:
            print(f"ℹ️ Using SEGMENT:{region} CATEGORY:{category}.")
            # Use Variable mode
            cli_vars = {
                "SEGMENT": region,
                "CATEGORY": category
            }
            # We pass empty profile_name to indicate generic run
            self._execute_build(BuildWorker, profile_name="", cli_vars=cli_vars)

    def _execute_build(self, worker_class, cli_vars=None, **kwargs):
        """
        Helper to clear console and start the build process.
        """
        # Ensure cli_vars is a dict (default to empty if None)
        if cli_vars is None:
            cli_vars = {}

        self.console_output.clear()

        # Pass cli_vars explicitly, and expand the rest of kwargs (like profile_name)
        self.controller.start_build(worker_class, cli_vars=cli_vars, **kwargs)

    def on_build_started(self):
        self._set_ui_enabled(False)

    def on_build_finished(self):
        self._set_ui_enabled(True)

    def on_build_error(self, error_message: str):
        QMessageBox.critical(self, "Build Failed", error_message)

    def update_console(self, text: str):
        self.console_output.moveCursor(QTextCursor.End)
        self.console_output.insertPlainText(text + "\n")

    def _set_ui_enabled(self, enabled: bool):
        self.run_profile_button.setEnabled(enabled)
        self.category_input.setEnabled(enabled)
        self.load_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.new_button.setEnabled(enabled) # Disable New button during build


if __name__ == "__main__":
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(description="Importance Ranking Editor")
    parser.add_argument(
        "config",        nargs='?',  default="default", help="Name of the LiteBuild config file (e.g., 'LB_lite_build.yml')."
        )

    # Argument to specify text scoring files
    parser.add_argument(
        "--text-scores",
        nargs='*', # 0 or more arguments
        default=["item_name", "sub_category"], # Default to the  hardcoded values
        help="Space-separated list of suffixes for text weight files (e.g., 'name description')."
    )
    args = parser.parse_args()

    window = ImportanceRank(args.config, args.text_scores)
    window.resize(1200, 900)  # Increased height for the new panel
    window.show()
    sys.exit(app.exec())
