import os
import sys
import subprocess
import shutil

from gwt_cli.git import (
    run_git,
    get_git_common_dir,
    get_main_branch,
    list_worktrees,
    parse_git_status,
    is_branch_merged,
    get_main_tree_hashes,
)


def cmd_init(url, directory=None, main_branch_override=None):
    if not directory:
        base = url.split("/")[-1]
        if base.endswith(".git"):
            base = base[:-4]
        directory = base

    directory = os.path.abspath(directory)
    if os.path.exists(directory):
        print(f"Error: Target directory '{directory}' already exists.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(directory)
    bare_dir = os.path.join(directory, ".bare")

    print(f"Cloning bare repository into '{bare_dir}'...", file=sys.stderr)
    try:
        subprocess.run(
            ["git", "clone", "--bare", url, ".bare"], cwd=directory, check=True
        )

        dot_git_path = os.path.join(directory, ".git")
        with open(dot_git_path, "w") as f:
            f.write("gitdir: ./.bare\n")

        run_git(
            ["config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*"],
            cwd=directory,
        )

        print("Fetching remote branches...", file=sys.stderr)
        run_git(["fetch", "origin"], cwd=directory)

        if main_branch_override:
            default_branch = main_branch_override
        else:
            default_branch = get_main_branch(bare_dir)
        print(
            f"Setting up main worktree for branch '{default_branch}'...",
            file=sys.stderr,
        )

        try:
            remote_branch_exists = False
            try:
                run_git(
                    ["show-ref", "--verify", f"refs/remotes/origin/{default_branch}"],
                    cwd=directory,
                    log_error=False,
                )
                remote_branch_exists = True
            except Exception:
                pass

            if remote_branch_exists:
                run_git(
                    ["worktree", "add", default_branch, default_branch], cwd=directory
                )
                run_git(
                    [
                        "branch",
                        f"--set-upstream-to=origin/{default_branch}",
                        default_branch,
                    ],
                    cwd=directory,
                )
            else:
                run_git(["worktree", "add", default_branch], cwd=directory)
        except Exception as e:
            print(
                f"Warning: Could not create main worktree for '{default_branch}'. Repo might be empty: {e}",
                file=sys.stderr,
            )

        print("Initialization completed successfully.", file=sys.stderr)
        print(directory)
    except Exception as e:
        print(f"Error during initialization: {e}", file=sys.stderr)
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
            except Exception:
                pass
        sys.exit(1)


def cmd_new(branch_name):
    common_dir = get_git_common_dir()
    if not common_dir:
        print("Error: Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    if not (
        common_dir.endswith("/.bare")
        or common_dir.endswith("\\.bare")
        or os.path.basename(common_dir) == ".bare"
    ):
        print(
            "Error: Not in a gwt-initialized project (missing '.bare' directory).",
            file=sys.stderr,
        )
        sys.exit(1)

    project_root = os.path.dirname(common_dir)
    main_branch = get_main_branch(common_dir)
    main_worktree_path = os.path.join(project_root, main_branch)

    if os.path.isdir(main_worktree_path):
        print(
            f"Updating main branch '{main_branch}' in '{main_worktree_path}'...",
            file=sys.stderr,
        )
        try:
            try:
                run_git(["fetch", "origin"], cwd=main_worktree_path)
            except Exception:
                print(
                    "Warning: Could not fetch from origin (offline or no remote?).",
                    file=sys.stderr,
                )

            has_upstream = False
            try:
                run_git(
                    ["rev-parse", "--abbrev-ref", "@{u}"],
                    cwd=main_worktree_path,
                    log_error=False,
                )
                has_upstream = True
            except Exception:
                pass

            if has_upstream:
                run_git(["pull", "--ff-only"], cwd=main_worktree_path)
            else:
                print(
                    "Note: Main branch has no upstream tracking configured. Skipping pull.",
                    file=sys.stderr,
                )
        except Exception as e:
            print(f"Error updating main branch: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(
            f"Warning: Main worktree directory '{main_worktree_path}' not found. Cannot update main branch.",
            file=sys.stderr,
        )

    dir_name = branch_name.replace("/", "-")
    new_worktree_path = os.path.join(project_root, dir_name)

    if os.path.exists(new_worktree_path):
        print(
            f"Error: Target directory '{new_worktree_path}' already exists.",
            file=sys.stderr,
        )
        sys.exit(1)

    branch_exists = False
    try:
        run_git(
            ["show-ref", "--verify", f"refs/heads/{branch_name}"],
            cwd=project_root,
            log_error=False,
        )
        branch_exists = True
    except Exception:
        pass

    if branch_exists:
        print(f"Error: Branch '{branch_name}' already exists.", file=sys.stderr)
        sys.exit(1)

    print(
        f"Creating new worktree for branch '{branch_name}' at '{new_worktree_path}'...",
        file=sys.stderr,
    )
    try:
        run_git(
            ["worktree", "add", "-b", branch_name, new_worktree_path, main_branch],
            cwd=project_root,
        )
        print(new_worktree_path)
    except Exception as e:
        print(f"Error creating worktree: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_clean():
    common_dir = get_git_common_dir()
    if not common_dir:
        print("Error: Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    if not (
        common_dir.endswith("/.bare")
        or common_dir.endswith("\\.bare")
        or os.path.basename(common_dir) == ".bare"
    ):
        print(
            "Error: Not in a gwt-initialized project (missing '.bare' directory).",
            file=sys.stderr,
        )
        sys.exit(1)

    project_root = os.path.dirname(common_dir)
    main_branch = get_main_branch(common_dir)
    main_tree_hashes = get_main_tree_hashes(project_root, main_branch)

    worktrees = list_worktrees(project_root)
    user_cwd = os.path.abspath(os.getcwd())

    for wt in worktrees:
        path = wt.get("path")
        is_bare = wt.get("bare", False)
        branch_ref = wt.get("branch")

        if is_bare or path == common_dir:
            continue

        if not branch_ref:
            continue

        branch_name = branch_ref.replace("refs/heads/", "")
        if branch_name == main_branch:
            continue

        is_merged = is_branch_merged(
            project_root, branch_ref, main_branch, main_tree_hashes
        )

        if not is_merged:
            continue

        if user_cwd == path or user_cwd.startswith(path + os.sep):
            print(
                f"Skipping worktree '{branch_name}' at '{path}' because it is your current shell directory.",
                file=sys.stderr,
            )
            continue

        try:
            status_output = run_git(
                ["status", "--porcelain"], cwd=path, log_error=False
            )
            staged, unstaged = parse_git_status(status_output)
            is_clean = len(staged) == 0 and len(unstaged) == 0
        except Exception as e:
            print(
                f"Error checking status of worktree '{branch_name}' at '{path}': {e}",
                file=sys.stderr,
            )
            continue

        if is_clean:
            print(
                f"Worktree '{branch_name}' at '{path}' is merged and clean. Deleting...",
                file=sys.stderr,
            )
            try:
                run_git(["worktree", "remove", "--force", path], cwd=project_root)
                try:
                    run_git(["branch", "-d", branch_name], cwd=project_root)
                except Exception:
                    run_git(["branch", "-D", branch_name], cwd=project_root)
                print(
                    f"Successfully deleted worktree and branch '{branch_name}'.",
                    file=sys.stderr,
                )
            except Exception as e:
                print(f"Error deleting worktree '{branch_name}': {e}", file=sys.stderr)
        else:
            print(
                f"\nWorktree '{branch_name}' at '{path}' is merged but NOT clean.",
                file=sys.stderr,
            )
            if staged:
                print("Staged changes:", file=sys.stderr)
                for indicator, file_p in staged:
                    print(f"  {indicator} {file_p}", file=sys.stderr)
                print("", file=sys.stderr)
            if unstaged:
                print("Unstaged changes:", file=sys.stderr)
                for indicator, file_p in unstaged:
                    print(f"  {indicator} {file_p}", file=sys.stderr)
                print("", file=sys.stderr)

            try:
                sys.stderr.write(
                    f"Delete these files and the worktree '{branch_name}'? [y/N]: "
                )
                sys.stderr.flush()
                response = sys.stdin.readline().strip().lower()
                if response in ["y", "yes"]:
                    print("Deleting...", file=sys.stderr)
                    run_git(["worktree", "remove", "--force", path], cwd=project_root)
                    try:
                        run_git(["branch", "-d", branch_name], cwd=project_root)
                    except Exception:
                        run_git(["branch", "-D", branch_name], cwd=project_root)
                    print(
                        f"Successfully deleted worktree and branch '{branch_name}'.",
                        file=sys.stderr,
                    )
                else:
                    print("Skipping deletion.", file=sys.stderr)
            except Exception as e:
                print(
                    f"Error handling cleanup for '{branch_name}': {e}", file=sys.stderr
                )


def cmd_list(interactive=False):
    common_dir = get_git_common_dir()
    if not common_dir:
        print("Error: Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    if not (
        common_dir.endswith("/.bare")
        or common_dir.endswith("\\.bare")
        or os.path.basename(common_dir) == ".bare"
    ):
        print(
            "Error: Not in a gwt-initialized project (missing '.bare' directory).",
            file=sys.stderr,
        )
        sys.exit(1)

    project_root = os.path.dirname(common_dir)
    main_branch = get_main_branch(common_dir)
    main_tree_hashes = get_main_tree_hashes(project_root, main_branch)

    try:
        worktrees = list_worktrees(project_root)
    except Exception as e:
        print(f"Error listing worktrees: {e}", file=sys.stderr)
        sys.exit(1)

    rows = []
    max_worktree_len = len("WORKTREE")
    max_branch_len = len("BRANCH")
    max_merge_len = len("MERGE STATUS")

    for wt in worktrees:
        path = wt.get("path")
        is_bare = wt.get("bare", False)
        branch_ref = wt.get("branch")

        dir_name = os.path.basename(path)

        if is_bare or path == common_dir:
            rows.append((".bare (repo)", "-", "-", "-"))
            continue

        if not branch_ref:
            rows.append((dir_name, "(detached)", "-", "-"))
            continue

        branch_name = branch_ref.replace("refs/heads/", "")

        # Merge status
        if branch_name == main_branch:
            merge_status = "Main"
        else:
            if is_branch_merged(
                project_root, branch_ref, main_branch, main_tree_hashes
            ):
                merge_status = "Merged"
            else:
                merge_status = "Unmerged"

        # File status
        try:
            status_output = run_git(
                ["status", "--porcelain"], cwd=path, log_error=False
            )
            staged, unstaged = parse_git_status(status_output)
            num_staged = len(staged)
            num_unstaged = len(unstaged)

            if num_staged == 0 and num_unstaged == 0:
                file_status = "Clean"
            elif num_staged > 0 and num_unstaged > 0:
                file_status = f"Dirty ({num_staged} staged, {num_unstaged} unstaged)"
            elif num_staged > 0:
                file_status = f"Dirty ({num_staged} staged)"
            else:
                file_status = f"Dirty ({num_unstaged} unstaged)"
        except Exception:
            file_status = "Unknown"

        rows.append((dir_name, branch_name, merge_status, file_status))

    for r in rows:
        max_worktree_len = max(max_worktree_len, len(r[0]))
        max_branch_len = max(max_branch_len, len(r[1]))
        max_merge_len = max(max_merge_len, len(r[2]))

    worktree_w = max_worktree_len + 3
    branch_w = max_branch_len + 3
    merge_w = max_merge_len + 3

    fmt = f"{{:<{worktree_w}}} {{:<{branch_w}}} {{:<{merge_w}}} {{}}"
    total_width = worktree_w + branch_w + merge_w + len("FILE STATUS")

    if interactive and sys.stderr.isatty():
        if not shutil.which("fzf"):
            print(
                "Error: fzf is required for interactive mode. Please install it (e.g. 'brew install fzf') or run without '-i'.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Generate fzf input lines (excluding .bare)
        fzf_lines = [
            fmt.format("WORKTREE", "BRANCH", "MERGE STATUS", "FILE STATUS"),
            "-" * max(80, total_width),
        ]
        path_map = {}
        for r, wt in zip(rows, worktrees):
            if r[0] == ".bare (repo)":
                continue
            fzf_lines.append(fmt.format(r[0], r[1], r[2], r[3]))
            path_map[r[0]] = wt.get("path")

        fzf_input = "\n".join(fzf_lines) + "\n"

        cmd = [
            "fzf",
            "--header-lines=2",
            "--prompt=Select worktree to cd into: ",
            "--height=10",
            "--layout=reverse",
            "--border",
            "--preview",
            f"git -C {project_root}/{{1}} log --oneline -n 5 2>/dev/null || echo 'No git history'",
        ]

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr,
                text=True,
            )
            fzf_output, _ = proc.communicate(input=fzf_input)
            if proc.returncode == 0 and fzf_output.strip():
                parts = fzf_output.strip().split()
                if parts:
                    dir_name = parts[0]
                    target_path = path_map.get(dir_name)
                    if target_path and os.path.isdir(target_path):
                        print(target_path)
                        sys.exit(0)
            sys.exit(0)
        except Exception as e:
            print(f"Error running interactive menu: {e}", file=sys.stderr)
            sys.exit(1)

    print(fmt.format("WORKTREE", "BRANCH", "MERGE STATUS", "FILE STATUS"))
    print("-" * max(80, total_width))

    for r in rows:
        print(fmt.format(r[0], r[1], r[2], r[3]))


def cmd_go(worktree_name=None):
    common_dir = get_git_common_dir()
    if not common_dir:
        print("Error: Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    if not (
        common_dir.endswith("/.bare")
        or common_dir.endswith("\\.bare")
        or os.path.basename(common_dir) == ".bare"
    ):
        print(
            "Error: Not in a gwt-initialized project (missing '.bare' directory).",
            file=sys.stderr,
        )
        sys.exit(1)

    project_root = os.path.dirname(common_dir)
    worktrees = list_worktrees(project_root)

    if worktree_name:
        # Direct navigation to a specific worktree
        target_path = None
        for wt in worktrees:
            path = wt.get("path")
            if wt.get("bare", False) or path == common_dir:
                continue

            dir_name = os.path.basename(path)
            branch_ref = wt.get("branch")
            branch_name = branch_ref.replace("refs/heads/", "") if branch_ref else ""

            # Match by directory name or branch name
            if worktree_name in [dir_name, branch_name]:
                target_path = path
                break

        if not target_path:
            print(f"Error: Worktree '{worktree_name}' not found.", file=sys.stderr)
            sys.exit(1)

        if os.path.isdir(target_path):
            print(target_path)
            sys.exit(0)
        else:
            print(
                f"Error: Worktree directory '{target_path}' does not exist.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Interactive mode using fzf
    if sys.stderr.isatty():
        if not shutil.which("fzf"):
            print(
                "Error: fzf is required for interactive mode. Please install it (e.g. 'brew install fzf') or specify a worktree name.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Generate fzf input lines (excluding .bare)
        fzf_lines = []
        path_map = {}
        for wt in worktrees:
            path = wt.get("path")
            if wt.get("bare", False) or path == common_dir:
                continue

            dir_name = os.path.basename(path)
            branch_ref = wt.get("branch")
            branch_name = (
                branch_ref.replace("refs/heads/", "") if branch_ref else "(detached)"
            )

            # Get status for preview
            try:
                status_output = run_git(
                    ["status", "--porcelain"], cwd=path, log_error=False
                )
                staged, unstaged = parse_git_status(status_output)
                if len(staged) == 0 and len(unstaged) == 0:
                    status = "Clean"
                elif len(staged) > 0 and len(unstaged) > 0:
                    status = f"Dirty ({len(staged)} staged, {len(unstaged)} unstaged)"
                elif len(staged) > 0:
                    status = f"Dirty ({len(staged)} staged)"
                else:
                    status = f"Dirty ({len(unstaged)} unstaged)"
            except Exception:
                status = "Unknown"

            line = f"{dir_name:<30} {branch_name:<30} {status}"
            fzf_lines.append(line)
            path_map[dir_name] = path

        fzf_input = "\n".join(fzf_lines) + "\n"

        cmd = [
            "fzf",
            "--prompt=Select worktree to cd into: ",
            "--height=15",
            "--layout=reverse",
            "--border",
            "--preview",
            f"git -C {project_root}/{{1}} log --oneline -n 5 2>/dev/null || echo 'No git history'",
        ]

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr,
                text=True,
            )
            fzf_output, _ = proc.communicate(input=fzf_input)
            if proc.returncode == 0 and fzf_output.strip():
                parts = fzf_output.strip().split()
                if parts:
                    dir_name = parts[0]
                    target_path = path_map.get(dir_name)
                    if target_path and os.path.isdir(target_path):
                        print(target_path)
                        sys.exit(0)
            sys.exit(0)
        except Exception as e:
            print(f"Error running interactive menu: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(
            "Error: Interactive mode requires a terminal. Please specify a worktree name.",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_repair():
    common_dir = get_git_common_dir()
    if not common_dir:
        print("Error: Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    project_root = os.path.dirname(common_dir)
    print("Repairing worktree pointers...", file=sys.stderr)
    try:
        run_git(["worktree", "repair"], cwd=project_root)
        print("Worktree pointers successfully repaired.", file=sys.stderr)
    except Exception as e:
        print(f"Error repairing worktrees: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_init_shell(shell_type=None):
    if not shell_type:
        shell_env = os.environ.get("SHELL", "")
        if "zsh" in shell_env:
            shell_type = "zsh"
        elif "bash" in shell_env:
            shell_type = "bash"
        else:
            shell_type = "bash"  # Default fallback

    if shell_type == "zsh":
        print("""# Autocompletions and wrapper for wt (Zsh)
if alias wt >/dev/null 2>&1; then
    unalias wt
fi

function wt {
    local is_interactive=0
    if [ "$1" = "list" ]; then
        for arg in "$@"; do
            if [ "$arg" = "-i" ] || [ "$arg" = "--interactive" ]; then
                is_interactive=1
                break
            fi
        done
    fi

    if [ "$1" = "new" ] || [ "$1" = "init" ] || [ $is_interactive -eq 1 ]; then
        local subcmd="$1"
        shift
        local target_dir
        target_dir=$(gwt-cli "$subcmd" "$@")
        local exit_code=$?
        if [ $exit_code -eq 0 ] && [ -n "$target_dir" ] && [ -d "$target_dir" ]; then
            cd "$target_dir" || return $exit_code
        fi
        return $exit_code
    else
        gwt-cli "$@"
    fi
}

_wt_zsh() {
    local -a subcmds
    subcmds=(
        'init:Clone a repository bare and setup main worktree'
        'new:Create a new worktree branched off main'
        'clean:Clean up merged worktrees'
        'cleanup:Clean up merged worktrees'
        'list:List all active worktrees and their status'
        'repair:Repair broken worktree pointers'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'wt command' subcmds
    elif (( CURRENT == 3 )); then
        case "${words[2]}" in
            new)
                local -a branches
                branches=($(git branch -a --format="%(refname:short)" 2>/dev/null | grep -v 'HEAD'))
                _describe -t branches 'branches' branches
                ;;
        esac
    fi
}

if type compdef >/dev/null 2>&1; then
    compdef _wt_zsh wt
fi
""")
    elif shell_type == "bash":
        print("""# Autocompletions and wrapper for wt (Bash)
if alias wt >/dev/null 2>&1; then
    unalias wt
fi

function wt {
    local is_interactive=0
    if [ "$1" = "list" ]; then
        for arg in "$@"; do
            if [ "$arg" = "-i" ] || [ "$arg" = "--interactive" ]; then
                is_interactive=1
                break
            fi
        done
    fi

    if [ "$1" = "new" ] || [ "$1" = "init" ] || [ $is_interactive -eq 1 ]; then
        local subcmd="$1"
        shift
        local target_dir
        target_dir=$(gwt-cli "$subcmd" "$@")
        local exit_code=$?
        if [ $exit_code -eq 0 ] && [ -n "$target_dir" ] && [ -d "$target_dir" ]; then
            cd "$target_dir" || return $exit_code
        fi
        return $exit_code
    else
        gwt-cli "$@"
    fi
}

_wt_bash() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="init new clean cleanup list repair"

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    elif [ "$COMP_CWORD" -eq 2 ]; then
        case "${prev}" in
            new)
                local branch_list
                branch_list=$(git branch -a --format="%(refname:short)" 2>/dev/null | grep -v 'HEAD')
                COMPREPLY=( $(compgen -W "${branch_list}" -- "${cur}") )
                return 0
                ;;
        esac
    fi
}

complete -F _wt_bash wt
""")
    else:
        print(
            f"Error: Unsupported shell '{shell_type}'. Supported shells: bash, zsh",
            file=sys.stderr,
        )
        sys.exit(1)
