''' opencos.eda_config - handles --config-yml arg, and providing a
'config' dict for use by opencos.eda, opencos.commands, and opencos.tools

Order of precedence for default value of eda arg: --config-yaml:
1) os.environ.get('EDA_CONFIG_YML', '') -- filepath to an eda_config.yml file
2) ~/.opencos-eda/EDA_CONFIG.yml
3) (package pip installed dir for opencos)/eda_config_defaults.yml
'''

import copy
import os
import argparse

import mergedeep

from opencos import util
from opencos.files import safe_shutil_which
from opencos.util import safe_emoji
from opencos.utils.markup_helpers import yaml_safe_load, yaml_safe_writer

class Defaults:
    '''Defaults is a global namespace for constants and supported features.

    Defaults.config_yml is set depending on search order for default eda_config[_defaults].yml

    Note that opencos.eda and other packages are free to set and add additonal keys to the
    "config", but the "supported_config_keys" are only what's allowed in the initial
    --config-yml=YAML_FILE
    '''

    environ_override_config_yml = ''
    home_override_config_yml = ''
    opencos_config_yml = 'eda_config_defaults.yml'
    config_yml = ''
    config_yml_set_from = ''

    supported_config_keys = set([
        'DEFAULT_HANDLERS', 'DEFAULT_HANDLERS_HELP',
        'defines',
        'dep_command_enables',
        'dep_tags_enables',
        'deps_markup_supported',
        'deps_subprocess_shell',
        'bare_plusarg_supported',
        'deps_expandvars_enable',
        'show_tool_versions',
        'dep_sub',
        'vars',
        'file_extensions',
        'command_determines_tool',
        'command_tool_is_optional',
        'command_has_subcommands',
        'tools',
        'auto_tools_order',
    ])
    supported_config_tool_keys = set([
        'exe', 'handlers',
        'requires_env', 'requires_py', 'requires_cmd', 'requires_in_exe_path',
        'requires_vsim_helper',
        'requires_vscode_extension',
        'disable-tools-multi', 'disable-auto',
        'defines',
        'log-bad-strings',
        'log-must-strings',
        'log-warning-strings',
        'sim-libraries',
        'compile-args',
        'compile-waves-args',
        'compile-waivers',
        'compile-coverage-args',
        'elab-args',
        'elab-waves-args',
        'simulate-args',
        'simulate-waves-args',
        'simulate-waivers',
        'simulate-coverage-tcl',
        'coverage-args',
    ])

EDA_OUTPUT_CONFIG_FNAME = 'eda_output_config.yml'

def set_defaults() -> None:
    '''Updates Defaults *config_yml members, sets Defaults.config_yml'''

    Defaults.environ_override_config_yml = os.environ.get(
        'EDA_CONFIG_YML', os.environ.get('EDA_CONFIG_YAML', '')
    )
    if Defaults.environ_override_config_yml and \
       os.path.isfile(Defaults.environ_override_config_yml):
        Defaults.config_yml = Defaults.environ_override_config_yml
        Defaults.config_yml_set_from = 'env EDA_CONFIG_YML'
        return

    home = os.environ.get('HOME', os.environ.get('HOMEPATH', ''))
    if home and os.path.isdir(os.path.join(home, '.opencos-eda')):
        Defaults.home_override_config_yml = [
            os.path.join(home, '.opencos-eda', 'EDA_CONFIG.yml'),
            os.path.join(home, '.opencos-eda', 'EDA_CONFIG.yaml')
        ]
        for x in Defaults.home_override_config_yml:
            if os.path.isfile(x):
                Defaults.config_yml = x
                Defaults.config_yml_set_from = 'file [$HOME|$HOMEPATH]/.opencos-eda'
                return

    # else default:
    Defaults.config_yml = Defaults.opencos_config_yml
    Defaults.config_yml_set_from = ''


set_defaults()


