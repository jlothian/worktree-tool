# Git Worktree Tool

A CLI tool for managing Git worktrees using a bare repository structure.

## Setup

Source the environment script to add the CLI to your path and enable automatic directory changing (`cd`) on worktree creation:

```bash
source aliases.sh
```

## Commands

### `gwt init <url> [directory]`
Clones the repository as a bare repository into `<directory>/.bare`, sets up the main worktree, and configures upstream tracking.

### `gwt new <branch>`
Fetches remote updates, updates `main`, and branches off it. Slashes in the branch name are converted to dashes in the directory name. Automatically `cd`s the shell into the new directory.

### `gwt clean` (or `cleanup`)
Scans worktrees merged into `main` and deletes them. If a merged worktree has dirty/untracked files, surfaces the files and prompts before deleting.

### `gwt list`
Displays a status table of all active worktrees, branches, merge status, and clean/dirty status.

### `gwt repair`
Fixes broken worktree pointer paths if the project directory is relocated.

## Running Tests

Run the automated integration tests:

```bash
python3 -m unittest discover -s tests
```