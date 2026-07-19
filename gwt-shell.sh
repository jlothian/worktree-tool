# This file is a wrapper that sources the actual git-worktree-tool (gwt) integration script.
# To use it, source this file from your shell:
#   source gwt-shell.sh

# shellcheck shell=bash

if [ -n "$BASH_VERSION" ] && [ -n "${BASH_SOURCE[0]}" ]; then
    _GWT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
elif [ -n "$ZSH_VERSION" ]; then
    # shellcheck disable=SC2296
    _ZSH_SRC="${(%):-%x}"
    _GWT_DIR="$( cd "$( dirname "$_ZSH_SRC" )" && pwd )"
else
    _GWT_DIR="$( cd "$( dirname "$0" )" && pwd )"
fi

if [ -n "$_GWT_DIR" ] && [ -f "$_GWT_DIR/gwt_cli/gwt-shell.sh" ]; then
    # shellcheck source=/dev/null
    source "$_GWT_DIR/gwt_cli/gwt-shell.sh"
else
    echo "Error: Could not find gwt_cli/gwt-shell.sh to source." >&2
fi

unset _GWT_DIR
