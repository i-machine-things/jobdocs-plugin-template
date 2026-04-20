# JobDocs Plugin Template

Starting point for a new external JobDocs plugin.

## Usage

1. **Copy this directory** and rename it to your plugin name (`jobdocs-my-feature`)
2. **Rename the class** in `module.py` from `TemplateModule` to something descriptive
3. **Update** `get_name()`, `get_order()`, and the settings key `my_plugin_dir`
4. **Build your UI** — edit `ui/plugin_tab.ui` in Qt Designer, or replace it entirely
5. **Add dependencies** to `requirements.txt` (JobDocs installs them on first load)
6. **Drop the folder** into the JobDocs `plugins_dir`

## Structure

```
jobdocs-my-feature/
├── .claude/
│   ├── CLAUDE.md                  auto version control rules
│   ├── S&P.md                     CodeRabbit review log (start empty)
│   ├── settings.json              Claude Code hook config
│   └── hooks/
│       └── pre_commit_sp_check.py pre-commit S&P pattern checker
├── ui/
│   └── plugin_tab.ui              Qt Designer UI file
├── __init__.py
├── module.py                      your plugin class (inherits BaseModule)
├── requirements.txt               extra pip dependencies
└── README.md
```

## Key Patterns

### UI path resolution

External plugins must resolve UI files relative to themselves:

```python
def _get_ui_path(self) -> Path:
    return Path(__file__).parent / 'ui' / 'plugin_tab.ui'
```

Never use `sys._MEIPASS` — that only exists inside the bundled JobDocs executable.

### Settings storage

Plugins can't modify the JobDocs Settings dialog. Expose configuration directly
in your plugin UI using the folder config bar pattern:

```python
# Save
self.app_context.set_setting('my_plugin_dir', chosen_path)
self.app_context.save_settings()

# Retrieve
saved = self.app_context.get_setting('my_plugin_dir', '')
```

Use a unique settings key (prefix with your plugin name to avoid collisions).

### app_context API

```python
# Settings
self.app_context.get_setting(key, default)
self.app_context.set_setting(key, value)
self.app_context.save_settings()

# History
self.app_context.add_to_history('my_type', {...})
self.app_context.save_history()

# Customers / directories
self.app_context.get_customer_list()
self.app_context.get_directories(is_itar=False)   # -> (bp_dir, cf_dir)

# Dialogs / logging
self.show_error(title, message)
self.show_info(title, message)
self.log_message(message)
```

### Shared utilities

```python
from shared.utils import (
    open_folder,        # open path in OS file browser
    sanitize_filename,  # strip invalid path characters
    parse_job_numbers,  # '1-3,5' -> ['1','2','3','5']
    is_blueprint_file,  # check extension against blueprint list
    create_file_link,   # hard/sym link or copy
)
```

## Deployment

In JobDocs → Settings, set **Plugins directory** to the folder that *contains*
your plugin folder (not the plugin folder itself):

```
plugins_dir/
└── jobdocs-my-feature/   ← this is your plugin
    ├── module.py
    └── ...
```

JobDocs scans `plugins_dir` for subdirectories containing `module.py` and loads
them automatically — no restart required after the first load.

## Real examples

- [`jobdocs-report-fixer`](../jobdocs-report-fixer) — Excel report transformer
- [`jobdocs-training-docs`](../jobdocs-training-docs) — Training guide tracker
