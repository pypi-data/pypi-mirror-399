''' opencos.tools.modelsim_ase - Used by opencos.eda for sim/elab commands w/ --tool=modelsim_ase.

Contains classes for CommandSimModelsimAse, CommandElabModelsimAse.

Note that this is for 32-bit Modelsim Student Edition. Consider using --tool=questa_fse instead.
'''

# pylint: disable=R0801 # (duplicate code in derived classes, such as if-condition return.)

import os

from opencos.tools.questa_common import CommonSimQuesta, CommonFListQuesta

class CommandSimModelsimAse(CommonSimQuesta):
    '''CommandSimModelsimAse is a command handler for: eda sim --tool=modelsim_ase'''

    _TOOL = 'modelsim_ase'
    _EXE = 'vsim'
    use_vopt = False

    def __init__(self, config: dict):
        CommonSimQuesta.__init__(self, config=config)

        # repairs: override self._TOOL, and run get_versions() again.
        self._TOOL = 'modelsim_ase'

        self.shell_command = os.path.join(self.sim_exe_base_path, 'vsim')
        self.starter_edition = True
        self.args.update({
            'tool': self._TOOL, # override
            'gui': False,
        })


        self.args_help.update({
            'vopt': (
                'Boolean to enable/disable use of vopt step prior to vsim step'
                ' Note that vopt args can be controlled with --elab-args=<value1>'
                ' --elab-args=<value2> ...'
            )
        })

    def set_tool_defines(self):
        # Update any defines from config.tools.modelsim_ase:
        self.defines.update(
            self.tool_config.get(
                'defines',
                # defaults, if not set:
                {'OC_ASSERT_PROPERTY_NOT_SUPPORTED': 1,
                 'OC_TOOL_MODELSIM_ASE': 1}
            )
        )



class CommandElabModelsimAse(CommandSimModelsimAse):
    '''CommandElabModelsimAse is a command handler for: eda elab --tool=modelsim_ase'''

    command_name = 'elab'

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True


class CommandLintModelsimAse(CommandSimModelsimAse):
    '''CommandLintModelsimAse is a command handler for: eda lint --tool=modelsim_ase'''

    command_name = 'lint'

    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-compile'] = True
        self.args['stop-after-elaborate'] = True


class CommandFListModelsimAse(CommonFListQuesta):
    '''CommandFListModelsimAse is a command handler for: eda flist --tool=modelsim_ase'''

    def __init__(self, config: dict):
        CommonFListQuesta.__init__(self, config=config)
        self._TOOL = 'questa_fse'
