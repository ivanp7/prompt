#!/bin/sh

MIN_COLS=99
CURRENT_COLS="$(tput cols)"
if [ "$(tput cols)" -lt $MIN_COLS ]
then
    echo "This demo requires a terminal with at least $MIN_COLS columns to be displayed correctly."
    echo "The current terminal has $CURRENT_COLS columns."
    exit 1
fi

c () { printf "\033[38;5;${1}m"; }

S="$(c 11)"
R="\033[0m"

PROMPT_SCRIPT="$(dirname -- "$0")/prompt.py"

unset PROMPT_STATUS PROMPT_PATH
unset PROMPT_DIR_UNREADABLE PROMPT_DIR_UNWRITABLE PROMPT_DIR_SETGUID PROMPT_DIR_STICKY
unset PROMPT_GIT_BRANCH PROMPT_GIT_DIR_DEPTH PROMPT_GIT_AHEAD PROMPT_GIT_BEHIND
unset PROMPT_GIT_MERGING PROMPT_GIT_UNTRACKED PROMPT_GIT_MODIFIED PROMPT_GIT_STAGED
unset PROMPT_EXIT_CODE PROMPT_EXEC_TIME
unset PROMPT_ROOT
unset PROMPT_MAX_LENGTH

echo "${R}The prompt is controlled by the following environment variables:

${S}PROMPT_STATUS${R} -- arbitrary short status message

${S}PROMPT_PATH${R} -- absolute path to present working directory (if unset, ${S}PWD${R} is used instead)
    ${S}PROMPT_DIR_UNREADABLE${R} -- present working directory is unreadable
    ${S}PROMPT_DIR_UNWRITABLE${R} -- present working directory is unwritable
    ${S}PROMPT_DIR_SETGUID${R} -- present working directory has setguid bit set
    ${S}PROMPT_DIR_STICKY${R} -- present working directory has sticky bit set

${S}PROMPT_GIT_BRANCH${R} -- name of current git branch (unset if not in git repository)
    ${S}PROMPT_GIT_DIR_DEPTH${R} -- depth into repository directory tree (unset if not in git repository)
    ${S}PROMPT_GIT_AHEAD${R} -- number of commits ahead remote repository (unset if none)
    ${S}PROMPT_GIT_BEHIND${R} -- number of commits behind remote repository (unset if none)
    ${S}PROMPT_GIT_MERGING${R} -- repository is in merging state (unset otherwise)
    ${S}PROMPT_GIT_UNTRACKED${R} -- repository contains untracked files (unset otherwise)
    ${S}PROMPT_GIT_MODIFIED${R} -- repository contains unstaged changes in tracked files (unset otherwise)
    ${S}PROMPT_GIT_STAGED${R} -- repository contains staged changes in tracked files (unset otherwise)

${S}PROMPT_EXIT_CODE${R} -- exit code of last command (unset if no command were executed)
${S}PROMPT_EXEC_TIME${R} -- execution time of last command in seconds (unset if no command were executed)

${S}PROMPT_ROOT${R} -- current user is root (unset otherwise)

${S}PROMPT_MAX_LENGTH${R} -- prompt length limit (unset to disable contraction)

${S}PROMPT_STYLE${R} -- prompt style in JSON format (optional, applied on top of the default style)
                refer to the source code for the list of adjustable elements
"
echo "

Without any of these variables set, the prompt displays present working directory only:
"

"$PROMPT_SCRIPT"

echo "
Non-printable characters (codes 0-31, 127) are replaced with a special symbol,
so the prompt won't break:
"

export PROMPT_PATH="$(echo "/the/last/path/component/has 2 lines:/first line\nsecond line")"
"$PROMPT_SCRIPT"

echo

export PROMPT_PATH="$(echo "/this/has/tabs\tin\tthe\tname")"
"$PROMPT_SCRIPT"

echo

export PROMPT_PATH="$(echo "/do\rnot\ause\vnon printable\033characters\nin\tthe\bfile\fname")"
"$PROMPT_SCRIPT"

echo "
Notice that slashes separating the path components are replaced with digits.
These digits designate number of levels to ascend
to get to that point from the current directory (modulo 10):
"

export PROMPT_PATH="/this/is/a/very/long/PROMPT_PATH/directory/with/more/than/10/components"
"$PROMPT_SCRIPT"

echo "
Root directory is the only exception:
"

PROMPT_PATH="/" "$PROMPT_SCRIPT"

echo "


A directory can be indicated as unreadable ($(c 160)r${R}), unwritable ($(c 160)w${R}), setguid ($(c 40)g${R}), and/or sticky ($(c 40)t${R}):
"

export PROMPT_PATH="/tmp/sessions/1/log"
PROMPT_DIR_UNREADABLE= "$PROMPT_SCRIPT"
echo
PROMPT_DIR_UNWRITABLE= "$PROMPT_SCRIPT"
echo
PROMPT_DIR_SETGUID= "$PROMPT_SCRIPT"
echo
PROMPT_DIR_STICKY= "$PROMPT_SCRIPT"
echo
PROMPT_DIR_UNREADABLE= PROMPT_DIR_UNWRITABLE= PROMPT_DIR_SETGUID= PROMPT_DIR_STICKY= "$PROMPT_SCRIPT"

echo "


Status color is different for non-root users and root:
"

export PROMPT_PATH="/home/user"
PROMPT_STATUS="non root" "$PROMPT_SCRIPT"
echo
PROMPT_STATUS="root" PROMPT_ROOT= "$PROMPT_SCRIPT"

