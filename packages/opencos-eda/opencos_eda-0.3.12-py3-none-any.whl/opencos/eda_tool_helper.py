''' opencos.eda_tool_helper -- used by pytests and other checks to see if tools are loaded

which helps determine if a pytest is runnable for a given tool, or should be skipped.
Does this without calling `eda` or eda.main(..)

Example uses:
    from opencos import eda_tool_helper
    cfg, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()
    assert 'verilator' in tools_loaded

'''

from importlib import import_module

from opencos import eda_config, util
from opencos.util import Colors
from opencos.utils import str_helpers

# Used by pytest, so we can skip tests if tools aren't present.

def get_config_and_tools_loaded( # pylint: disable=dangerous-default-value
        quiet: bool = False, args: list = []
) -> (dict, set):
    '''Returns config dict and set tools_loaded, given the found config.

    Can BYO args such as --config-yml=MY_OWN_EDA_CONFIG.yml
    '''

    # We have to figure out what tools are avaiable w/out calling eda.main,
    # so we can get some of these using eda_config.get_eda_config()
    config, _ = eda_config.get_eda_config(args=args, quiet=quiet)

    # only import 'eda' here so that other methods in this pymodule can be used
    # within eda, etc, if you already have a valid config or tools_loaded.
    eda = import_module("opencos.eda")
    config = eda.init_config(config=config, quiet=quiet)
    tools_loaded = config.get('tools_loaded', set()).copy()

    return config, tools_loaded


def get_all_handler_commands(config=None, tools_loaded=None) -> dict:
    '''Given a config and tools_loaded (or if not supplied uses defaults) returns a dict

    of { <command>: [list of tools that run that command, in auto-tool-order] }.

    For example:
       { "sim": ["verilator", "vivado"],
         "elab": ["slang", "verilator", ...], ...
       }
    '''
    all_handler_commands = {}

    if config is None or tools_loaded is None:
        config, tools_loaded = get_config_and_tools_loaded()

    assert isinstance(config, dict)
    assert isinstance(tools_loaded, set)

    # Let's re-walk auto_tools_order to get this ordered per eda command:
    for command, tools_list in config.get('auto_tools_order', {}).items():

        for tool in tools_list:
            entry = config.get('tools', {}).get(tool, {})
            assert entry, f'{command=} in auto_tools_order {tool=} not present in tools'

            if tool not in tools_loaded:
                continue

            if entry.get('disable-tools-multi', False):
                # Flagged as do-not-add when running eda command: tools-multi
                util.debug(f'eda_tool_helper.py -- skipping {tool=} it is set with flag',
                           'disable-tools-multi in config')
                continue

            if command in entry.get('handlers', {}):
                if command not in all_handler_commands:
                    # create ordered list from config.
                    all_handler_commands[command] = list([tool])
                else:
                    all_handler_commands[command].append(tool)

    return all_handler_commands


def get_handler_tool_version(tool: str, eda_command: str, config: dict) -> str:
    '''Attempts to get a Command Handler's version given tool + eda_command'''

    entry = config['tools'].get(tool, {})
    if not entry:
        return ''

    handler_name = entry.get('handlers', {}).get(eda_command, '')
    if not handler_name:
        return ''

    module = util.import_class_from_string(handler_name)
    obj = module(config=config)

    # Some command classes like CommandWaves, don't have get_versions(), but
    # have get_versions_of_tool():
    if getattr(obj, 'get_versions_of_tool', None):
        return obj.get_versions_of_tool(tool)

    # Note that Tool.get_versions() is supposed to be 'fast', we don't always
    # run the tool if the 'exe -version' takes too long.
    if getattr(obj, 'get_versions', None):
        return obj.get_versions()

    return ''



def get_handler_info_with_versions( # pylint: disable=too-many-branches
        config: dict | None = None,
        include_commands: bool = True,
        sort: bool = True
) -> str:
    '''Creates and returns a dict of

    {'commands': (what tools/versions can run them),
     'tools': (what version and what commands they can run)
    }

    for arg 'config' you may use:

    config, tools_loaded = get_config_and_tools_loaded()
    '''

    if not config:
        config, tools_loaded = get_config_and_tools_loaded()
    else:
        tools_loaded = list(config.get('tools_loaded', set()))

    eda_commands = list(config.get('DEFAULT_HANDLERS', {}).keys())
    show_versions = config.get('show_tool_versions', False)

    info = {
        'tools': {},
    }


    if not show_versions:
        for tool, path in config.get('auto_tools_found', {}).items():
            info['tools'][tool] = {
                'path': path
            }
        return info


    if include_commands:
        info.update({
            'commands': {}
        })
        for eda_command in eda_commands:
            info['commands'][eda_command] = {} # init

    for tool in tools_loaded:

        if include_commands:
            info['tools'][tool] = {
                'version': '',
                'commands': [],
            }
        else:
            info['tools'][tool] = {
                'version': '',
            }

        for eda_command in eda_commands:

            if not include_commands and info['tools'][tool]['version']:
                # version is already set, and we're not doing for all commands:
                break

            # Note that if you have a generic handler, or a tool that has
            # several handlers with more than one Tool class, that all can return a
            # non blank-str version, you may have problems.
            ver = get_handler_tool_version(
                tool=tool, eda_command=eda_command, config=config
            )

            if not ver:
                continue

            info['tools'][tool]['version'] = ver

            if include_commands:
                info['commands'][eda_command][tool] = ver
                info['tools'][tool]['commands'].append(eda_command)

    for tool, _ in info['tools'].items():
        if tool in config.get('auto_tools_found', {}):
            info['tools'][tool]['path'] = config['auto_tools_found'][tool]

    # return the info dict with 'tools' and 'commands' entries sorted:
    if sort:
        for key in list(info.keys()):
            if info[key]:
                info[key] = dict(sorted(info[key].items()))

    return info


def pretty_info_handler_tools(
        info: dict | None = None, config: dict | None = None, command: str | None = ''
) -> None:
    '''Pretty print (via util.info) the result from get_handler_info_with_versions()

    if info is None or empty, will use config to run get_handler_info_with_versions(..)

    Does not include commands
    '''

    if not info:
        info = get_handler_info_with_versions(config=config, include_commands=False, sort=True)

    if not info.get('tools', {}):
        # No tools detected
        if command and command in config.get('command_tool_is_optional', []):
            # but this command doesn't need tools
            return

        # if command omitted, or command may need tools, print that we don't have any
        util.info('No tools detected!', color=Colors.yellow)
        return

    show_versions = any('version' in dvalue for dvalue in info['tools'].values())

    tools_rows = [
        ['--Detected tool--', '--Path--'] # Header row.
    ]

    if show_versions:
        tools_rows[0].append('--Version--')

    for _tool, dvalue in info['tools'].items():
        path = dvalue.get("path", "")
        if path:
            path = f'({path})'

        if show_versions:
            version = dvalue.get("version", "")
            # will defer printing again, so we can put them into aligned columns:
            tools_rows.append([_tool, path, version])
        else:
            tools_rows.append([_tool, path])


    # Finally, print detected tools:
    for rownum, row in enumerate(str_helpers.pretty_2dlist_columns(
            tools_rows, return_as_2d_list=True, header_row_centered=False)):
        if rownum == 0:
            util.info(f'{Colors.bgreen}{"".join(row)}')
        else:
            # get the results in a padded 2D list so we can colorize the tool (index 0)
            util.info(f'{Colors.bgreen}{row[0]}{Colors.normal}{Colors.cyan}' \
                      + ''.join(row[1:]))