def find_eda_config_yml_fpath(
        filename:str, package_search_only=False, package_search_enabled=True
) -> str:
    '''Locates the filename (.yml) either from fullpath provided or from the sys.path
    (pip-installed) opencos-eda package paths.'''

    # Check fullpath, unless we're only checking the installed pacakge dir.
    if package_search_only:
        pass
    elif os.path.exists(filename):
        return os.path.abspath(filename)

    leaf_filename = os.path.split(filename)[1]

    if leaf_filename != filename:
        # filename had subdirs, and we didn't find it already.
        util.error(f'eda_config: Could not find {filename=}')
        return None

    # Search in . or pacakge installed dir
    thispath = os.path.dirname(__file__) # this is not an executable, should be in packages dir.

    if package_search_only:
        paths = [thispath]
    elif package_search_enabled:
        paths = ['', thispath]
    else:
        paths = ['']


    for dpath in paths:
        fpath = os.path.join(dpath, leaf_filename)
        if os.path.exists(fpath):
            return fpath

    util.error(f'eda_config: Could not find {leaf_filename=} in opencos within {paths=}')
    return None


def check_config(config:dict, filename='') -> None:
    '''Returns None, will util.error(..) if there are issues in 'config'

    checks for known dict keys and data types, is NOT exhaustive checking.
    '''

    # sanity checks:
    for key in config:
        if key not in Defaults.supported_config_keys:
            util.error(f'eda_config.get_config({filename=}): has unsupported {key=}' \
                       + f' {Defaults.supported_config_keys=}')

    for tool,table in config.get('tools', {}).items():
        for key in table:
            if key not in Defaults.supported_config_tool_keys:
                util.error(f'eda_config.get_config({filename=}): has unsupported {key=}' \
                           + f' in config.tools.{tool=}, ' \
                           + f' {Defaults.supported_config_tool_keys=}')


def update_config_auto_tool_order_for_tool(tool: str, config: dict) -> str:
    '''Update config entry if the value for tool is in the form 'name=/path/to/exe

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'

    Performs no update if tool has no = or : in it. Returns tool (str) w/out = in it
    '''
    return tool_try_add_to_path(tool=tool, config=config, update_config=True)


def update_config_auto_tool_order_for_tools(tools: list, config: dict) -> list:
    '''Given a list of tools and eda_config style 'config' dict, update

    the auto_tool_order (consumed by opencos.eda when --tool is not specified).
    '''
    ret = []
    for tool in tools:
        ret.append(update_config_auto_tool_order_for_tool(tool, config))
    return ret


def update_config_for_eda_safe(config) -> None:
    '''Set method to update config dict values to run in a "safe" mode'''
    config['dep_command_enables']['shell'] = False


def deps_shell_commands_enabled(config) -> bool:
    '''Get method on config to determine if DEPS.yml shell-style commands are allowed'''
    return config['dep_command_enables']['shell']


def get_config(filename) -> dict:
    '''Given an eda_config_default.yml (or --config-yml=<filename>) return a config

    dict from the filename.'''

    fpath = find_eda_config_yml_fpath(filename)
    user_config = yaml_safe_load(fpath)
    check_config(user_config, filename=filename)

    # The final thing we do is update key 'config-yml' with the full path used.
    # This way we don't have to pass around --config-yml as some special arg
    # in eda.CommandDesign.args, and eda.CommandMulti can use when re-invoking 'eda'.
    user_config['config-yml'] = fpath
    return user_config


def get_config_handle_defaults(filename) -> dict:
    '''Given a user provided --config-yml=<filename>, return a merged config with

    the existing default config.'''

    user_config = get_config(filename)
    user_config = get_config_merged_with_defaults(user_config)
    return user_config


