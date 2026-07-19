# Getting Started Guide

This document describes how to set up, configure, and use the Git Worktree Management Tool (`gwt`).

---

## 1. Setup and Installation

### Prerequisites
* Git installed on your system.
* Python 3.9+ installed.

### Loading the Shell Wrapper
To use the `gwt` CLI and enable automatic directory changes (`cd`) on worktree creation or initialization, you must source the environment script in your shell:

```bash
source /path/to/worktree-tool/aliases.sh
```

To make this persistent, add the source command to your shell configuration profile (e.g. `~/.zshrc` or `~/.bashrc`):

```bash
# Add to ~/.zshrc or ~/.bashrc
source /Users/jlothian/src/worktree-tool/aliases.sh
```

---

## 2. Command Reference

### `gwt init <url> [directory]`
Clones the remote repository as a bare repository, creates the main worktree, and configures the tracking branch.
* **Arguments**:
  * `<url>`: Git clone URL (SSH or HTTPS).
  * `[directory]`: Optional target directory name (defaults to repository name).
* **Behavior**:
  - Clones repository bare to `.bare/`.
  - Creates `.git` file pointer in the directory root.
  - Automatically fetches remote branches and creates the default branch worktree (e.g., `main/` or `master/`).
  - Sets up the `main` branch to track the upstream `origin/main` branch.
  - **CD Behavior**: Automatically changes your shell directory into the initialized project root folder.

### `gwt new <branch_name>`
Creates a new worktree branched off the updated main branch.
* **Arguments**:
  * `<branch_name>`: Name of the new branch to create (e.g., `feature/login`).
* **Behavior**:
  - Pulls updates (`--ff-only`) in the `main` worktree to ensure the new worktree branches off up-to-date code.
  - Replaces all slashes (`/`) in `<branch_name>` with dashes (`-`) to construct the directory name.
  - Checks out the branch into the flat sibling directory (e.g. `feature-login/`).
  - **CD Behavior**: Automatically changes your shell directory into the new worktree folder.

### `gwt list`
Displays a status table of all active worktrees in the current project namespace.
* **Outputs**:
  * `WORKTREE`: The directory name.
  * `BRANCH`: The Git branch currently checked out.
  * `MERGE STATUS`: State of the branch relative to main (`Main`, `Merged`, or `Unmerged`).
  * `FILE STATUS`: State of uncommitted changes (`Clean`, `Dirty (X staged)`, `Dirty (Y unstaged)`, or `Dirty (X staged, Y unstaged)`).

### `gwt clean` (or `cleanup`)
Scans for worktree branches that have been merged into `main` and deletes them.
* **Behavior**:
  - Automatically deletes merged worktrees and their local branches if they are clean.
  - If a merged worktree has uncommitted or staged changes, it surfaces the files under `Staged changes:` and `Unstaged changes:` headers and prompts the user for confirmation.
  - Skips deleting the current working directory of your terminal to avoid breaking your shell path.

### `gwt repair`
Fixes broken worktree pointer paths if you relocate the parent project directory.

---

## 3. Shell Autocompletion

Autocompletion is automatically registered when you source `aliases.sh`.

* **Zsh Autocomplete**: Supports subcommand suggestions (`init`, `new`, `clean`, etc.) and dynamically suggestions for remote/local branches when executing `gwt new <tab>`.
* **Bash Autocomplete**: Supports subcommand completions and dynamic branch completion.

---

## 4. Typical Workflow Example

```bash
# 1. Initialize a new project from a remote repository (CDs into my-project)
$ gwt init git@github.com:user/my-project.git

# 2. View current worktrees (should show .bare and main)
$ gwt list

# 3. Create a feature worktree (automatically branches off main and CDs in)
$ gwt new feature/analytics
Updating main branch 'main' in 'my-project/main'...
Creating new worktree for branch 'feature/analytics' in 'my-project/feature-analytics'...

# 4. Make code edits, stage, and check status
$ touch tracking.js && git add tracking.js
$ gwt list
WORKTREE             BRANCH               MERGE STATUS    FILE STATUS
--------------------------------------------------------------------------------
.bare (repo)         -                    -               -
feature-analytics    feature/analytics    Unmerged        Dirty (1 staged)
main                 main                 Main            Clean

# 5. Commit, push, merge, and clean up
$ git commit -m "add tracking" && git push origin feature/analytics
$ cd ../main && git merge feature/analytics
$ gwt clean
Worktree 'feature/analytics' at 'my-project/feature-analytics' is merged and clean. Deleting...
Successfully deleted worktree and branch 'feature/analytics'.
```
