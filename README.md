# Git Worktree Tool

[![CI/CD Status](https://github.com/jlothian/worktree-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/jlothian/worktree-tool/actions)

A CLI tool for managing Git worktrees using a bare repository structure.

## Setup

1. **Install**:
   ```bash
   pipx install git+https://github.com/jlothian/worktree-tool.git
   ```
   Or from a local clone:
   ```bash
   pip install .
   ```

2. **Add shell wrapper & autocompletions** (add this to `~/.zshrc` or `~/.bashrc`):
   ```bash
   eval "$(gwt-cli init-shell)"
   ```
   *(For local development, you can instead source `source aliases.sh`)*

## Commands

### `wt init <url> [directory] [--main <branch>]`
Clones the repository as a bare repository into `<directory>/.bare`, sets up the main worktree (checking out the remote HEAD branch or the custom branch name if `--main` is specified), and configures upstream tracking.

### `wt new <branch>`
Fetches remote updates, updates `main`, and branches off it. Slashes in the branch name are converted to dashes in the directory name. Automatically `cd`s the shell into the new directory.

### `wt clean` (or `cleanup`)
Scans worktrees merged into `main` and deletes them. Automatically detects and cleans up squash-merged branches by comparing tree hashes against recent commits on the main branch. If a merged worktree has dirty/untracked files, surfaces the files and prompts before deleting.

### `wt list`
Displays a status table of all active worktrees, branches, merge status, and clean/dirty status. Run `wt list -i` or `wt list --interactive` to launch an interactive selection picker (powered by `fzf`) that previews and automatically changes directory (`cd`) to the selected worktree. (Requires `fzf` installed).

### `wt go [worktree]`
Navigates to an existing worktree. If a worktree name (directory name or branch name) is provided, it outputs the path to that worktree. If no name is provided, it launches an interactive `fzf` picker to select a worktree and outputs its path. The shell wrapper automatically `cd`s to the selected worktree. (Interactive mode requires `fzf` installed).

### `wt delete [worktree]` (or `remove`, `rm` / option `-f`, `--force`)
Deletes a specific worktree and its associated branch. If no name is provided, launches an interactive `fzf` selection picker (excluding the main and active worktrees). Includes safety prompts if the worktree has uncommitted changes or if its branch is not merged into `main`. The `-f` or `--force` flag bypasses all prompts.

### `wt repair`
Fixes broken worktree pointer paths if the project directory is relocated.

### `wt --version` (or `-v`)
Prints the current version of the tool.

## Running Tests

Run the automated integration tests:

```bash
python3 -m unittest discover -s tests
```