import argparse
import sys

from gwt_cli.commands import (
    cmd_init,
    cmd_new,
    cmd_clean,
    cmd_list,
    cmd_go,
    cmd_repair,
    cmd_init_shell,
)

__version__ = "0.3.0"


class StderrArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)


def main():
    parser = StderrArgumentParser(description="Git Worktree Management Tool")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the tool's version and exit",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Clone a repository bare and setup main worktree"
    )
    init_parser.add_argument("url", help="URL of the repository to clone")
    init_parser.add_argument(
        "directory", nargs="?", default=None, help="Target directory for the project"
    )
    init_parser.add_argument(
        "--main", dest="main", default=None, help="Custom main branch name to checkout"
    )
    init_parser.set_defaults(
        handler=lambda args: cmd_init(args.url, args.directory, args.main)
    )

    new_parser = subparsers.add_parser(
        "new", help="Create a new worktree branched off main"
    )
    new_parser.add_argument("branch", help="Name of the new branch/worktree")
    new_parser.set_defaults(handler=lambda args: cmd_new(args.branch))

    init_shell_parser = subparsers.add_parser(
        "init-shell", help="Generate shell wrapper and autocomplete configuration"
    )
    init_shell_parser.add_argument(
        "shell",
        nargs="?",
        choices=["bash", "zsh"],
        default=None,
        help="The shell type (bash or zsh)",
    )
    init_shell_parser.set_defaults(handler=lambda args: cmd_init_shell(args.shell))

    clean_parser = subparsers.add_parser("clean", help="Clean up merged worktrees")
    clean_parser.set_defaults(handler=lambda args: cmd_clean())

    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up merged worktrees")
    cleanup_parser.set_defaults(handler=lambda args: cmd_clean())

    list_parser = subparsers.add_parser(
        "list", help="List all active worktrees and their status"
    )
    list_parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch interactive fzf picker to select and cd to a worktree",
    )
    list_parser.set_defaults(handler=lambda args: cmd_list(args.interactive))

    go_parser = subparsers.add_parser(
        "go", help="Navigate to an existing worktree (interactive if no name given)"
    )
    go_parser.add_argument(
        "worktree",
        nargs="?",
        default=None,
        help="Name of the worktree to navigate to (interactive picker if omitted)",
    )
    go_parser.set_defaults(handler=lambda args: cmd_go(args.worktree))

    repair_parser = subparsers.add_parser(
        "repair", help="Repair broken worktree pointers"
    )
    repair_parser.set_defaults(handler=lambda args: cmd_repair())

    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