def merge_config(dst_config:dict, overrides_config:dict, additive_strategy=False) -> None:
    '''Mutates dst_config, uses Strategy.TYPESAFE_REPLACE'''
    # TODO(drew): It would be cool if I could have Sets be additive, but oh well,
    # this gives the user more control over replacing entire lists.
    strategy = mergedeep.Strategy.TYPESAFE_REPLACE
    if additive_strategy:
        strategy = mergedeep.Strategy.TYPESAFE_ADDITIVE
    mergedeep.merge(dst_config, overrides_config, strategy=strategy)


def get_config_merged_with_defaults(config:dict) -> dict:
    '''Returns a new config that has been merged with the default config.

    The default config location is based on Defaults.config_yml (env, local, or pip
    installed location)'''

    default_fpath = find_eda_config_yml_fpath(Defaults.config_yml, package_search_only=True)
    default_config = yaml_safe_load(default_fpath)
    merge_config(default_config, overrides_config=config)
    # This technically mutated updated into default_config, so return that one:
    return default_config


def get_argparser() -> argparse.ArgumentParser:
    '''Returns an ArgumentParser, handles --config-yml=<filename> arg'''

    # re-run set_defaults() in case a --env-file overwrote Defaults.config_yml
    set_defaults()

    parser = argparse.ArgumentParser(
        prog=f'{safe_emoji("🔎 ")}opencos eda config options', add_help=False, allow_abbrev=False
    )
    parser.add_argument(
        '--config-yml', type=str, default=Defaults.config_yml,
        help=(
            f'YAML filename to use for configuration (default {Defaults.config_yml}).'
            ' Can be overriden using environmnet var EDA_CONFIG_YML=FILE, or from file'
            ' [$HOME|$HOMEPATH]/.opencos-eda/EDA_CONFIG.yml'
        )
    )
    return parser


def get_argparser_short_help() -> str:
    '''Returns a shortened help string given for arg --config-yml.'''
    return util.get_argparser_short_help(parser=get_argparser())


def get_eda_config(args:list, quiet=False) -> (dict, list):
    '''Returns an config dict and a list of args to be passed downstream
    to eda.main and eda.process_tokens.

    Handles args for:
      --config-yml=<YAMLFILE>

    This will merge the result with the default config (if overriden)
    '''
    parser = get_argparser()
    try:
        parsed, unparsed = parser.parse_known_args(args + [''])
        unparsed = list(filter(None, unparsed))
    except argparse.ArgumentError:
        util.error(f'problem attempting to parse_known_args for {args=}')

    util.debug(f'eda_config.get_eda_config: {parsed=} {unparsed=}  from {args=}')

    if parsed.config_yml:
        if not quiet:
            if parsed.config_yml != Defaults.config_yml:
                # It was set on CLI:
                util.info(f'eda_config: --config-yml={parsed.config_yml} observed')
            elif Defaults.config_yml_set_from:
                # It was picked up via env or HOME/.opencos-eda/ override:
                util.info(f'eda_config: --config-yml={parsed.config_yml} observed, from',
                          f'{Defaults.config_yml_set_from}')
        fullpath = find_eda_config_yml_fpath(parsed.config_yml)
        config = get_config(fullpath)
        if not quiet:
            util.info(f'eda_config: using config: {fullpath}')

        # Calling get_config(fullpath) will add fullpath to config['config-yml'], so the
        # arg for --config-yml does not need to be re-added.
    else:
        config = None

    if parsed.config_yml != Defaults.config_yml:
        config = get_config_merged_with_defaults(config)

    return config, unparsed


