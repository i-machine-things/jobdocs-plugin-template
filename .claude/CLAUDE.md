# Auto Version Control Rules - Claude AI

You are a senior software developer. These rules override your default behavior. Follow them on every action without being asked.

## Rule 0: Always Read First

Before taking any action on this project — including edits, commits, or file creation:

1. Read `.claude/CLAUDE.md` and `.claude/S&P.md`.
2. Run `gh pr list` — if a PR exists for the current branch, run `gh pr view <number> --comments` and read **all comments** (CodeRabbit and human) before proceeding.
3. Run `gh issue list` — check for open issues relevant to the current work.
4. Do not make any edits until all outstanding findings and review comments are addressed or acknowledged.

No exceptions.

### S&P.md is for programming notes only

`.claude/S&P.md` is a standards and practices log — a reference for coding patterns, past findings, and decisions. It is **not** the source of truth for PR review status.

- To check if a PR review is complete or paused: **always use `gh pr view <number> --comments`**.
- CodeRabbit may auto-pause reviews after rapid commits — check for `review paused` in the summary comment.
- If paused, trigger a new run with: `gh pr comment <number> --body "@coderabbitai review"`
- If CR hits a rate limit (`Rate limit exceeded`), run `date -u` to get the current UTC time, calculate the UTC timestamp when the window clears, and state it explicitly (e.g. "clears at 05:04 UTC"). Re-trigger on the first user interaction at least 5 minutes after that time to allow for clock drift.
- **Sequential PR workflow:** Open one PR, wait for CR to finish and address all findings, merge, then open the next. Do not trigger multiple concurrent CodeRabbit reviews.

## Trigger Prompt

When the user says **"run auto version control"** (or any close variation like "run avc", "auto version control", "start version control"), immediately run the full assessment:

1. Run `git status`, `git branch`, and `git log --oneline -10`
2. Run `gh issue list` and report any open issues
3. Report the current state: branch, uncommitted changes, recent commits, version tags
4. Flag any issues: working on main, uncommitted changes, missing .gitignore, no tags
5. Recommend next actions

This is how the user explicitly asks you to check in on the project.

## Rule 1: Git Is Mandatory

- If the project is not a git repository, run `git init` and create an initial commit before doing anything else.
- Never work directly on `master`. Always create a feature branch first then merge into `master`.
- Branch naming: `feat/description`, `fix/description`, `refactor/description`, `docs/description`, `chore/description`.
- If you are on `master` when you start, create and switch to a feature branch immediately.

## Rule 2: Conventional Commits

Every commit message must follow this format:

```
type: short description (imperative, lowercase, no period)
```

Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `style`, `perf`, `chore`, `ci`, `build`.

Examples:
- `feat: add user authentication endpoint`
- `fix: prevent null pointer in payment handler`
- `refactor: extract validation logic into shared module`
- `docs: add API usage examples to README`

Rules:
- One logical change per commit. Do not bundle unrelated changes.
- Commit after every meaningful change, not at the end of a long session.
- If a commit touches more than 3 unrelated things, you are bundling too much. Split it.
- If a new feature is added or changed, update the top-level README.md before committing.
- After every commit, check if a PR exists for the current branch (`gh pr list --head <branch>`). If none exists, open one immediately via `gh pr create`. Never leave a commit on a feature branch without an open PR.

## Rule 3: Fork From the Template — Backport Template Changes

### New plugins must be forked from this repository

Every new JobDocs external plugin starts as a fork of `jobdocs-plugin-template`.
Do **not** create a plugin repo from scratch.

- Fork `jobdocs-plugin-template` on GitHub, then rename the fork to your plugin name.
- Rename the class in `module.py` and update `get_name()`, `get_order()`, and the settings key.
- All `.claude/` files come pre-configured — do not strip or replace them.

### Template file changes must be PR'd back upstream

The following files are **template files** — shared infrastructure owned by `jobdocs-plugin-template`:

```
.claude/CLAUDE.md
.claude/S&P.md               (format/structure only — not plugin-specific content)
.claude/settings.json
.claude/hooks/pre_commit_sp_check.py
module.py                    (scaffold structure, not plugin-specific logic)
ui/plugin_tab.ui             (folder config bar pattern, base layout)
requirements.txt             (format/comments only)
README.md
```

If you improve or fix any of these in a plugin repo, open a PR to `jobdocs-plugin-template`
with the change **before** (or alongside) merging it in the plugin repo. This keeps the
template current so future forks benefit from the fix.

Plugin-specific code (your own methods, UI widgets, settings keys, S&P entries) is **not**
backported — only changes that would benefit every plugin.

---

## Rule 4 (was Rule 3): This Is an External Plugin — Not Part of JobDocs Core

This repository is a standalone external plugin. It is loaded at runtime from the
JobDocs `plugins_dir` setting and must never be merged into the main JobDocs repo.

- Do **not** add this plugin's code to the `JobDocs/modules/` directory.
- Keep all UI path resolution relative to `Path(__file__).parent` — never use `sys._MEIPASS`.
- Plugin-specific settings must be surfaced through the plugin's own UI (Browse button pattern).
- Dependencies go in `requirements.txt`; JobDocs installs them automatically on first load.

---

## Rule 5: Semantic Versioning

Update GitHub releases on minor version changes to the production branch.

Tag releases using `vMAJOR.MINOR.PATCH`:
- **MAJOR** — breaking changes (removed features, changed APIs, incompatible updates)
- **MINOR** — new features that do not break existing functionality
- **PATCH** — bug fixes, typo corrections, minor improvements

**To cut a release:**
```bash
git tag v1.2.3
git push origin v1.2.3
```

**Note:** Only tag from `master`.

### Automatic Version Bump Triggers

After every merge to `master`, count commits since the last `v*` tag:

```bash
last_tag=$(git describe --tags --abbrev=0 2>/dev/null)
if [ -n "$last_tag" ]; then
  git log "$last_tag"..master --oneline
else
  git log master --oneline
fi
```

Count by type:
- Lines starting with `feat:` → feature count
- Lines starting with `fix:` → fix count

**Thresholds:**
- **5 or more `feat:` commits** → bump MINOR, reset PATCH to 0, tag and push
- **5 or more `fix:` commits** → bump PATCH, tag and push

If both thresholds are met simultaneously, bump MINOR (takes precedence).

Check this threshold after every merge to master. Do not wait for the user to ask.

## Rule 6: Pull Request Reviews

When a pull request is open or being prepared:

- Always open PRs via `gh pr create` — never merge directly to `master` without a PR.
- After any review is submitted (CodeRabbit **or human**), read all comments before making any further changes.
- For each finding, regardless of source:
  1. If it matches an existing `.claude/S&P.md` entry — fix it immediately and reference the S&P entry in the commit message.
  2. If it is a new pattern — fix it, then append it to `.claude/S&P.md` in the standard format before committing.
- Do not dismiss or ignore nitpicks — log them to `.claude/S&P.md` even if not immediately actionable.
- Only merge a PR after all blocking comments are resolved.

### S&P.md Entry Format

```markdown
## YYYY-MM-DD — `path/to/file.py` (short description)

**Review:** WHAT CODERABBIT FLAGGED
**Result:** outcome / resolution

### Findings

1. **Title**
   - Detail
   - Fix applied
```
