# CHANGELOG


## v0.1.0 (2026-07-19)

### Features

- Prepare repository for open source release (LICENSE, pyproject.toml p…
  ([#1](https://github.com/jlothian/worktree-tool/pull/1),
  [`5eb3a5d`](https://github.com/jlothian/worktree-tool/commit/5eb3a5d36d11a6fdc4d5d3bac0509d31f373134d))

### Summary Prepares the repository for open-source publication and automates releases using
  `python-semantic-release`.

### Changes * **Packaging & License**: Added MIT `LICENSE`, `pyproject.toml` configuration, and
  `CONTRIBUTING.md` guide. * **CLI Updates**: Added `gwt-cli init-shell` command to dynamically
  generate shell wrappers, support for `--main <branch>` during `init`, and a `--version` flag. *
  **Release Automation**: Added GitHub Actions workflow to auto-tag releases and publish builds on
  push/merge to `main`. * **Namespace Protection**: Prefixed and unset shell variables in
  `aliases.sh` to prevent terminal environment pollution. * **Community**: Added issue and PR
  templates.

All 11 tests, formatting checks, and Shellcheck lints are green.
