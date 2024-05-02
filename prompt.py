#!/usr/bin/env python

import os
import re
import json


# default style
PROMPT_STYLE = {
        ### status ###
        'col_status_fg_nonroot': 250,
        'col_status_bg_nonroot': 240,

        'col_status_fg_root': 236,
        'col_status_bg_root': 202,

        ### path ###
        'ch_path_omit': "≈",
        'ch_path_nonprint': "_",
        'ch_path_dir_unreadable': "r",
        'ch_path_dir_unwritable': "w",
        'ch_path_dir_unvisitable': "x",
        'ch_path_dir_setguid': "g",
        'ch_path_dir_sticky': "t",

        'col_path_dir_fg': 254,
        'col_path_git_dir_fg': 229,
        'col_path_sep_fg': 234,
        'col_path_omit_fg': 39,
        'col_path_nonprint_fg': 196,
        'col_path_noperm_fg': 160,
        'col_path_perm_fg': 40,
        'col_path_bg': 238,

        ### git status ###
        'ch_git_ahead': "↑",
        'ch_git_behind': "↓",
        'ch_git_merging': "↕",
        'ch_git_untracked': "•",
        'ch_git_modified': "•",
        'ch_git_staged': "•",

        'col_git_branch_fg': 230,
        'col_git_detached_fg': 208,
        'col_git_ahead_fg': 254,
        'col_git_behind_fg': 232,
        'col_git_merging_fg': 19,
        'col_git_untracked_fg': 124,
        'col_git_modified_fg': 220,
        'col_git_staged_fg': 40,
        'col_git_bg': 240,

        ### exit code ###
        'ch_exit_code_sep': '·',

        'col_exit_code_fg_success': 254,
        'col_exit_code_bg_success': 36,

        'col_exit_code_fg_fail': 252,
        'col_exit_code_bg_fail': 88,

        'col_exit_code_bg_default': 244,

        ### postfix ###
        'str_postfix': "", # "" if $TERM is "linux"
}

