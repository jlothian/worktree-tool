# This file is a reference and environment script for git-worktree-tool (gwt).
# To use these aliases, source this file from your shell:
#   source aliases.sh

# Unalias gwt if it is already defined as an alias, to prevent parsing errors
if alias gwt >/dev/null 2>&1; then
    unalias gwt
fi

# Resolve directory of this script in both Bash and Zsh
if [ -n "$BASH_VERSION" ]; then
    GWT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
elif [ -n "$ZSH_VERSION" ]; then
    GWT_DIR="$( cd "$( dirname "${(%):-%x}" )" && pwd )"
else
    GWT_DIR="$( cd "$( dirname "$0" )" && pwd )"
fi

# Add bin to path if not already present
if [[ ":$PATH:" != *":$GWT_DIR/bin:"* ]]; then
    export PATH="$GWT_DIR/bin:$PATH"
fi

# Wrapper function for gwt to allow directory changing (cd) on 'new'
gwt() {
    if [ "$1" = "new" ]; then
        shift
        local target_dir
        # Run gwt-cli, capturing only stdout (the path on success)
        target_dir=$(gwt-cli new "$@")
        local exit_code=$?
        if [ $exit_code -eq 0 ] && [ -n "$target_dir" ] && [ -d "$target_dir" ]; then
            cd "$target_dir"
        fi
        return $exit_code
    else
        gwt-cli "$@"
    fi
}

# Autocompletion for Zsh
_gwt_zsh() {
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
        _describe -t commands 'gwt command' subcmds
    elif (( CURRENT == 3 )); then
        case "$words[2]" in
            new)
                local -a branches
                branches=($(git branch -a --format="%(refname:short)" 2>/dev/null | grep -v 'HEAD'))
                _describe -t branches 'branches' branches
                ;;
        esac
    fi
}

# Autocompletion for Bash
_gwt_bash() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="init new clean cleanup list repair"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    elif [ $COMP_CWORD -eq 2 ]; then
        case "${prev}" in
            new)
                local branches=$(git branch -a --format="%(refname:short)" 2>/dev/null | grep -v 'HEAD')
                COMPREPLY=( $(compgen -W "${branches}" -- ${cur}) )
                return 0
                ;;
        esac
    fi
}

# Register autocompletion based on active shell type
if [ -n "$ZSH_VERSION" ] && type compdef >/dev/null 2>&1; then
    compdef _gwt_zsh gwt
elif [ -n "$BASH_VERSION" ]; then
    complete -F _gwt_bash gwt
fi

