# CHANGELOG


## v0.1.3 (2026-07-19)

### Bug Fixes

- Add unalias gwt guard to init-shell outputs
  ([`a4a1ec7`](https://github.com/jlothian/worktree-tool/commit/a4a1ec70682976c352a10818a2845a5b6a082e2d))


## v0.1.2 (2026-07-19)

### Bug Fixes

- Switch to console_scripts entry point to fix spaces in pipx venv paths
  ([`3a8008a`](https://github.com/jlothian/worktree-tool/commit/3a8008a377f1982dabe438eca7c8a7d7d0326b67))


## v0.1.1 (2026-07-19)

### Bug Fixes

- Use semver regex in version test instead of hardcoded string
  ([`1d0c1c4`](https://github.com/jlothian/worktree-tool/commit/1d0c1c499edc4c331ee5225923df1dbc0597f634))

### Documentation

- Add pipx install instructions to README
  ([`fd2403f`](https://github.com/jlothian/worktree-tool/commit/fd2403f121b04cdb8729c3b2971765c2c1dc5dff))


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