# known exit codes
PROMPT_EXIT_CODES = {
        "0": "SUCCESS", "1": "GENERAL", "2": "MISUSE",
        "126": "NOTEXEC", "128": "ABNORMAL",  "127": "NOTFOUND", "255": "OUTOFRANGE",
        # signals (128+N)
        "129": "SIGHUP",    "130": "SIGINT",    "131": "SIGQUIT",   "132": "SIGILL",    "133": "SIGTRAP",   # 1-5
        "134": "SIGABRT",   "135": "SIGBUS",    "136": "SIGFPE",    "137": "SIGKILL",   "138": "SIGUSR1",   # 6-10
        "139": "SIGSEGV",   "140": "SIGUSR2",   "141": "SIGPIPE",   "142": "SIGALRM",   "143": "SIGTERM",   # 11-15
        "145": "SIGCHLD",   "146": "SIGCONT",   "147": "SIGSTOP",   "148": "SIGTSTP",   "149": "SIGTTIN",   # 17-21
        "150": "SIGTTOU",   "151": "SIGURG",    "152": "SIGXCPU",   "153": "SIGXFSZ",   "154": "SIGVTALRM", # 22-26
        "155": "SIGPROF",   "156": "SIGWINCH",  "157": "SIGPOLL",   "158": "SIGPWR",    "159": "SIGSYS",    # 27-31
}


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def parse(environ: dict) -> AttributeDict:
    """Parse environment variables and return the prompt state.
    """
    prompt = AttributeDict()

    prompt.limited = os.environ['TERM'] == 'linux' # virtual terminal can display only 16 colors and 256 characters

    prompt.root = 'PROMPT_ROOT' in environ
    prompt.status = environ.get('PROMPT_STATUS', "")

    prompt.path = environ['PROMPT_PATH'] if 'PROMPT_PATH' in environ else environ['PWD']
    prompt.path_dir_unreadable = 'PROMPT_DIR_UNREADABLE' in environ
    prompt.path_dir_unwritable = 'PROMPT_DIR_UNWRITABLE' in environ
    prompt.path_dir_unvisitable = 'PROMPT_DIR_UNVISITABLE' in environ
    prompt.path_dir_setguid = 'PROMPT_DIR_SETGUID' in environ
    prompt.path_dir_sticky = 'PROMPT_DIR_STICKY' in environ

    prompt.path_git_dir_depth = environ.get('PROMPT_GIT_DIR_DEPTH', None)
    try:
        prompt.path_git_dir_depth = int(prompt.path_git_dir_depth)
    except:
        prompt.path_git_dir_depth = -2 # -1 is insufficient when $PWD is /

    prompt.git_branch = environ.get('PROMPT_GIT_BRANCH', None)
    prompt.git_detached = 'PROMPT_GIT_DETACHED' in environ
    prompt.git_ahead = environ.get('PROMPT_GIT_AHEAD', None)
    prompt.git_behind = environ.get('PROMPT_GIT_BEHIND', None)
    prompt.git_merging = 'PROMPT_GIT_MERGING' in environ
    prompt.git_untracked = 'PROMPT_GIT_UNTRACKED' in environ
    prompt.git_modified = 'PROMPT_GIT_MODIFIED' in environ
    prompt.git_staged = 'PROMPT_GIT_STAGED' in environ

    prompt.exit_code = environ.get('PROMPT_EXIT_CODE', None)
    prompt.exec_time = environ.get('PROMPT_EXEC_TIME', None)

    prompt.max_length = environ.get('PROMPT_MAX_LENGTH', None)
    try:
        prompt.max_length = int(prompt.max_length)
    except:
        prompt.max_length = None

    prompt.style = AttributeDict(PROMPT_STYLE)
    if prompt.limited:
        prompt.style.str_postfix = ""
    prompt_style_changes = environ.get('PROMPT_STYLE', None)
    if prompt_style_changes is not None:
        try:
            prompt_style_changes = json.loads(prompt_style_changes)
        except:
            prompt_style_changes = {}
        prompt.style.update(prompt_style_changes)
    del prompt_style_changes

    known_exit_codes = PROMPT_EXIT_CODES
    known_exit_codes_changes = environ.get('PROMPT_EXIT_CODES', None)
    if known_exit_codes_changes is not None:
        try:
            known_exit_codes_changes = json.loads(known_exit_codes_changes)
        except:
            known_exit_codes_changes = {}
        known_exit_codes.update(known_exit_codes_changes)
    prompt.style.str_exit_code_known = known_exit_codes
    del known_exit_codes, known_exit_codes_changes

    return prompt

def finalize_style(prompt: AttributeDict) -> AttributeDict:
    """Determine actual prompt style.
    """
    if 'col_status_fg' not in prompt.style:
        prompt.style.col_status_fg = prompt.style.col_status_fg_root if prompt.root \
                else prompt.style.col_status_fg_nonroot
    if 'col_status_bg' not in prompt.style:
        prompt.style.col_status_bg = prompt.style.col_status_bg_root if prompt.root \
                else prompt.style.col_status_bg_nonroot

    if prompt.exit_code is not None:
        exit_success = (prompt.exit_code == "0") or not prompt.exit_code

        if 'col_exit_code_fg' not in prompt.style:
            prompt.style.col_exit_code_fg = prompt.style.col_exit_code_fg_success if exit_success \
                    else prompt.style.col_exit_code_fg_fail
        if 'col_exit_code_bg' not in prompt.style:
            prompt.style.col_exit_code_bg = prompt.style.col_exit_code_bg_success if exit_success \
                    else prompt.style.col_exit_code_bg_fail
    else:
        if 'col_exit_code_bg' not in prompt.style:
            prompt.style.col_exit_code_bg = prompt.style.col_exit_code_bg_default

    if 'col_postfix_fg' not in prompt.style:
        prompt.style.col_postfix_fg = prompt.style.col_exit_code_bg

    return prompt

def prettify_exit_code(exit_code: str, sep: str, known_exit_codes: dict) -> tuple[str, str]:
    """Prettify exit code.
    """
    if exit_code is None:
        return None, None

    if (exit_code == "0") or not exit_code:
        return "", ""
    elif exit_code in known_exit_codes:
        return exit_code + sep + known_exit_codes[exit_code], exit_code
    else:
        return exit_code, exit_code