echo "


Git indicators are displayed in the following order:
($(c 230)branch${R}) ($(c 254)ahead${R})($(c 232)behind${R}) ($(c 19)merging${R})($(c 124)untracked${R})($(c 220)modified${R})($(c 40)staged${R})

Directories belonging to a git repository are highlighted with a $(c 229)different color${R}:
"

export PROMPT_PATH="/home/user/projects/cool-program/src"
export PROMPT_GIT_BRANCH="master"
export PROMPT_GIT_DIR_DEPTH=1
export PROMPT_GIT_AHEAD=2
export PROMPT_GIT_BEHIND=1
export PROMPT_GIT_MERGING=
export PROMPT_GIT_UNTRACKED=
export PROMPT_GIT_MODIFIED=
export PROMPT_GIT_STAGED=
"$PROMPT_SCRIPT"

echo "
Not all indicators have to be displayed at all times:
"

unset PROMPT_GIT_AHEAD PROMPT_GIT_BEHIND PROMPT_GIT_MERGING PROMPT_GIT_STAGED
"$PROMPT_SCRIPT"

echo
unset PROMPT_GIT_UNTRACKED PROMPT_GIT_MODIFIED
export PROMPT_GIT_AHEAD=1
export PROMPT_GIT_STAGED=
"$PROMPT_SCRIPT"

echo
unset PROMPT_GIT_AHEAD PROMPT_GIT_STAGED
"$PROMPT_SCRIPT"
unset PROMPT_GIT_BRANCH PROMPT_GIT_DIR_DEPTH

echo "


For non-zero exit codes without standard meaning, only number is displayed:
"

export PROMPT_PATH="/usr/local/bin"
PROMPT_EXIT_CODE=100 "$PROMPT_SCRIPT"

echo "
For non-zero exit codes with standard meaning, description is appended:
"

PROMPT_EXIT_CODE=1 "$PROMPT_SCRIPT"
echo
PROMPT_EXIT_CODE=127 "$PROMPT_SCRIPT"

echo "
For exit codes corresponding to signals, signal name is appended:
"

PROMPT_EXIT_CODE=130 "$PROMPT_SCRIPT"
echo
PROMPT_EXIT_CODE=138 "$PROMPT_SCRIPT"

echo "
Zero exit code (command success) is designated with a different color and no text:
"

export PROMPT_EXIT_CODE=0
"$PROMPT_SCRIPT"

echo "


Execution time is displayed as days, hours, minutes, and seconds.
Up to 2 most significant components are displayed:
"

PROMPT_STATUS="1 second" PROMPT_EXEC_TIME=1 "$PROMPT_SCRIPT"
echo
PROMPT_STATUS="100 seconds" PROMPT_EXEC_TIME=100 "$PROMPT_SCRIPT"
echo
PROMPT_STATUS="10000 seconds" PROMPT_EXEC_TIME=10000 "$PROMPT_SCRIPT"
echo
PROMPT_STATUS="1000000 seconds" PROMPT_EXEC_TIME=1000000 "$PROMPT_SCRIPT"

echo "
If execution time is 0 seconds, it is not displayed:
"

PROMPT_STATUS="0 seconds" PROMPT_EXEC_TIME=0 "$PROMPT_SCRIPT"

echo "


With all supported indicators enabled at once, the prompt looks like this:
"

export PROMPT_STATUS="PROMPT_STATUS"
export PROMPT_PATH="/this/is/PROMPT_PATH"
export PROMPT_DIR_UNREADABLE=
export PROMPT_DIR_UNWRITABLE=
export PROMPT_DIR_SETGUID=
export PROMPT_DIR_STICKY=
export PROMPT_GIT_BRANCH="PROMPT_GIT_BRANCH"
export PROMPT_GIT_DIR_DEPTH=0
export PROMPT_GIT_AHEAD=15
export PROMPT_GIT_BEHIND=11
export PROMPT_GIT_MERGING=
export PROMPT_GIT_UNTRACKED=
export PROMPT_GIT_MODIFIED=
export PROMPT_GIT_STAGED=
export PROMPT_EXIT_CODE=138
export PROMPT_EXEC_TIME=999
export PROMPT_ROOT=

"$PROMPT_SCRIPT"

echo "
This prompt's length is 99 columns. It is long and may not fit in the terminal.
However, it is possible to set length limit so the prompt would be contracted if necessary.

Steps of contraction:"

echo "
- postfix disappears:
"
PROMPT_MAX_LENGTH=98 "$PROMPT_SCRIPT"
echo "
- exit code suffix disappears:
"
PROMPT_MAX_LENGTH=96 "$PROMPT_SCRIPT"
echo "
- git branch name disappears:
"
PROMPT_MAX_LENGTH=88 "$PROMPT_SCRIPT"
echo "
- characters are omitted from path components:
"
PROMPT_MAX_LENGTH=64 "$PROMPT_SCRIPT"
echo "
- minimum is 2 characters per path component:
"
PROMPT_MAX_LENGTH=60 "$PROMPT_SCRIPT"
echo "
- execution time disappears:
"
PROMPT_MAX_LENGTH=59 "$PROMPT_SCRIPT"
echo "
- exit code disappears, leaving color strip only:
"
PROMPT_MAX_LENGTH=52 "$PROMPT_SCRIPT"
echo "
- status disappears:
"
PROMPT_MAX_LENGTH=47 "$PROMPT_SCRIPT"

echo "
Length of the final prompt is 34, which is a third (34/99) of the original length!
"

