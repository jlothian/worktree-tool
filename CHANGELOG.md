# CHANGELOG


## v0.3.1 (2026-07-19)

### Bug Fixes

- Add go command to shell wrapper cd check and remove redundant li…
  ([#6](https://github.com/jlothian/worktree-tool/pull/6),
  [`2d8fbfc`](https://github.com/jlothian/worktree-tool/commit/2d8fbfc7c0fdf7d9ba1a5e3cbd49fd1de1dbce00))


## v0.3.0 (2026-07-19)

### Features

- Support detecting and cleaning up squash-merged branches
  ([#5](https://github.com/jlothian/worktree-tool/pull/5),
  [`91b9240`](https://github.com/jlothian/worktree-tool/commit/91b92407ae7663dba7ceb01b3716b0214a19ea97))

feat: support detecting and cleaning up squash-merged branches

### Refactoring

- Modularize codebase and simplify subcommand routing
  ([#4](https://github.com/jlothian/worktree-tool/pull/4),
  [`87cdec5`](https://github.com/jlothian/worktree-tool/commit/87cdec5bcbb5fc6a7eb32f4939a77dcf77ffe55e))

## Description Brief description of the changes introduced by this Pull Request. Focus on the
  motivation, implementation details, and any architectural choices.

## Related Issues Fixes # (issue number)

## Type of Change - [ ] Bug fix (non-breaking change which fixes an issue) - [ x] New feature
  (non-breaking change which adds functionality) - [ ] Breaking change (fix or feature that would
  cause existing functionality to not work as expected) - [ ] Documentation update

## How Has This Been Tested? Please describe the tests that you ran to verify your changes (e.g.
  automated tests, manual testing walkthroughs).

- [ ] Run `python3 -m unittest discover -s tests` (All tests green) - [ ] Run `ruff check` / `ruff
  format --check` - [ ] Run `shellcheck aliases.sh` (if applicable)

## Checklist: - [ ] My code follows the style guidelines of this project - [ ] I have performed a
  self-review of my own code - [ ] I have commented my code, particularly in hard-to-understand
  areas - [ ] I have made corresponding changes to the documentation - [ ] My changes generate no
  new warnings


## v0.2.0 (2026-07-19)

### Features

- Add wt go command for worktree navigation ([#3](https://github.com/jlothian/worktree-tool/pull/3),
  [`86c1bf9`](https://github.com/jlothian/worktree-tool/commit/86c1bf9269a9132854132068e01c1d34d1377557))

feat: add wt go command for worktree navigation

Add go command to navigate to existing worktrees by name or interactive fzf picker. Shell wrapper
  automatically cd's to selected worktree.


## v0.1.5 (2026-07-19)

### Bug Fixes

- Rename shell wrapper alias from gwt to wt to prevent oh-my-zsh collision
  ([`b771fae`](https://github.com/jlothian/worktree-tool/commit/b771faed4a75cafe7e9af477cee3ef91c70e4646))


## v0.1.4 (2026-07-19)

### Bug Fixes

- Change wrapper syntax to function gwt to avoid parse-time alias expansion error
  ([`b244899`](https://github.com/jlothian/worktree-tool/commit/b24489996662d92a936748fe98a981756f72ee30))


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
