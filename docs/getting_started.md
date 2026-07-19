# Getting Started Guide

This document describes how to set up, configure, and use the Git Worktree Management Tool (`wt`).

---

## 1. Setup and Installation

### Prerequisites
* Git installed on your system.
* Python 3.9+ installed.

### Loading the Shell Wrapper
To use the `wt` CLI and enable automatic directory changes (`cd`) on worktree creation or initialization, you must add the shell initialization to your profile:

```bash
# Add to ~/.zshrc or ~/.bashrc
eval "$(gwt-cli init-shell)"
```

*(For local development, you can instead source `source /path/to/worktree-tool/aliases.sh`)*

---

## 2. Command Reference

### `wt init <url> [directory] [--main <branch>]`
Clones the remote repository as a bare repository, creates the main worktree, and configures the tracking branch.
* **Arguments**:
  * `<url>`: Git clone URL (SSH or HTTPS).
  * `[directory]`: Optional target directory name (defaults to repository name).
  * `--main <branch>`: Optional custom main branch name to checkout (defaults to default branch of remote HEAD).
* **Behavior**:
  - Clones repository bare to `.bare/`.
  - Creates `.git` file pointer in the directory root.
  - Automatically fetches remote branches and creates the main branch worktree (e.g., `main/` or `master/`).
  - Sets up the `main` branch to track the upstream `origin/main` branch.
  - **CD Behavior**: Automatically changes your shell directory into the initialized project root folder.

### `wt new <branch_name>`
Creates a new worktree branched off the updated main branch.
* **Arguments**:
  * `<branch_name>`: Name of the new branch to create (e.g., `feature/login`).
* **Behavior**:
  - Pulls updates (`--ff-only`) in the `main` worktree to ensure the new worktree branches off up-to-date code.
  - Replaces all slashes (`/`) in `<branch_name>` with dashes (`-`) to construct the directory name.
  - Checks out the branch into the flat sibling directory (e.g. `feature-login/`).
  - **CD Behavior**: Automatically changes your shell directory into the new worktree folder.

### `wt list`
Displays a status table of all active worktrees in the current project namespace.
* **Arguments**:
  * `-i`, `--interactive`: Launches an interactive selection menu powered by `fzf`. Allows moving between worktrees using arrow keys, displays a live preview of the recent commits for the selected worktree, and changes the shell directory (`cd`) to it on `Enter`. (Requires `fzf` installed).
* **Outputs**:
  * `WORKTREE`: The directory name.
  * `BRANCH`: The Git branch currently checked out.
  * `MERGE STATUS`: State of the branch relative to main (`Main`, `Merged`, or `Unmerged`).
  * `FILE STATUS`: State of uncommitted changes (`Clean`, `Dirty (X staged)`, `Dirty (Y unstaged)`, or `Dirty (X staged, Y unstaged)`).

### `wt clean` (or `cleanup`)
Scans for worktree branches that have been merged into `main` and deletes them.
* **Behavior**:
  - Automatically deletes merged worktrees and their local branches if they are clean.
  - If a merged worktree has uncommitted or staged changes, it surfaces the files under `Staged changes:` and `Unstaged changes:` headers and prompts the user for confirmation.
  - Skips deleting the current working directory of your terminal to avoid breaking your shell path.

### `wt repair`
Fixes broken worktree pointer paths if you relocate the parent project directory.

### `wt --version` (or `-v`)
Prints the current version of the tool.

---

## 3. Shell Autocompletion

Autocompletion is automatically registered when you load `init-shell`.

* **Zsh Autocomplete**: Supports subcommand suggestions (`init`, `new`, `clean`, etc.) and dynamic suggestions for remote/local branches when executing `wt new <tab>`.
* **Bash Autocomplete**: Supports subcommand completions and dynamic branch completion.

---

## 4. Typical Workflow Example

```bash
# 1. Initialize a new project from a remote repository (CDs into my-project)
$ wt init git@github.com:user/my-project.git

# 2. View current worktrees (should show .bare and main)
$ wt list

# 3. Create a feature worktree (automatically branches off main and CDs in)
$ wt new feature/analytics
Updating main branch 'main' in 'my-project/main'...
Creating new worktree for branch 'feature/analytics' in 'my-project/feature-analytics'...

# 4. Make code edits, stage, and check status
$ touch tracking.js && git add tracking.js
$ wt list
WORKTREE             BRANCH               MERGE STATUS    FILE STATUS
--------------------------------------------------------------------------------
.bare (repo)         -                    -               -
feature-analytics    feature/analytics    Unmerged        Dirty (1 staged)
main                 main                 Main            Clean

# 5. Commit, push, merge, and clean up
$ git commit -m "add tracking" && git push origin feature/analytics
$ cd ../main && git merge feature/analytics
$ wt clean
Worktree 'feature/analytics' at 'my-project/feature-analytics' is merged and clean. Deleting...
Successfully deleted worktree and branch 'feature/analytics'.
```
