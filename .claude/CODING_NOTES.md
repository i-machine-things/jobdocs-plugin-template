# Coding Best Practices & Reminders

> **Style rule:** Notes must be clear and concise — 300 characters or less each. Group by topic, not by date. Whenever a PR review (CodeRabbit or human) catches a mistake, add or amend a note here right away so it isn't repeated.

## Exception Handling

**Avoid broad `except Exception` in hooks.** It swallows unexpected errors silently — catch specific types instead (e.g. `OSError`/`subprocess.SubprocessError` for subprocess calls, `json.JSONDecodeError` for stdin parsing).

## Subprocess / Git Usage

**Resolve the git executable, don't hardcode `"git"`.** A literal `"git"` string can fail if git isn't on `PATH` in some environments — resolve it with `shutil.which("git")` and bail early if not found.

## Shell Scripting

**Guard `git describe --tags --abbrev=0` for tagless repos.** It errors on a fresh repo with no tags, breaking version-bump scripts. Capture into a variable with `2>/dev/null` and fall back to `git log <branch> --oneline` when empty.