def prettify_exec_time(exec_time: str) -> str:
    """Prettify execution time.
    """
    if not exec_time:
        return None

    try:
        seconds = int(exec_time)
    except:
        return exec_time

    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    hours = hours % 24
    minutes = minutes % 60
    seconds = seconds % 60

    if days > 0:
        return f"{days}d{hours}h"
    elif hours > 0:
        return f"{hours}h{minutes}m"
    elif minutes > 0:
        return f"{minutes}m{seconds}s"
    elif seconds > 0:
        return f"{seconds}s"
    else:
        return None

def prettify(prompt: AttributeDict) -> AttributeDict:
    """Prettify prompt state.
    """
    prompt.exit_code, prompt.exit_code_short = \
            prettify_exit_code(prompt.exit_code, prompt.style.ch_exit_code_sep, prompt.style.str_exit_code_known)

    prompt.exec_time = prettify_exec_time(prompt.exec_time)

    return prompt

def color1(num: int=None, fg: bool=True) -> str:
    """Change foreground or background color of text.
    """
    assert num is None or (type(num) == int and num >= 0 and num < 256)

    s = chr(27) + '['
    if num is not None:
        s += f'{38 if fg else 48};5;{num}m'
    else:
        s += '0m'

    return s

def color2(fg: int=None, bg: int=None, transparent_bg: bool=False) -> str:
    """Change foreground and background color of text.
    """
    if bg is not None:
        s = color1(bg, False)
    else:
        s = color1(None) if transparent_bg else ''

    if fg is not None:
        s += color1(fg, True)

    return s

