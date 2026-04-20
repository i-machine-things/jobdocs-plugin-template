"""
Plugin Template Module — External JobDocs Plugin

This is the starting point for a new JobDocs external plugin.

QUICK START
-----------
1. Copy this entire directory and rename it to your plugin name
   (e.g. jobdocs-my-feature)
2. Rename the class below from TemplateModule to something descriptive
3. Update get_name(), get_order(), and get_description()
4. Replace the placeholder UI and methods with your functionality
5. Drop (or symlink) the folder into the JobDocs plugins directory

EXTERNAL vs INTERNAL PLUGINS
-----------------------------
External plugins live *outside* the JobDocs install directory and are
loaded from the filesystem at runtime — even in the packaged .exe build.
This means you never need to recompile or rebuild JobDocs to ship a plugin.

Key difference from internal modules:
  - UI path uses  Path(__file__).parent  (not sys._MEIPASS)
  - Settings are stored via app_context.get_setting() / set_setting()
  - Provide your own config UI if the user needs to set a folder path

DEPLOYMENT
----------
  plugins_dir/
  └── your-plugin-name/      ← this directory
      ├── __init__.py
      ├── module.py
      ├── requirements.txt
      └── ui/
          └── plugin_tab.ui

Set plugins_dir in JobDocs → Settings → Plugins directory.
"""

import os
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QFileDialog, QAbstractItemView
)
from PyQt6 import uic

from core.base_module import BaseModule
from shared.utils import open_folder, sanitize_filename  # noqa: F401  # remove unused imports


class TemplateModule(BaseModule):
    """
    Template external plugin module.

    Replace this docstring and class name with your plugin's purpose.
    """

    def __init__(self):
        super().__init__()
        self._widget = None

        # ── Widget references ──────────────────────────────────────────
        # Declare every widget ref you'll use from the .ui file here so
        # the type checker knows they exist before _create_widget runs.
        self.dir_edit = None          # folder config bar
        self.status_label = None

        # ── State ──────────────────────────────────────────────────────
        self.pending_files: List[str] = []

    # ══════════════════════════════════════════════════════════════════
    # REQUIRED — implement these three methods
    # ══════════════════════════════════════════════════════════════════

    def get_name(self) -> str:
        """Tab label shown in JobDocs."""
        return "My Plugin"

    def get_order(self) -> int:
        """
        Tab position — lower numbers appear further left.

        Built-in tab order for reference:
            10  Quote       50  Search
            20  Job         60  Import BP
            40  Bulk        70  History
        Use 100+ for external plugins to stay out of the way.
        """
        return 100

    def initialize(self, app_context):
        """Called once after the plugin is loaded, before the widget is created."""
        super().initialize(app_context)
        self.log_message(f"{self.get_name()} plugin initialized")

    def get_widget(self) -> QWidget:
        """Return (and lazily create) the tab widget."""
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    # ══════════════════════════════════════════════════════════════════
    # OPTIONAL
    # ══════════════════════════════════════════════════════════════════

    def is_experimental(self) -> bool:
        """
        Return True to hide this plugin unless the user enables
        experimental features in JobDocs settings.
        """
        return False

    def cleanup(self):
        """Called when JobDocs closes. Release resources here."""
        self.pending_files.clear()

    # ══════════════════════════════════════════════════════════════════
    # UI CREATION — replace with your own widget
    # ══════════════════════════════════════════════════════════════════

    def _get_ui_path(self) -> Path:
        """
        Resolve the .ui file path relative to this module file.

        External plugins must use Path(__file__).parent — NOT sys._MEIPASS,
        which only exists inside the bundled JobDocs executable.
        """
        ui_file = Path(__file__).parent / 'ui' / 'plugin_tab.ui'
        if not ui_file.exists():
            raise FileNotFoundError(f"UI file not found: {ui_file}")
        return ui_file

    def _create_widget(self) -> QWidget:
        """Build the tab widget from the .ui file and wire up signals."""
        widget = QWidget()
        uic.loadUi(str(self._get_ui_path()), widget)

        # ── Folder config bar ──────────────────────────────────────────
        # Plugins can't modify the main Settings dialog, so expose any
        # folder/path config directly in the plugin UI (see dir_edit +
        # browse_dir_btn in plugin_tab.ui).
        self.dir_edit = widget.dir_edit
        saved_dir = self.app_context.get_setting('my_plugin_dir', '')
        if saved_dir:
            self.dir_edit.setText(saved_dir)
        widget.browse_dir_btn.clicked.connect(self._browse_dir)

        # ── Status label ──────────────────────────────────────────────
        self.status_label = widget.status_label

        # ── Connect your signals here ─────────────────────────────────
        # Example:
        #   widget.my_button.clicked.connect(self._on_my_button)
        #   widget.my_list.itemSelectionChanged.connect(self._on_selection)

        # ── Enable drag and drop on the widget ────────────────────────
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = self._drag_enter
        widget.dropEvent = self._drop_event

        return widget

    # ══════════════════════════════════════════════════════════════════
    # FOLDER CONFIG — settings storage pattern for external plugins
    # ══════════════════════════════════════════════════════════════════

    def _browse_dir(self):
        """
        Let the user pick a working folder and persist it to JobDocs settings.

        Replace 'my_plugin_dir' with a unique settings key for your plugin.
        """
        current = self.app_context.get_setting('my_plugin_dir', '')
        chosen = QFileDialog.getExistingDirectory(
            self._widget, "Select Folder", current or ""
        )
        if chosen:
            self.dir_edit.setText(chosen)
            self.app_context.set_setting('my_plugin_dir', chosen)
            self.app_context.save_settings()
            self.log_message(f"{self.get_name()} folder set: {chosen}")

    def _get_working_dir(self) -> Path | None:
        """
        Retrieve and validate the configured working directory.
        Creates it if it doesn't exist yet.
        Returns None (with an error dialog) if not configured.
        """
        dir_path = self.app_context.get_setting('my_plugin_dir', '')
        if not dir_path:
            self.show_error(
                "No Folder Set",
                "Please use the Browse button to choose a working folder."
            )
            return None
        p = Path(dir_path)
        if not p.exists():
            try:
                p.mkdir(parents=True)
            except OSError as e:
                self.show_error("Directory Error", f"Could not create folder:\n{e}")
                return None
        return p

    # ══════════════════════════════════════════════════════════════════
    # DRAG AND DROP
    # ══════════════════════════════════════════════════════════════════

    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _drop_event(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and os.path.isfile(file_path):
                if file_path not in self.pending_files:
                    self.pending_files.append(file_path)
                    # TODO: add to your file list widget
                    # self.files_list.addItem(os.path.basename(file_path))

    # ══════════════════════════════════════════════════════════════════
    # YOUR PLUGIN LOGIC GOES HERE
    # ══════════════════════════════════════════════════════════════════

    # Example method skeleton:
    #
    # def _do_something(self):
    #     working_dir = self._get_working_dir()
    #     if working_dir is None:
    #         return
    #
    #     try:
    #         # ... your logic ...
    #         self.status_label.setText("Done")
    #         self.status_label.setStyleSheet("color: green;")
    #     except OSError as e:
    #         self.show_error("Error", str(e))
