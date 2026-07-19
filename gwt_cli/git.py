import os
import sys
import subprocess


def run_git(args, cwd=None, capture_output=True, log_error=True):
    try:
        cmd = ["git"] + args
        res = subprocess.run(
            cmd, cwd=cwd, capture_output=capture_output, text=True, check=True
        )
        return res.stdout.rstrip()
    except subprocess.CalledProcessError as e:
        if log_error:
            err_msg = (
                e.stderr.strip()
                if e.stderr
                else e.stdout.strip()
                if e.stdout
                else str(e)
            )
            print(f"Error running {' '.join(cmd)}: {err_msg}", file=sys.stderr)
        raise


def get_git_common_dir():
    try:
        common_dir = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return os.path.abspath(common_dir)
    except subprocess.CalledProcessError:
        return None


def get_main_branch(common_dir):
    # Try remote HEAD first
    try:
        remote_head = subprocess.check_output(
            [
                "git",
                "-C",
                common_dir,
                "symbolic-ref",
                "--short",
                "refs/remotes/origin/HEAD",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if remote_head.startswith("origin/"):
            return remote_head[len("origin/") :]
    except subprocess.CalledProcessError:
        pass

    # Try looking for refs/heads/main or master
    for b in ["main", "master"]:
        if os.path.exists(os.path.join(common_dir, "refs", "heads", b)):
            return b

    # Default fallback
    return "main"


def list_worktrees(project_root):
    output = run_git(["worktree", "list", "--porcelain"], cwd=project_root)
    worktrees = []
    current_wt = {}

    for line in output.splitlines():
        line = line.strip()
        if not line:
            if current_wt:
                worktrees.append(current_wt)
                current_wt = {}
            continue

        parts = line.split(" ", 1)
        key = parts[0]
        val = parts[1] if len(parts) > 1 else ""

        if key == "worktree":
            current_wt["path"] = os.path.abspath(val)
            current_wt["bare"] = False
        elif key == "bare":
            current_wt["bare"] = True
        elif key == "branch":
            current_wt["branch"] = val

    if current_wt:
        worktrees.append(current_wt)

    return worktrees


def parse_git_status(status_output):
    """Parses git status --porcelain output and returns (staged_files, unstaged_files).
    Each list contains tuples of (status_indicator, file_path).
    """
    staged = []
    unstaged = []

    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        status_part = line[:2]
        file_path = line[3:]

        idx_status = status_part[0]
        worktree_status = status_part[1]

        is_staged = idx_status not in (" ", "?", "!")
        is_unstaged = worktree_status != " " or status_part == "??"

        if is_staged:
            staged.append((idx_status, file_path))
        if is_unstaged:
            indicator = worktree_status if status_part != "??" else "??"
            unstaged.append((indicator, file_path))

    return staged, unstaged


def get_main_tree_hashes(project_root, main_branch):
    try:
        output = run_git(
            ["log", f"refs/heads/{main_branch}", "--format=%T", "-n", "100"],
            cwd=project_root,
            log_error=False,
        )
        return set(output.splitlines())
    except Exception:
        return set()


def is_branch_merged(project_root, branch_ref, main_branch, main_tree_hashes=None):
    # 1. Standard check (commit ancestry)
    try:
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                branch_ref,
                f"refs/heads/{main_branch}",
            ],
            cwd=project_root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        pass

    # 2. Squash merge fallback (tree hash comparison in recent history of main)
    try:
        branch_tree = run_git(
            ["rev-parse", f"{branch_ref}^{{tree}}"], cwd=project_root, log_error=False
        )
        if main_tree_hashes is None:
            main_tree_hashes = get_main_tree_hashes(project_root, main_branch)

        if branch_tree in main_tree_hashes:
            return True
    except Exception:
        pass

    return False
