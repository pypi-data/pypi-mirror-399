'''Because so many tools use the exe vsim, I don't want to run `vsim -version` N times for N
tools each to figure out if it's full-Questa, Modelsim, QuestaFSE, or Riviera.

Instead, eda.py can call this once, and then query if this tool exists when running
opencos.eda.auto_tool_setup(..)
'''

import os
import subprocess

from opencos.files import safe_shutil_which
from opencos.util import debug

INIT_HAS_RUN = False  # pylint: disable=invalid-name
TOOL_PATH = {
    'riviera': None,
    'modelsim_ase': None,
    'questa' : None,
    'questa_fe' : None,
    'questa_fse': None
}

def found() -> str:
    '''Returns the found tool, or blank str'''
    for k,v in TOOL_PATH.items():
        if k and v:
            return k
    return ''

def init_get_version(dirpath: str) -> None:
    '''Runs vsim -version using vsim_path, updates TOOL_PATH'''

    vsim_path = safe_shutil_which(os.path.join(dirpath, 'vsim'))
    if not os.access(vsim_path, os.X_OK):
        debug(f'{vsim_path} is not executable')
        vsim_path = ''

    if not vsim_path:
        return # didn't find a valid vsim exe in dirpath (Windows names included)

    proc = None
    try:
        proc = subprocess.run([vsim_path, '-version'], capture_output=True, check=False)
    except Exception as e:
        debug(f'{vsim_path} -version: exception {e}')

    if proc is None or proc.returncode != 0:
        debug(f'{vsim_path} returncode non-zero: {proc=}')
        return

    stdout_str_lower = proc.stdout.decode('utf-8', errors='replace').lower()
    dirpath = os.path.abspath(dirpath)
    settool = None

    if all(x in stdout_str_lower for x in ('starter', 'modelsim', 'fpga')):
        settool = 'modelsim_ase'
    elif all(x in stdout_str_lower for x in ('starter', 'questa', 'fpga')):
        settool = 'questa_fse'
    elif all(x in stdout_str_lower for x in ('questa', 'fpga')):
        settool = 'questa_fe'
    elif all(x in stdout_str_lower for x in ('riviera', 'aldec')):
        settool = 'riviera'
    elif 'questa' in stdout_str_lower:
        settool = 'questa'

    debug(f'{vsim_path=} {settool=} from version')

    if settool:
        TOOL_PATH[settool] = vsim_path


def init() -> None:
    '''Sets INIT_HAS_RUN=True (only runs once) and updates TOOL_PATH[tool]'''
    global INIT_HAS_RUN # pylint: disable=global-statement

    if INIT_HAS_RUN:
        return

    INIT_HAS_RUN = True
    vsim_path = safe_shutil_which('vsim') # It might be vsim.EXE in Windows.
    debug(f'vsim_helper: found vsim executable {vsim_path}')

    if not vsim_path:
        return

    path_env = os.environ.get('PATH', '')
    paths = path_env.split(':')

    for path in paths:
        if not os.path.isdir(path):
            continue
        files = os.listdir(path)
        if any(x in files for x in ('vsim', 'vsim.exe', 'vsim.bat')):
            debug(f'vsim_helper: found in PATH: vsim executable {vsim_path} in {path}')
            init_get_version(dirpath=path)

    debug(f'vsim_helper: {TOOL_PATH=}')
