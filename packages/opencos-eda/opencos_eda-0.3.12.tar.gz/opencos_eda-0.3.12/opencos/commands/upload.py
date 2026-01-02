'''opencos.commands.upload - Base class command handler for: eda upload ...

Intended to be overriden by Tool based classes (such as CommandUploadVivado, etc)
'''

import os
import re
from datetime import datetime
from pathlib import Path

from opencos.eda_base import Command, Tool
from opencos.util import Colors, debug, info, warning, safe_emoji, import_class_from_string


class CommandUpload(Command):
    '''Base class command handler for: eda upload ...

    If a --tool arg is not specified, this is the default handler for 'eda upload'
    and will attempt to choose a derived class based on the bit files found
    '''

    command_name = 'upload'

    # SUPPORTED_TOOLS is used
    SUPPORTED_TOOLS = {
        'vivado': ['.bit'],
        'quartus': ['.sof'],
    }
    BIT_EXT_TO_TOOL = {}

    # Child classes can set SUPPORTED_BIT_EXT = ['.bit', ..] because they
    # should only represent one tool
    SUPPORTED_BIT_EXT = [item for value in SUPPORTED_TOOLS.values() for item in value]


    def __init__(self, config: dict):
        Command.__init__(self, config=config)
        self.unparsed_args = []

        self.args.update({
            'bitfile': "",
            'list-bitfiles': False,
        })

        self.str_ext = '/'.join(self.SUPPORTED_BIT_EXT).replace('.', '').upper()

        help_upload_tools = '|'.join(self.config.get('auto_tools_found', []))
        if not help_upload_tools:
            help_upload_tools = 'TOOL'

        self.args_help.update({
            'bitfile': (
                f'Tool specific {self.str_ext} files to upload (auto-detected if not specified)'
                ' If you would like see full help for a given tool, use:'
                f' {Colors.yellow}eda upload --help'
                f' {Colors.byellow}--tool={help_upload_tools}{Colors.green}'
            ),
            'list-bitfiles': (
                f'List available {self.str_ext} files.'
                ' If you would like see full help for a given tool, use:'
                f' {Colors.yellow}eda upload --help'
                f' {Colors.byellow}--tool={help_upload_tools}{Colors.green}'
            )
        })

        self.bitfiles = []

        if not getattr(self, '_TOOL', ''):
            for tool, bit_exts in self.SUPPORTED_TOOLS.items():
                for ext in bit_exts:
                    self.BIT_EXT_TO_TOOL[ext] = tool


    def process_tokens(
            self, tokens: list, process_all: bool = True, pwd: str = os.getcwd()
    ) -> list:

        self.unparsed_args = Command.process_tokens(
            self, tokens=tokens, process_all=False, pwd=pwd
        )

        if self.stop_process_tokens_before_do_it():
            return []

        self.bitfiles = self.get_list_bitfiles(display=True)

        # If someone called --list-bitfiles, stop now.
        if self.args['list-bitfiles']:
            if not self.bitfiles:
                self.error('No bitfiles found')
            return []

        sco = self._get_child_handling_class()

        if sco is None or not isinstance(sco, Tool):
            self.error('Could not find a suitable tool to process bitfiles')
            return []

        sco.unparsed_args = Command.process_tokens(
            sco, tokens=tokens, process_all=False, pwd=pwd
        )
        sco.bitfiles = self.bitfiles
        sco.create_work_dir()
        sco.do_it()
        return []

    def get_targets_or_files_from_unparsed_args(self) -> (list, list):
        '''Returns (list of targets, list of files) from unparsed args or --bitfile'''

        targets = []
        files = []
        for f in self.unparsed_args + [self.args['bitfile']]:
            if not f:
                continue
            if os.path.isfile(f):
                files.append(f)
            elif not f.startswith('-'):
                # avoid a arg
                targets.append(f)
        return targets, files


    def get_list_bitfiles(self, display: bool = True) -> list:
        '''Returns a list of bit files (ending with self.SUPPORTED_BIT_EXT)'''

        bitfiles: list[Path] = []

        targets, files = self.get_targets_or_files_from_unparsed_args()
        targets.extend(files)

        debug(f"Looking for bitfiles in {os.path.abspath('.')=}")
        for root, _, files in os.walk("."):
            for f in files:
                if any(f.endswith(x) for x in self.SUPPORTED_BIT_EXT):
                    fullpath = os.path.abspath(Path(root) / f)
                    if os.path.isfile(fullpath) and fullpath not in bitfiles:
                        bitfiles.append(fullpath)

        matched: list[Path] = []
        for cand in bitfiles:
            debug(f"Looking for {cand=} in {targets=}")
            passing = all(re.search(t, str(cand)) for t in targets)
            if passing:
                matched.append(cand)
                mod_time_string = datetime.fromtimestamp(
                    os.path.getmtime(cand)).strftime('%Y-%m-%d %H:%M:%S')
                tool_guess = getattr(self, '_TOOL', '')
                if not tool_guess:
                    ext = os.path.splitext(cand)[1]
                    tool_guess = self.BIT_EXT_TO_TOOL.get(ext, '')
                if tool_guess:
                    tool_guess = f'({tool_guess})'
                if display:
                    info(
                        f"{safe_emoji('⏩ ')}Found matching bitfile {tool_guess}:",
                        f"{Colors.cyan}{mod_time_string}{Colors.normal} :",
                        f"{Colors.byellow}{cand}"
                    )

        if display and not matched:
            if self.args['list-bitfiles']:
                warning(f'{safe_emoji("❕ ")}--list-bitfiles: no {self.str_ext} found that matched',
                        f'{targets}')
            else:
                warning(f'{safe_emoji("❕ ")} Searched for bitfiles with {self.str_ext}: none found',
                        f'that matched {targets}')

        return matched




    def _get_child_handling_class(self) -> object:
        '''Returns a class handle of a child to process this, which should be a Tool class

        if no appropriate child is found, returns self.
        '''

        if isinstance(self, Tool):
            # We're already a tool handling class.
            return self

        tools_found = set()
        for bitfile in self.bitfiles:
            ext = os.path.splitext(bitfile)[1]
            tool_guess = self.BIT_EXT_TO_TOOL.get(ext, '')
            if tool_guess:
                tools_found.add(tool_guess)
            else:
                warning(f'For bitfile {bitfile} no tool found for it')
                return self

        if not tools_found:
            # Probably not an error?
            warning(f'No tools found to process bitfiles: {self.bitfiles}')
            return self

        if len(tools_found) > 1:
            warning(f'More than one tool found ({tools_found}) to to process bitfiles:',
                         f'{self.bitfiles}')
            return self


        tool = tools_found.pop() # only item in set
        # Do we have a handler for this in our config?
        if tool in self.config.get('tools_loaded', []):
            tool_cfg = self.config.get('tools', {}).get(tool, {})
            if tool_cfg:
                cls_str = tool_cfg.get('handlers', {}).get(self.command_name, None)
                if cls_str:
                    cls = import_class_from_string(cls_str)
                    if issubclass(cls, Command):
                        info(f'For found bitfiles, can use tool={tool} and handler {cls}')
                        sco = cls(config=self.config)
                        return sco


        warning(f'No handler found for tool={tool} to process bitfiles: {self.bitfiles}')
        debug(f'config -- tools_loaded: {self.config["tools_loaded"]}')
        debug(f'config -- tools for tool: {self.config["tools"].get(tool, "")}')
        return self
