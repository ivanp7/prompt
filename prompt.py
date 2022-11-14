#!/bin/python

import os
import re


##############
### status ###
##############

DEFAULT_COLOR_STATUS_NON_ROOT_FG = 248 # style['col_status_nr_fg']
DEFAULT_COLOR_STATUS_NON_ROOT_BG = 238 # style['col_status_nr_bg']

DEFAULT_COLOR_STATUS_ROOT_FG = 236 # style['col_status_r_fg']
DEFAULT_COLOR_STATUS_ROOT_BG = 202 # style['col_status_r_bg']

############
### path ###
############

DEFAULT_CHAR_PATH_OMIT = "▶"     # style['ch_path_omit']
DEFAULT_CHAR_PATH_NONPRINT = "_" # style['ch_path_nonprint']

DEFAULT_COLOR_PATH_DIR_FG = 254      # style['col_path_dir_fg']
DEFAULT_COLOR_PATH_SEP_FG = 236      # style['col_path_sep_fg']
DEFAULT_COLOR_PATH_OMIT_FG = 200     # style['col_path_omit_fg']
DEFAULT_COLOR_PATH_NONPRINT_FG = 196 # style['col_path_nonprint_fg']
DEFAULT_COLOR_PATH_BG = 240          # style['col_path_bg']

##################
### git status ###
##################

DEFAULT_CHAR_GIT_AHEAD = "↑"   # style['ch_git_ahead']
DEFAULT_CHAR_GIT_BEHIND = "↓"  # style['ch_git_behind']
DEFAULT_CHAR_GIT_MERGING = "↕" # style['ch_git_staged']

DEFAULT_CHAR_GIT_UNTRACKED = "•" # style['ch_git_untracked']
DEFAULT_CHAR_GIT_MODIFIED = "•"  # style['ch_git_modified']
DEFAULT_CHAR_GIT_STAGED = "•"    # style['ch_git_staged']

DEFAULT_COLOR_GIT_BRANCH_FG = 228    # style['col_git_branch_fg']
DEFAULT_COLOR_GIT_AHEAD_FG = 254     # style['col_git_ahead_fg']
DEFAULT_COLOR_GIT_BEHIND_FG = 166    # style['col_git_behind_fg']
DEFAULT_COLOR_GIT_MERGING_FG = 33    # style['col_git_merging_fg']
DEFAULT_COLOR_GIT_UNTRACKED_FG = 160 # style['col_git_untracked_fg']
DEFAULT_COLOR_GIT_MODIFIED_FG = 214  # style['col_git_modified_fg']
DEFAULT_COLOR_GIT_STAGED_FG = 34     # style['col_git_staged_fg']
DEFAULT_COLOR_GIT_BG = 238           # style['col_git_bg']

#################
### exit code ###
#################

DEFAULT_CHAR_EXIT_CODE_SEP = '·' # style['ch_exit_code_sep']

DEFAULT_COLOR_EXIT_CODE_SUCCESS_FG = 254 # style['col_exit_code_success_fg']
DEFAULT_COLOR_EXIT_CODE_SUCCESS_BG = 35 # style['col_exit_code_success_bg']

DEFAULT_COLOR_EXIT_CODE_FAIL_FG = 252   # style['col_exit_code_fail_fg']
DEFAULT_COLOR_EXIT_CODE_FAIL_BG = 124 # style['col_exit_code_fail_bg']

######################
### execution time ###
######################

DEFAULT_COLOR_EXEC_TIME_FG = 244 # style['col_exec_time_fg']
DEFAULT_COLOR_EXEC_TIME_BG = 238 # style['col_exec_time_bg']

###############
### postfix ###
###############

DEFAULT_STRING_POSTFIX = "" # style['str_postfix']

DEFAULT_COLOR_POSTFIX_FG = 244 # style['col_postfix_fg']

###############


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


