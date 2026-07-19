# Architecture & Design Decisions

This document outlines the core technical and architectural design decisions made during the development of the Git Worktree Management Tool (`gwt`).

---

## 1. Bare Repository Layout (`.bare`)

In traditional Git clone setups, one directory functions as the "primary" repository containing the `.git` folder, and all other worktrees are "linked" to it. If the primary directory is deleted, relocated, or corrupted, the link breaks for all other worktrees.

To resolve this, we adopt the **Bare Repository Convention**:
* **Shared Object Store**: The repository is cloned as a bare repository (`git clone --bare`) into a hidden directory called `.bare`.
* **Equal Peers**: Because a bare repository has no working tree of its own, all checking-out operations are forced into dedicated worktree directories (like `main`, `feature-branch`). Every worktree functions as an equal sibling, making it safe to delete any branch directory without affecting others.
* **Root Repository Pointer**: We create a `.git` file in the project root containing:
  ```
  gitdir: ./.bare
  ```
  This allows standard Git commands (like `git worktree add`, `git fetch`, etc.) executed from the project root directory to automatically find and interact with the bare repository.

---

## 2. Directory Name Mapping (Replacing Slashes)

Git branch naming conventions frequently encourage nesting (e.g. `feature/login` or `bugfix/issue-123`). However, having directories nested inside folders in the workspace can complicate file navigation, script execution, and IDE workspaces.

* **Decision**: We replace all slashes (`/`) in the branch name with dashes (`-`) for the worktree directory name.
* **Result**: A branch named `feature/login` is created in a sibling directory named `feature-login`, ensuring a flat structure in the workspace.

---

## 3. Staged Changes Safety Checks

When a worktree branch has been merged into the `main` branch, native Git allows deleting it. However, if a developer made modifications and staged them in the index (`git add`) but never committed them, these files are not recorded in Git history. Using `git worktree remove --force` would silently and permanently destroy this uncommitted code.

* **Decision**: The `clean` command checks `git status --porcelain` before performing any cleanup. 
* **Index State Separation**: We parse the two-column status indicators to separate staged changes from unstaged or untracked changes.
* **Safety Prompt**: If there are staged changes, we block silent deletion, explicitly print the staged changes to `stderr`, and prompt the user:
  ```
  Worktree 'feature/login' at '...' is merged but NOT clean.
  Staged changes:
    A  src/login.js

  Unstaged changes:
    ?? debug.log

  Delete these files and the worktree 'feature/login'? [y/N]:
  ```
  This guarantees that work-in-progress code is never accidentally deleted.

---

## 4. Shell Integration & Navigation Wrapper

Operating system security prevents compiled binaries or child scripts (like Python or standard Bash scripts run in a child process) from changing the working directory (`cd`) of the parent shell.

* **Decision**: We use an environment script `aliases.sh` that is sourced by the user's shell.
* **Wrapper Interception**: The sourced wrapper function `gwt()` intercepts commands like `new` and `init`. It executes the underlying Python CLI (`gwt-cli`), captures its successful directory outputs, and triggers `cd` in the parent shell.
* **Safe Autocompletion**: The script registers completion scripts dynamically for Zsh and Bash, using guards to check for command availability (like Zsh's `compdef`) to prevent errors in non-interactive shell scripts.