def visualize(prompt: AttributeDict) -> str:
    """Construct printable prompt string.
    """
    TRIANGLE = "" if not prompt.limited else "▶"

    ################################
    # calculate full prompt length #
    ################################

    length = 1 # space

    if prompt.status:
        length += len(prompt.status) + 1 # status, space

    assert len(prompt.style.ch_path_omit) == 1
    assert len(prompt.style.ch_path_nonprint) == 1
    assert len(prompt.style.ch_path_dir_unreadable) == 1
    assert len(prompt.style.ch_path_dir_unwritable) == 1
    assert len(prompt.style.ch_path_dir_unvisitable) == 1
    assert len(prompt.style.ch_path_dir_setguid) == 1
    assert len(prompt.style.ch_path_dir_sticky) == 1

    # split by slashes, remove empty parts, replace non-printable characters with temporary slashes
    path = [''.join([ch if ord(ch) >= 32 and ord(ch) != 127 else '/' for ch in component])
            for component in prompt.path.split('/') if component]
    if path:
        length += 1 + 1 + sum([1 + len(s) for s in path]) + 1 # triangle, space, path, space

        path_sep = [f"{i%10}" for i in range(len(path), 0, -1)]
        path_omitted = [0] * len(path)
    else:
        length += 1 + 1 + 1 + 1 # triangle, space, slash, space

    length_dir_attributes = int(prompt.path_dir_unreadable) + int(prompt.path_dir_unwritable) + \
            int(prompt.path_dir_unvisitable) + int(prompt.path_dir_setguid) + int(prompt.path_dir_sticky) # char, char, char, char, char
    if length_dir_attributes > 0:
        length_dir_attributes += 1 # space
        length += length_dir_attributes

    assert len(prompt.style.ch_git_ahead) == 1
    assert len(prompt.style.ch_git_behind) == 1
    assert len(prompt.style.ch_git_merging) == 1
    assert len(prompt.style.ch_git_untracked) == 1
    assert len(prompt.style.ch_git_modified) == 1
    assert len(prompt.style.ch_git_staged) == 1

    length_git_status_block = 0
    length_git_branch = 0
    length_git_history = 0
    length_git_state = 0
    if prompt.git_branch is not None:
        length_git_status_block += 1 + 1 # triangle, space

        length_git_branch += len(prompt.git_branch) + 1 # git branch, space

        if prompt.git_ahead or prompt.git_behind:
            if prompt.git_ahead:
                length_git_history += 1 + len(prompt.git_ahead) # character, ahead
            if prompt.git_behind:
                length_git_history += 1 + len(prompt.git_behind) # character, behind
            length_git_history += 1 # space

        length_git_state += int(prompt.git_merging) + int(prompt.git_untracked) + \
                int(prompt.git_modified) + int(prompt.git_staged) # char, char, char, char
        if length_git_state > 0:
            length_git_state += 1 # space

        length_git_status_block += length_git_branch + length_git_history + length_git_state
        length += length_git_status_block

    length_exit_code_block = 0
    length_exit_code = 0
    length_exit_code_short = 0

    length_exit_code_block += 1 # triangle
    if prompt.exit_code:
        length_exit_code += 1 + len(prompt.exit_code) + 1 # space, exit code, space

        if 'exit_code_short' in prompt:
            assert prompt.exit_code_short is not None
            assert len(prompt.exit_code) >= len(prompt.exit_code_short)

            length_exit_code_short += 1 + len(prompt.exit_code_short) + 1 # space, exit code, space
        else:
            length_exit_code_short = length_exit_code

    length_exit_code_block += length_exit_code
    length += length_exit_code_block

    length += 1 + len(prompt.style.str_postfix) # triangle, postfix

    length_exec_time_block = 0
    length_exec_time = 0
    if prompt.exec_time is not None:
        length_exec_time_block += 1 # space

        if prompt.exec_time:
            length_exec_time += len(prompt.exec_time) # execution time

        length_exec_time_block += length_exec_time
        length += length_exec_time_block

    ##############################################
    # contract prompt to fit within length limit #
    ##############################################

    status = prompt.status

    git_status = prompt.git_branch is not None
    git_branch = prompt.git_branch
    git_history = prompt.git_ahead or prompt.git_behind
    git_state = prompt.git_merging or prompt.git_untracked or prompt.git_modified or prompt.git_staged

    exit_code = prompt.exit_code
    exec_time = prompt.exec_time

    assert prompt.max_length is None or prompt.max_length > 0
    surplus = length - prompt.max_length if prompt.max_length is not None else 0

    if surplus > 0:
        surplus -= len(prompt.style.str_postfix)
        prompt.style.str_postfix = ""

        if surplus > 0:
            if 'exit_code_short' in prompt:
                surplus -= length_exit_code - length_exit_code_short
                exit_code = prompt.exit_code_short
                length_exit_code = length_exit_code_short

            if surplus > 0:
                surplus -= length_git_branch
                git_branch = ""

                if surplus > 0:
                    for i, component in enumerate(path):
                        if len(component) > 2:
                            if surplus > len(component) - 2:
                                path_omitted[i] = len(component) - 1 # always keep first character
                                surplus -= path_omitted[i] - 1 # count insertion of 'omit' character
                            else:
                                path_omitted[i] = surplus + 1 # count insertion of 'omit' character
                                surplus = 0
                                break

                    if surplus > 0:
                        surplus -= length_exec_time_block
                        exec_time = None

                        if surplus > 0:
                            surplus -= length_exit_code
                            if exit_code is not None:
                                exit_code = ""

                            if surplus > 0:
                                surplus -= len(status)
                                status = ""

    #######################################
    # construct prompt string for display #
    #######################################

    prompt_str = color1(None) # reset all text decorations

    prompt_str += color2(fg=prompt.style.col_status_fg, bg=prompt.style.col_status_bg) + " "
    prev_bg = prompt.style.col_status_bg

    if status:
        prompt_str += status + " "

    prompt_str += color2(fg=prev_bg, bg=prompt.style.col_path_bg) + TRIANGLE + " "
    prev_bg = prompt.style.col_path_bg

    path_dir_fg = prompt.style.col_path_git_dir_fg if prompt.path_git_dir_depth >= (len(path) - 1) \
            else prompt.style.col_path_dir_fg

    if path:
        for i, component, sep, omitted in zip(range(len(path)), path, path_sep, path_omitted):
            prompt_str += color1(prompt.style.col_path_sep_fg) + sep

            if omitted > 0:
                component = component[:-omitted]

            for part in re.split('(/+)', component):
                if not part:
                    continue
                elif part[0] == '/':
                    prompt_str += color1(prompt.style.col_path_nonprint_fg) + prompt.style.ch_path_nonprint * len(part)
                else:
                    prompt_str += color1(path_dir_fg) + part

            if omitted > 0:
                prompt_str += color1(prompt.style.col_path_omit_fg) + prompt.style.ch_path_omit

            if i + 1 == (len(path) - 1) - prompt.path_git_dir_depth:
                path_dir_fg = prompt.style.col_path_git_dir_fg
    else:
        prompt_str += color1(path_dir_fg) + "/"
    prompt_str += " "

    if prompt.path_dir_unreadable or prompt.path_dir_unwritable \
            or prompt.path_dir_unvisitable or prompt.path_dir_setguid or prompt.path_dir_sticky:
                if prompt.path_dir_unreadable or prompt.path_dir_unwritable or prompt.path_dir_unvisitable:
                    prompt_str += color1(prompt.style.col_path_noperm_fg)

                    if prompt.path_dir_unreadable:
                        prompt_str += prompt.style.ch_path_dir_unreadable

                    if prompt.path_dir_unwritable:
                        prompt_str += prompt.style.ch_path_dir_unwritable

                    if prompt.path_dir_unvisitable:
                        prompt_str += prompt.style.ch_path_dir_unvisitable

                if prompt.path_dir_setguid or prompt.path_dir_sticky:
                    prompt_str += color1(prompt.style.col_path_perm_fg)

                    if prompt.path_dir_setguid:
                        prompt_str += prompt.style.ch_path_dir_setguid

                    if prompt.path_dir_sticky:
                        prompt_str += prompt.style.ch_path_dir_sticky

                prompt_str += " "

    if git_status:
        prompt_str += color2(fg=prev_bg, bg=prompt.style.col_git_bg) + TRIANGLE + " "
        prev_bg = prompt.style.col_git_bg

        if git_branch:
            prompt_str += color1(prompt.style.col_git_branch_fg if not prompt.git_detached
                                 else prompt.style.col_git_detached_fg) + git_branch + " "

        if git_history:
            if prompt.git_ahead:
                prompt_str += color1(prompt.style.col_git_ahead_fg) + prompt.style.ch_git_ahead + prompt.git_ahead
            if prompt.git_behind:
                prompt_str += color1(prompt.style.col_git_behind_fg) + prompt.style.ch_git_behind + prompt.git_behind
            prompt_str += " "

        if git_state:
            if prompt.git_merging:
                prompt_str += color1(prompt.style.col_git_merging_fg) + prompt.style.ch_git_merging
            if prompt.git_untracked:
                prompt_str += color1(prompt.style.col_git_untracked_fg) + prompt.style.ch_git_untracked
            if prompt.git_modified:
                prompt_str += color1(prompt.style.col_git_modified_fg) + prompt.style.ch_git_modified
            if prompt.git_staged:
                prompt_str += color1(prompt.style.col_git_staged_fg) + prompt.style.ch_git_staged
            prompt_str += " "

    prompt_str += color2(fg=prev_bg, bg=prompt.style.col_exit_code_bg) + TRIANGLE
    prev_bg = prompt.style.col_exit_code_bg

    if exit_code:
        prompt_str += color1(prompt.style.col_exit_code_fg) + " " + exit_code + " "

    prompt_str += color2(fg=prev_bg, transparent_bg=True) + TRIANGLE
    if prompt.style.str_postfix:
        prompt_str += color1(prompt.style.col_postfix_fg) + prompt.style.str_postfix

    if exec_time is not None:
        prompt_str += " " + exec_time

    # reset all text decorations
    prompt_str += color1(None)

    return prompt_str


if __name__ == '__main__':
    print(visualize(prettify(finalize_style(parse(os.environ)))), end="")