class Prompt:
    """Shell prompt.
    """
    def __init__(self, status: str, path: str,
                 git_branch: str=None,
                 git_ahead: str=None, git_behind: str=None, git_merging: bool=False,
                 git_untracked: bool=False, git_modified: bool=False, git_staged: bool=False,
                 exit_code: str=None, exec_time: str=None,
                 root: bool=False, max_length: str=None,
                 style: dict={}):
        """Construct prompt.
        """
        self._style = style

        self._status = status
        self._path = path
        self._git_branch = git_branch
        self._git_ahead = git_ahead
        self._git_behind = git_behind
        self._git_merging = git_merging
        self._git_untracked = git_untracked
        self._git_modified = git_modified
        self._git_staged = git_staged
        self._exit_code, self._exit_code_suffix = self._prettify_exit_code(exit_code)
        self._exit_success = exit_code == "0" or not exit_code
        self._exec_time = self._prettify_exec_time(exec_time)

        self._root = root
        self._max_length = int(max_length) if max_length else None

        assert self._max_length is None or self._max_length > 0

        self._construct()

    def __str__(self) -> str:
        """Return string representation of prompt.
        """
        return self._str

    @property
    def status(self) -> str:
        """Return status.
        """
        return self._status

    @property
    def path(self) -> str:
        """Return path.
        """
        return self._path

    @property
    def git_branch(self) -> str:
        """Return git branch name.
        """
        return self._git_branch

    @property
    def git_ahead(self) -> str:
        """Return number of commits local repo is ahead of remote.
        """
        return self._git_ahead

    @property
    def git_behind(self) -> str:
        """Return number of commits local repo is behind of remote.
        """
        return self._git_behind

    @property
    def git_merging(self) -> str:
        """Return True if local repo is in merging state, otherwise False.
        """
        return self._git_merging

    @property
    def git_untracked(self) -> str:
        """Return True if local repo has untracked files, otherwise False.
        """
        return self._git_untracked

    @property
    def git_modified(self) -> str:
        """Return True if local repo has modified files, otherwise False.
        """
        return self._git_modified

    @property
    def git_staged(self) -> str:
        """Return True if local repo has staged files, otherwise False.
        """
        return self._git_staged

    @property
    def exit_code(self) -> str:
        """Return exit code.
        """
        return self._exit_code

    @property
    def exec_time(self) -> str:
        """Return execution time.
        """
        return self._exec_time

    @property
    def root(self) -> str:
        """Return True if prompt is for root user, otherwise False.
        """
        return self._root

    @property
    def max_length(self) -> str:
        """Return upper limit for prompt length.
        """
        return self._max_length

    @property
    def style(self) -> str:
        """Return prompt style.
        """
        return self._style

    def _prettify_exit_code(self, exit_code: str) -> tuple[str, str]:
        """Prettify exit code.
        """
        if exit_code is None:
            return None, ""

        char_sep = self._style.get('ch_exit_code_sep', DEFAULT_CHAR_EXIT_CODE_SEP)
        assert len(char_sep) == 1

        known_exit_codes = {
                "1": "GENERAL",
                "2": "MISUSE",
                "126": "NOTEXEC",
                "127": "NOTFOUND",
                # signals #
                "129": "SIGHUP",
                "130": "SIGINT",
                "131": "SIGQUIT",
                "132": "SIGILL",
                "133": "SIGTRAP",
                "134": "SIGABRT",
                "135": "SIGBUS",
                "136": "SIGFPE",
                "137": "SIGKILL",
                "138": "SIGUSR1",
                "139": "SIGSEGV",
                "140": "SIGUSR2",
                "141": "SIGPIPE",
                "142": "SIGALRM",
                "143": "SIGTERM",
                "144": "SIGSTKFLT",
                "145": "SIGCHLD",
                "146": "SIGCONT",
                "147": "SIGSTOP",
                "148": "SIGTSTP",
                "149": "SIGTTIN",
                "150": "SIGTTOU",
                "151": "SIGURG",
                "152": "SIGXCPU",
                "153": "SIGXFSZ",
                "154": "SIGVTALRM",
                "155": "SIGPROF",
                "156": "SIGWINCH",
                "157": "SIGIO",
                "158": "SIGPWR",
                "159": "SIGSYS",
                "162": "SIGRTMIN"}

        if exit_code == "0":
            return "", ""
        elif exit_code in known_exit_codes:
            return exit_code, char_sep + known_exit_codes[exit_code]
        else:
            return exit_code, ""

    def _prettify_exec_time(self, exec_time: str) -> str:
        """Prettify execution time.
        """
        if not exec_time:
            return None

        seconds = int(exec_time)
        assert seconds >= 0

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

    def _construct(self) -> None:
        """Construct prompt string for display.
        """
        TRIANGLE = ""

        #######################################
        # read style settings for this prompt #
        #######################################

        if not self._root:
            COLOR_STATUS_FG = self._style.get('col_status_nr_fg', DEFAULT_COLOR_STATUS_NON_ROOT_FG)
            COLOR_STATUS_BG = self._style.get('col_status_nr_bg', DEFAULT_COLOR_STATUS_NON_ROOT_BG)
        else:
            COLOR_STATUS_FG = self._style.get('col_status_r_fg', DEFAULT_COLOR_STATUS_ROOT_FG)
            COLOR_STATUS_BG = self._style.get('col_status_r_bg', DEFAULT_COLOR_STATUS_ROOT_BG)

        CHAR_PATH_OMIT = self._style.get('ch_path_omit', DEFAULT_CHAR_PATH_OMIT)
        CHAR_PATH_NONPRINT = self._style.get('ch_path_nonprint', DEFAULT_CHAR_PATH_NONPRINT)

        assert len(CHAR_PATH_OMIT) == 1
        assert len(CHAR_PATH_NONPRINT) == 1

        COLOR_PATH_DIR_FG = self._style.get('col_path_dir_fg', DEFAULT_COLOR_PATH_DIR_FG)
        COLOR_PATH_SEP_FG = self._style.get('col_path_sep_fg', DEFAULT_COLOR_PATH_SEP_FG)
        COLOR_PATH_OMIT_FG = self._style.get('col_path_omit_fg', DEFAULT_COLOR_PATH_OMIT_FG)
        COLOR_PATH_NONPRINT_FG = self._style.get('col_path_nonprint_fg', DEFAULT_COLOR_PATH_NONPRINT_FG)
        COLOR_PATH_BG = self._style.get('col_path_bg', DEFAULT_COLOR_PATH_BG)

        CHAR_GIT_AHEAD = self._style.get('ch_git_ahead', DEFAULT_CHAR_GIT_AHEAD)
        CHAR_GIT_BEHIND = self._style.get('ch_git_behind', DEFAULT_CHAR_GIT_BEHIND)
        CHAR_GIT_MERGING = self._style.get('ch_git_merging', DEFAULT_CHAR_GIT_MERGING)

        CHAR_GIT_UNTRACKED = self._style.get('ch_git_untracked', DEFAULT_CHAR_GIT_UNTRACKED)
        CHAR_GIT_MODIFIED = self._style.get('ch_git_modified', DEFAULT_CHAR_GIT_MODIFIED)
        CHAR_GIT_STAGED = self._style.get('ch_git_staged', DEFAULT_CHAR_GIT_STAGED)

        assert len(CHAR_GIT_AHEAD) == 1
        assert len(CHAR_GIT_BEHIND) == 1
        assert len(CHAR_GIT_MERGING) == 1

        assert len(CHAR_GIT_UNTRACKED) == 1
        assert len(CHAR_GIT_MODIFIED) == 1
        assert len(CHAR_GIT_STAGED) == 1

        COLOR_GIT_BRANCH_FG = self._style.get('col_git_branch_fg', DEFAULT_COLOR_GIT_BRANCH_FG)
        COLOR_GIT_AHEAD_FG = self._style.get('col_git_ahead_fg', DEFAULT_COLOR_GIT_AHEAD_FG)
        COLOR_GIT_BEHIND_FG = self._style.get('col_git_behind_fg', DEFAULT_COLOR_GIT_BEHIND_FG)
        COLOR_GIT_MERGING_FG = self._style.get('col_git_merging_fg', DEFAULT_COLOR_GIT_MERGING_FG)
        COLOR_GIT_UNTRACKED_FG = self._style.get('col_git_untracked_fg', DEFAULT_COLOR_GIT_UNTRACKED_FG)
        COLOR_GIT_MODIFIED_FG = self._style.get('col_git_modified_fg', DEFAULT_COLOR_GIT_MODIFIED_FG)
        COLOR_GIT_STAGED_FG = self._style.get('col_git_staged_fg', DEFAULT_COLOR_GIT_STAGED_FG)
        COLOR_GIT_BG = self._style.get('col_git_bg', DEFAULT_COLOR_GIT_BG)

        if self._exit_success:
            COLOR_EXIT_CODE_FG = self._style.get('col_exit_code_success_fg', DEFAULT_COLOR_EXIT_CODE_SUCCESS_FG)
            COLOR_EXIT_CODE_BG = self._style.get('col_exit_code_success_bg', DEFAULT_COLOR_EXIT_CODE_SUCCESS_BG)
        else:
            COLOR_EXIT_CODE_FG = self._style.get('col_exit_code_fail_fg', DEFAULT_COLOR_EXIT_CODE_FAIL_FG)
            COLOR_EXIT_CODE_BG = self._style.get('col_exit_code_fail_bg', DEFAULT_COLOR_EXIT_CODE_FAIL_BG)

        if self._exit_code is not None:
            COLOR_EXEC_TIME_FG = COLOR_EXIT_CODE_BG
        else:
            COLOR_EXEC_TIME_FG = self._style.get('col_exec_time_fg', DEFAULT_COLOR_EXEC_TIME_FG)
        COLOR_EXEC_TIME_BG = self._style.get('col_exec_time_bg', DEFAULT_COLOR_EXEC_TIME_BG)

        POSTFIX = self._style.get('str_postfix', DEFAULT_STRING_POSTFIX)

        if self._exit_code is not None:
            POSTFIX_FG = COLOR_EXIT_CODE_BG
        else:
            POSTFIX_FG = self._style.get('col_postfix_fg', DEFAULT_COLOR_POSTFIX_FG)

        ################################
        # calculate full prompt length #
        ################################

        length = 1 # space

        if self._status:
            length += len(self._status) + 1 # status, space

        # split by slashes, remove empty parts, replace non-printable characters with temporary slashes
        path = [''.join([ch if ord(ch) >= 32 and ord(ch) != 127 else '/' for ch in component])
                for component in self._path.split('/') if component]
        if path:
            length += 1 + 1 + sum([1 + len(s) for s in path]) + 1 # triangle, space, path, space

            path_sep = [f"{i%10}" for i in range(len(path), 0, -1)]
            path_omitted = [0] * len(path)
        else:
            length += 1 + 1 + 1 + 1 # triangle, space, slash, space

        length_git_status_block = 0
        length_git_branch = 0
        length_git_history = 0
        length_git_state = 0
        if self._git_branch is not None:
            length_git_status_block += 1 + 1 # triangle, space

            length_git_branch = len(self._git_branch) + 1 # git branch, space

            if self._git_ahead or self._git_behind:
                if self._git_ahead:
                    length_git_history += 1 + len(self._git_ahead) # character, ahead
                if self._git_behind:
                    length_git_history += 1 + len(self._git_behind) # character, behind
                length_git_history += 1 # space

            if self._git_merging or self._git_untracked or self._git_modified or self._git_staged:
                if self._git_merging:
                    length_git_state += 1 # character
                if self._git_untracked:
                    length_git_state += 1 # character
                if self._git_modified:
                    length_git_state += 1 # character
                if self._git_staged:
                    length_git_state += 1 # character
                length_git_state += 1 # space

            length_git_status_block += length_git_branch + length_git_history + length_git_state
            length += length_git_status_block

        length_exit_code_block = 0
        length_exit_code = 0
        length_exit_code_suffix = 0
        if self._exit_code is not None:
            length_exit_code_block += 1 + 1 # triangle, space

            if self._exit_code:
                length_exit_code += len(self._exit_code) + 1 # exit code, space
                length_exit_code_suffix += len(self._exit_code_suffix)

            length_exit_code_block += length_exit_code + length_exit_code_suffix
            length += length_exit_code_block

        length_exec_time_block = 0
        length_exec_time = 0
        if self._exec_time is not None:
            length_exec_time_block += 1 + 1 # triangle, space

            if self._exec_time:
                length_exec_time += len(self._exec_time) + 1 # execution time, space

            length_exec_time_block += length_exec_time
            length += length_exec_time_block

        length += 1 + len(POSTFIX) # triangle, postfix

        ##############################################
        # contract prompt to fit within length limit #
        ##############################################

        status = self._status

        git_status = self._git_branch is not None
        git_branch = self._git_branch
        git_history = self._git_ahead or self._git_behind
        git_state = self._git_merging or self._git_untracked or self._git_modified or self._git_staged

        exit_code = self._exit_code
        exit_code_suffix = self._exit_code_suffix
        exec_time = self._exec_time

        surplus = length - self._max_length if self._max_length is not None else 0

        if surplus > 0:
            surplus -= len(POSTFIX)
            POSTFIX = ""

            if surplus > 0:
                surplus -= length_exit_code_suffix
                exit_code_suffix = ""

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

        self._str = color1(None) # reset all text decorations

        self._str += color2(fg=COLOR_STATUS_FG, bg=COLOR_STATUS_BG) + " "
        prev_bg = COLOR_STATUS_BG

        if status:
            self._str += status + " "

        self._str += color2(fg=prev_bg, bg=COLOR_PATH_BG) + TRIANGLE + " "
        prev_bg = COLOR_PATH_BG

        if path:
            for component, sep, omitted in zip(path, path_sep, path_omitted):
                self._str += color1(COLOR_PATH_SEP_FG) + sep

                if omitted > 0:
                    component = component[:-omitted]

                for part in re.split('(/+)', component):
                    if not part:
                        continue
                    elif part[0] == '/':
                        self._str += color1(COLOR_PATH_NONPRINT_FG) + CHAR_PATH_NONPRINT * len(part)
                    else:
                        self._str += color1(COLOR_PATH_DIR_FG) + part

                if omitted > 0:
                    self._str += color1(COLOR_PATH_OMIT_FG) + CHAR_PATH_OMIT
        else:
            self._str += color1(COLOR_PATH_DIR_FG) + "/"
        self._str += " "

        if git_status:
            self._str += color2(fg=prev_bg, bg=COLOR_GIT_BG) + TRIANGLE + " "
            prev_bg = COLOR_GIT_BG

            if git_branch:
                self._str += color1(COLOR_GIT_BRANCH_FG) + git_branch + " "

            if git_history:
                if self._git_ahead:
                    self._str += color1(COLOR_GIT_AHEAD_FG) + CHAR_GIT_AHEAD + self._git_ahead
                if self._git_behind:
                    self._str += color1(COLOR_GIT_BEHIND_FG) + CHAR_GIT_BEHIND + self._git_behind
                self._str += " "

            if git_state:
                if self._git_merging:
                    self._str += color1(COLOR_GIT_MERGING_FG) + CHAR_GIT_MERGING
                if self._git_untracked:
                    self._str += color1(COLOR_GIT_UNTRACKED_FG) + CHAR_GIT_UNTRACKED
                if self._git_modified:
                    self._str += color1(COLOR_GIT_MODIFIED_FG) + CHAR_GIT_MODIFIED
                if self._git_staged:
                    self._str += color1(COLOR_GIT_STAGED_FG) + CHAR_GIT_STAGED
                self._str += " "

        if exit_code is not None:
            self._str += color2(fg=prev_bg, bg=COLOR_EXIT_CODE_BG) + TRIANGLE + " "
            prev_bg = COLOR_EXIT_CODE_BG

            if exit_code:
                self._str += color1(COLOR_EXIT_CODE_FG) + exit_code + exit_code_suffix + " "

        if exec_time is not None:
            self._str += color2(fg=prev_bg, bg=COLOR_EXEC_TIME_BG) + TRIANGLE + " "
            prev_bg = COLOR_EXEC_TIME_BG

            if exec_time:
                self._str += color1(COLOR_EXEC_TIME_FG) + exec_time + " "

        self._str += color2(fg=prev_bg, transparent_bg=True) + TRIANGLE
        if POSTFIX:
            self._str += color1(POSTFIX_FG) + POSTFIX

        # reset all text decorations
        self._str += color1(None)


if __name__ == '__main__':
    print(str(Prompt(os.environ.get('PROMPT_STATUS', ""),
                     os.environ['PROMPT_PATH'] if 'PROMPT_PATH' in os.environ else os.environ['PWD'],
                     git_branch=os.environ.get('PROMPT_GIT_BRANCH', None),
                     git_ahead=os.environ.get('PROMPT_GIT_AHEAD', None),
                     git_behind=os.environ.get('PROMPT_GIT_BEHIND', None),
                     git_merging='PROMPT_GIT_MERGING' in os.environ,
                     git_untracked='PROMPT_GIT_UNTRACKED' in os.environ,
                     git_modified='PROMPT_GIT_MODIFIED' in os.environ,
                     git_staged='PROMPT_GIT_STAGED' in os.environ,
                     exit_code=os.environ.get('PROMPT_EXIT_CODE', None),
                     exec_time=os.environ.get('PROMPT_EXEC_TIME', None),
                     root='PROMPT_ROOT' in os.environ,
                     max_length=os.environ.get('PROMPT_MAX_LENGTH', None))))

