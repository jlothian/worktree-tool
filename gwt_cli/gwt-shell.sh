# This file is a reference and environment script for git-worktree-tool (gwt).
# To use these aliases, source this file from your shell:
#   source gwt-shell.sh

# shellcheck shell=bash

# Unalias wt if it is already defined as an alias, to prevent parsing errors
if alias wt >/dev/null 2>&1; then
    unalias wt
fi

# Resolve directory of this script in both Bash and Zsh
_GWT_DIR=""
if [ -n "${BASH_SOURCE[0]}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    _GWT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
elif [ -n "$ZSH_VERSION" ]; then
    # shellcheck disable=SC2296
    _ZSH_SRC="${(%):-%x}"
    if [ -f "$_ZSH_SRC" ]; then
        _GWT_DIR="$( cd "$( dirname "$_ZSH_SRC" )" && pwd )"
    fi
fi

# Add bin to path if not already present (checking both local bin/ and parent bin/)
if [ -n "$_GWT_DIR" ]; then
    if [ -d "$_GWT_DIR/bin" ]; then
        _BIN_DIR="$_GWT_DIR/bin"
    elif [ -d "$(dirname "$_GWT_DIR")/bin" ]; then
        _BIN_DIR="$(dirname "$_GWT_DIR")/bin"
    fi
    
    if [ -n "$_BIN_DIR" ] && [[ ":$PATH:" != *":$_BIN_DIR:"* ]]; then
        export PATH="$_BIN_DIR:$PATH"
    fi
    unset _BIN_DIR
fi

unset _GWT_DIR

# Wrapper function for wt to allow directory changing (cd) on 'new' and 'init'
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

    if [ "$1" = "new" ] || [ "$1" = "init" ] || [ "$1" = "go" ] || [ $is_interactive -eq 1 ]; then
        local subcmd="$1"
        shift
        local target_dir
        # Run gwt-cli, capturing only stdout (the path on success)
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

# Autocompletion for Zsh
# shellcheck disable=SC2034,SC2154
_wt_zsh() {
    local -a subcmds
    subcmds=(
        'init:Clone a repository bare and setup main worktree'
        'new:Create a new worktree branched off main'
        'clean:Clean up merged worktrees'
        'cleanup:Clean up merged worktrees'
        'list:List all active worktrees and their status'
        'go:Navigate to an existing worktree (interactive if no name given)'
        'repair:Repair broken worktree pointers'
        'delete:Delete a specific worktree and its branch'
        'remove:Delete a specific worktree and its branch'
        'rm:Delete a specific worktree and its branch'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'wt command' subcmds
    elif (( CURRENT == 3 )); then
        case "${words[2]}" in
            new)
                local -a branches
                # shellcheck disable=SC2207
                branches=($(git branch -a --format="%(refname:short)" 2>/dev/null | grep -v 'HEAD'))
                _describe -t branches 'branches' branches
                ;;
            go|delete|remove|rm)
                local -a worktrees
                # Get worktree directories and branches
                mapfile -t worktrees < <(git worktree list --porcelain 2>/dev/null | grep -E "^(worktree|branch)" | paste - - | sed 's/worktree //;s/branch refs\/heads\///' | awk '{print $1, $2}' | grep -v "\.bare" | awk '{print $1, $2}')
                _describe -t worktrees 'worktrees' worktrees
                ;;
        esac
    fi
}

# Autocompletion for Bash
_wt_bash() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="init new clean cleanup list go repair delete remove rm"

    if [ "$COMP_CWORD" -eq 1 ]; then
        # shellcheck disable=SC2207
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    elif [ "$COMP_CWORD" -eq 2 ]; then
        case "${prev}" in
            new)
                local branch_list
                branch_list=$(git branch -a --format="%(refname:short)" 2>/dev/null | grep -v 'HEAD')
                # shellcheck disable=SC2207
                COMPREPLY=( $(compgen -W "${branch_list}" -- "${cur}") )
                return 0
                ;;
            go|delete|remove|rm)
                local worktree_list
                worktree_list=$(git worktree list --porcelain 2>/dev/null | grep -E "^(worktree|branch)" | paste - - | sed 's/worktree //;s/branch refs\/heads\///' | awk '{print $1, $2}' | grep -v "\.bare" | awk '{print $1, $2}' | tr '\n' ' ')
                # shellcheck disable=SC2207
                COMPREPLY=( $(compgen -W "${worktree_list}" -- "${cur}") )
                return 0
                ;;
        esac
    fi
}

# Register autocompletion based on active shell type
if [ -n "$ZSH_VERSION" ] && type compdef >/dev/null 2>&1; then
    compdef _wt_zsh wt
elif [ -n "$BASH_VERSION" ]; then
    complete -F _wt_bash wt
fi
