# Architecture & Design Decisions

This document outlines the core technical and architectural design decisions made during the development of the Git Worktree Management Tool (`wt`).

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

## 3. Worktree Deletion Safety Checks (Uncommitted & Unmerged Commit Protection)

When a worktree branch has been merged into the `main` branch, native Git allows deleting it. However, if a developer made modifications and staged them in the index (`git add`) or left them unstaged but never committed them, these files are not recorded in Git history. Using `git worktree remove --force` would silently and permanently destroy this uncommitted code. 

Furthermore, deleting an unmerged branch results in permanent loss of its unique commits.

* **Decision**: The `clean` and `delete`/`remove`/`rm` commands check `git status --porcelain` before performing any cleanup or deletion.
* **Index State Separation**: We parse the two-column status indicators to separate staged changes from unstaged or untracked changes.
* **Safety Prompt**: If there are staged or unstaged changes, we block silent deletion, explicitly print the changes to `stderr`, and prompt the user:
  ```
  Worktree 'feature/login' at '...' has uncommitted changes.
  Staged changes:
    A  src/login.js

  Unstaged changes:
    ?? debug.log

  Delete anyway? [y/N]:
  ```
* **Merge Validation**: For the targeted `delete` subcommand, we also perform a merge check against the main branch. If the branch has commits not yet merged into `main`, we warn the user about the loss of commits and prompt for confirmation before deleting.
* **Bypass**: The `-f` or `--force` flag is provided to bypass these prompts for scripted environments or direct overrides.

---

## 4. Shell Integration & Navigation Wrapper

Operating system security prevents compiled binaries or child scripts (like Python or standard Bash scripts run in a child process) from changing the working directory (`cd`) of the parent shell.

* **Decision**: We use an environment script `aliases.sh` that is sourced by the user's shell.
* **Wrapper Interception**: The sourced wrapper function `wt()` intercepts commands like `new` and `init`. It executes the underlying Python CLI (`gwt-cli`), captures its successful directory outputs, and triggers `cd` in the parent shell.
* **Safe Autocompletion**: The script registers completion scripts dynamically for Zsh and Bash, using guards to check for command availability (like Zsh's `compdef`) to prevent errors in non-interactive shell scripts.

---

## 5. Squash Merge Detection

When developers squash-merge pull requests on platforms like GitHub, Git's commit history for the `main` branch does not include the original commits from the feature branch. A standard commit-ancestry check (such as `git merge-base --is-ancestor`) will report that the feature branch is unmerged, even though its files are fully incorporated.

* **Decision**: We implement a fallback tree-hash comparison.
* **Mechanism**:
  1. We retrieve the tree hash of the target branch's tip commit (`git rev-parse branch_ref^{tree}`).
  2. We retrieve the tree hashes of the last 100 commits in the main branch.
  3. If the target branch's tree hash matches any of those main branch tree hashes, we consider the branch merged.
* **Benefit**: This enables both `wt clean` and `wt delete` to correctly recognize squash-merged worktrees and clean them up automatically without warning about unmerged commits.

