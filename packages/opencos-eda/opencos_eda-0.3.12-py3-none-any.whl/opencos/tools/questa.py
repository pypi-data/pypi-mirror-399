''' opencos.tools.questa - Used by opencos.eda for sim/elab commands w/ --tool=questa.

Contains classes for CommandSimQuesta, CommandElabQuesta.
For: Questa Edition-64 vsim 20XX.X Simulator

'''

# pylint: disable=R0801 # (setting similar, but not identical, self.defines key/value pairs)

# TODO(drew): fix these pylint eventually:
# pylint: disable=too-many-branches, too-many-ancestors

import os

from opencos.tools.questa_common import CommonSimQuesta, CommonFListQuesta


class CommandSimQuesta(CommonSimQuesta):
    '''CommandSimQuesta is a command handler for: eda sim --tool=questa

    Note this inherits 99% from CommonSimQuesta for command handling
    '''
    _TOOL = 'questa'
    _EXE = 'vsim'
    use_vopt = True

    def __init__(self, config: dict):
        # this will setup with self._TOOL = questa, optionally repair it later
        CommonSimQuesta.__init__(self, config=config)

        # repairs: override self._TOOL, and run get_versions() again.
        self._TOOL = 'questa'

        self.shell_command = os.path.join(self.sim_exe_base_path, 'vsim')
        self.starter_edition = False
        self.args.update({
            'tool': self._TOOL, # override
            'gui': False,
        })


    def set_tool_defines(self):
        '''Override from questa.ToolQuesta'''
        # Update any defines from config.tools.questa_fse:
        self.defines.update(
            self.tool_config.get(
                'defines',
                # defaults, if not set:
                {
                 'OC_TOOL_QUESTA': 1
                }
            )
        )


class CommandElabQuesta(CommandSimQuesta):
    '''CommandElabQuesta is a command handler for: eda elab --tool=questa'''

    command_name = 'elab'

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True


class CommandLintQuesta(CommandSimQuesta):
    '''CommandLintQuesta is a command handler for: eda lint --tool=questa'''

    command_name = 'lint'

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-compile'] = True
        self.args['stop-after-elaborate'] = True


class CommandFListQuesta(CommonFListQuesta):
    '''CommandFListQuesta is a command handler for: eda flist --tool=questa'''

    def __init__(self, config: dict):
        CommonFListQuesta.__init__(self, config=config)
        self._TOOL = 'questa'
