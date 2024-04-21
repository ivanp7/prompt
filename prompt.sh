#!/bin/sh

# Set all prompt variables except PROMPT_STATUS, PROMPT_PATH, PROMPT_EXIT_CODE, PROMPT_EXEC_TIME

if [ "$PROMPT_PATH" ]
then
    [ -d "$PROMPT_PATH" ] || exit 1
    PROMPT_PATH="$(realpath -L -- "$PROMPT_PATH")"
else
    PROMPT_PATH="$PWD"
fi

[ ! -r "$PROMPT_PATH" ] && export PROMPT_DIR_UNREADABLE= || unset PROMPT_DIR_UNREADABLE
[ ! -w "$PROMPT_PATH" ] && export PROMPT_DIR_UNWRITABLE= || unset PROMPT_DIR_UNWRITABLE
[ ! -x "$PROMPT_PATH" ] && export PROMPT_DIR_UNVISITABLE= || unset PROMPT_DIR_UNVISITABLE
[ -g "$PROMPT_PATH" ] && export PROMPT_DIR_SETGUID= || unset PROMPT_DIR_SETGUID
[ -k "$PROMPT_PATH" ] && export PROMPT_DIR_STICKY= || unset PROMPT_DIR_STICKY

reset_git ()
{
    unset PROMPT_GIT_DIR_DEPTH
    unset PROMPT_GIT_BRANCH PROMPT_GIT_DETACHED
    unset PROMPT_GIT_AHEAD PROMPT_GIT_BEHIND PROMPT_GIT_MERGING
    unset PROMPT_GIT_UNTRACKED PROMPT_GIT_MODIFIED PROMPT_GIT_STAGED
}

if [ -x "$PROMPT_PATH" ]
then
    cd -- "$PROMPT_PATH"

    if git rev-parse --is-inside-work-tree > /dev/null 2>&1 &&
        [ "$(git rev-parse --is-inside-git-dir 2> /dev/null)" = "false" ]
    then
        export PROMPT_GIT_BRANCH="$(git branch --show-current)"
        if [ "$PROMPT_GIT_BRANCH" ]
        then
            unset PROMPT_GIT_DETACHED
        else
            export PROMPT_GIT_BRANCH="$(git rev-parse --short HEAD)"
            export PROMPT_GIT_DETACHED=
        fi

        GIT_ROOT="$(git rev-parse --show-toplevel 2> /dev/null)"
        GIT_RELPATH="$(realpath --relative-base="$GIT_ROOT" -- "$PWD")"
        if [ "$GIT_RELPATH" = "." ]
        then
            export PROMPT_GIT_DIR_DEPTH=0
        else
            export PROMPT_GIT_DIR_DEPTH=$((1 + $(printf "$GIT_RELPATH" | sed 's|[^/]||g' | wc -m)))
        fi

        export PROMPT_GIT_AHEAD="$(git log --oneline @{u}.. 2> /dev/null | wc -l | tr -d ' ')"
        [ "$PROMPT_GIT_AHEAD" -gt 0 ] || unset PROMPT_GIT_AHEAD

        export PROMPT_GIT_BEHIND="$(git log --oneline ..@{u} 2> /dev/null | wc -l | tr -d ' ')"
        [ "$PROMPT_GIT_BEHIND" -gt 0 ] || unset PROMPT_GIT_BEHIND

        GIT_DIR="$(git rev-parse --git-dir 2> /dev/null)"
        [ -n "$GIT_DIR" -a -r "$GIT_DIR/MERGE_HEAD" ] &&
            export PROMPT_GIT_MERGING= || unset PROMPT_GIT_MERGING

        [ "$(git ls-files "$GIT_ROOT" --others --exclude-standard 2> /dev/null)" ] &&
            export PROMPT_GIT_UNTRACKED= || unset PROMPT_GIT_UNTRACKED

        git diff --quiet 2> /dev/null &&
            unset PROMPT_GIT_MODIFIED || export PROMPT_GIT_MODIFIED=

        git diff --cached --quiet 2> /dev/null &&
            unset PROMPT_GIT_STAGED || export PROMPT_GIT_STAGED=
    else
        reset_git
    fi
else
    reset_git
fi

[ "$(id -u)" -eq 0 ] && export PROMPT_ROOT= || unset PROMPT_ROOT

: ${PROMPT_MAX_LENGTH:=$(tput cols)}
export PROMPT_MAX_LENGTH

PROMPT_PY="$(realpath -- "$(dirname -- "$0")/prompt.py")"
[ -x "$PROMPT_PY" ] && exec "$PROMPT_PY" || exec prompt.py

