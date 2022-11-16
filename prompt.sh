#!/bin/sh

[ "$PROMPT_PATH" ] && { cd -- "$PROMPT_PATH" || exit 1; unset PROMPT_PATH; }

[ -r "." ] && unset PROMPT_DIR_UNREADABLE || export PROMPT_DIR_UNREADABLE=
[ -w "." ] && unset PROMPT_DIR_UNWRITABLE || export PROMPT_DIR_UNWRITABLE=

if git rev-parse --is-inside-work-tree > /dev/null 2>&1 &&
    [ "$(git rev-parse --is-inside-git-dir 2> /dev/null)" = "false" ]
then
    export PROMPT_GIT_BRANCH="$(git branch --show-current)"

    export PROMPT_GIT_AHEAD="$(git log --oneline @{u}.. 2> /dev/null | wc -l | tr -d ' ')"
    [ "$PROMPT_GIT_AHEAD" -gt 0 ] || unset PROMPT_GIT_AHEAD

    export PROMPT_GIT_BEHIND="$(git log --oneline ..@{u} 2> /dev/null | wc -l | tr -d ' ')"
    [ "$PROMPT_GIT_BEHIND" -gt 0 ] || unset PROMPT_GIT_BEHIND

    GIT_DIR="$(git rev-parse --git-dir 2> /dev/null)"
    [ -n "$GIT_DIR" -a -r "$GIT_DIR/MERGE_HEAD" ] &&
        export PROMPT_GIT_MERGING= || unset PROMPT_GIT_MERGING

    [ "$(git ls-files $(git rev-parse --show-toplevel) --other --exclude-standard 2> /dev/null)" ] &&
        export PROMPT_GIT_UNTRACKED= || unset PROMPT_GIT_UNTRACKED

    git diff --quiet 2> /dev/null &&
        unset PROMPT_GIT_MODIFIED || export PROMPT_GIT_MODIFIED=

    git diff --cached --quiet 2> /dev/null &&
        unset PROMPT_GIT_STAGED || export PROMPT_GIT_STAGED=
else
    unset PROMPT_GIT_BRANCH
    unset PROMPT_GIT_AHEAD PROMPT_GIT_BEHIND PROMPT_GIT_MERGING
    unset PROMPT_GIT_UNTRACKED PROMPT_GIT_MODIFIED PROMPT_GIT_STAGED
fi

exec prompt.py