def write_eda_config_and_args(
        dirpath : str, filename: str = EDA_OUTPUT_CONFIG_FNAME,
        command_obj_ref: object = None
) -> None:
    '''Writes and eda_config style dict to dirpath/filename'''
    if command_obj_ref is None:
        return
    fullpath = os.path.join(dirpath, filename)
    data = {}
    for x in ['command_name', 'config', 'target', 'args', 'modified_args', 'defines',
              'incdirs', 'files_v', 'files_sv', 'files_vhd', 'files_cpp', 'files_sdc',
              'files_non_source']:
        # Use deep copy b/c otherwise these are references to opencos.eda.
        data[x] = copy.deepcopy(getattr(command_obj_ref, x, ''))

    # copy util.args
    data['util'] = {
        'args': util.args
    }

    # fix some burried class references in command_obj_ref.config,
    # otherwise we won't be able to safe load this yaml, so cast as str repr.
    for k, v in getattr(command_obj_ref, 'config', {}).items():
        if k == 'command_handler':
            data['config'][k] = str(v)

    yaml_safe_writer(data=data, filepath=fullpath)


def tool_arg_get_parts(tool: str) -> list:
    '''Given a tool (str or None) that may be in form <name>=/path/to/something

    Return the parts [<name>, <path>, ..]
    '''
    if not tool or ('=' not in tool and ':' not in tool):
        return [tool]

    if '=' in tool:
        parts = tool.split('=')
    else:
        parts = tool.split(':')

    return parts

def tool_arg_remove_path_information(tool: str) -> str:
    '''Given a tool (str or None) that may be in form <name>=/path/to/something

    Return the <name> only
    '''
    if not tool:
        return tool
    return tool_arg_get_parts(tool)[0]


def tool_try_add_to_path( # pylint: disable=too-many-branches
        tool: str, config: dict, update_config: bool
) -> str:
    '''Since we support --tool=<name>=/path/to/bin[/exe], attempt to prepend $PATH

    (also works for --tool=<name>:/path/to/bin[/exe] )

    with this information for this tool (which will nicely affect all subprocesses,
    but not wreck our original shell).'''

    name_path_parts = tool_arg_get_parts(tool)
    if len(name_path_parts) == 1:
        return name_path_parts[0]

    name, path_arg = name_path_parts[0:2]

    if name not in config['tools']:
        return name

    config_exe = config['tools'][name].get('exe', str())
    if isinstance(config_exe, list):
        orig_exe = config_exe[0]
    else:
        orig_exe = config_exe

    if path_arg and os.path.isfile(path_arg):
        # Someone passes us --tool=<name>=/path/to/bin/exe, remove the exe from path:
        path, exe = os.path.split(path_arg)
    elif path_arg and os.path.isdir(path_arg):
        # Someone passes us --tool=<name>=/path/to/bin/ (did not have exe)
        path, exe = path_arg, orig_exe
    else:
        path, exe = '', ''

    if not path or not exe:
        util.error(f'Can not find path or exe for --tool={tool}: {name=} path={path_arg}')
        return name

    path = os.path.abspath(path)
    if os.path.isdir(path):
        paths = os.environ.get('PATH', '').split(':')
        if path not in paths:
            util.info(f'--tool={tool} has path information, prepending PATH with: {path}')
            os.environ['PATH'] = path + ':' + os.environ.get('PATH', '')
        else:
            util.info(f'--tool={tool} has path information, but {path} already in $PATH')

    user_exe = os.path.join(path, exe)
    if not os.access(user_exe, os.X_OK):
        util.error(f'--tool setting for {tool}: {user_exe} is not an executable')
        return name

    user_exe = safe_shutil_which(user_exe)

    if update_config:
        if isinstance(config_exe, list):
            config['tools'][name]['exe'][0] = user_exe
            for index,value in enumerate(config_exe[1:]):
                # update all entries, if we can, if the value is also in 'path'
                # from our set --tool=Name=path/exe
                new_value = os.path.join(path, os.path.split(value)[1])
                if os.path.exists(new_value) and safe_shutil_which(new_value) and \
                   os.access(new_value, os.X_OK):
                    config['tools'][name]['exe'][index] = new_value
        else:
            config['tools'][name]['exe'] = user_exe
        util.debug(f'For {tool=}, tools config entry updated')

    util.debug(f'For {tool=}, final {user_exe=}')

    return name
