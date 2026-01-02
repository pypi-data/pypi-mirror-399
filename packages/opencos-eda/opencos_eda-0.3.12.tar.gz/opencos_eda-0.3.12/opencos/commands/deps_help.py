'''opencos.commands.deps_help - command handler for: eda deps_help [args]

Note this command is handled differently than others (such as CommandSim),
it is generally run as simply

    > eda deps_help
    > eda deps_help --verbose
    > eda deps_help --help

uses no tools and will print a help text regarding DEPS markup files to stdout.
'''

# pylint: disable=line-too-long

import os
import re

from opencos.eda_base import Command
from opencos import util
from opencos.util import Colors

def get_deps_md_file() -> str:
    '''Tries to get docs/DEPS.md from our pypackage dist'''
    opencos_dir, _ = os.path.split(util.__file__)

    # Try to get it from site-packages dir, which should have docs/ alongside
    # commands/ and tools/
    filename = os.path.join(opencos_dir, 'docs', 'DEPS.md')
    if os.path.isfile(filename):
        return filename

    # If you're running directly from the git checkout dir, you won't be getting
    # this dist, so it's not in opencos/docs, it will simply be in ./docs
    filename = os.path.join(opencos_dir, '..', 'docs', 'DEPS.md')
    if os.path.isfile(filename):
        return filename
    return ''

def get_deps_md_contents() -> str:
    '''Tries to get the docs/DEPS.md file and returns the str contents

    This also performs some limited colorization of markdown and YAML
    (assuming util was not disabled with --no-color)
    '''
    filename = get_deps_md_file()
    if not filename:
        return ''

    def make_byellow(match):
        '''Used by re.sub to wrap the match with bold yellow and return to normal yellow'''
        return f'{Colors.byellow}{match.group(0)}{Colors.normal}{Colors.yellow}'

    lines = []
    with open(filename, encoding='utf-8') as f:
        for line in f.readlines():

            if line.startswith('# '):
                # colors for markdown headings
                line = f'{Colors.bgreen}{line}{Colors.normal}{Colors.yellow}'
            elif line.startswith('## '):
                # colors for markdown headings
                line = f'{Colors.bcyan}{line}{Colors.normal}{Colors.yellow}'

            elif '#' in line:
                # colors for comments
                line = line.replace('#', f'{Colors.normal}{Colors.cyan}#') + Colors.yellow

            # colors for starting a line with:
            #  key: value
            #  - key : value
            # try to make "key:"  or "- key:" as bold:
            line = re.sub(
                r'^( *\-? ?[^ ]+):', make_byellow, line
            )

            lines.append(line)

    return ''.join(lines)


BASIC_DEPS_HELP = f'''
{Colors.yellow}
Note: you can run with one of: {Colors.cyan}--verbose, --help, --debug{Colors.yellow} to show full
schema supported, or {Colors.cyan}--no-color{Colors.yellow} to avoid printing this text with colors.

{Colors.green}--------------------------------------------------------------------{Colors.yellow}

  What is a {Colors.byellow}DEPS.yml{Colors.normal}{Colors.yellow} file and why does `eda` use this?
  - {Colors.byellow}DEPS.yml{Colors.normal}{Colors.yellow} is a fancy filelist.
  - Used to organize a project into "targets", a tool can run on a "target".
  - Allows for more than just source files attached to a "target".
    -- incdirs, defines, and args can be applied to a "target".

{Colors.green}--------------------------------------------------------------------{Colors.yellow}

  Hello World example:

  The following example is a {Colors.byellow}DEPS.yml{Colors.normal}{Colors.yellow} file example for a SystemVerilog simulation of
  hello_world_tb.sv. {Colors.byellow}DEPS.yml{Colors.normal}{Colors.yellow} is, in short, a fancy filelist. We use them in the `eda`
  app to organize projects.

--- {Colors.byellow}DEPS.yml{Colors.normal}{Colors.yellow}: ---

hello-world:           # <-- this is a named target that will be run

  deps:                # <-- 'deps' is a list of SV, Verilog, VHDL files in compile order
    - hello_world_tb.sv

  top: hello_world_tb  # <-- For testbenches, it is good practice to specifiy the topmost
                       #     module using using 'top'. This is not necessary for design
                       #     files.


--- hello_world_tb.sv: ---

module hello_world_tb;

  initial begin
    #10ns;
    $display("%t %m: Hello World!", $realtime);
    $display("%t %m: Test finished", $realtime);
    $finish;
  end

endmodule : hello_world_tb

---


  hello-world:
    The target name in the {Colors.byellow}DEPS.yml{Colors.normal}{Colors.yellow} we named is hello-world. That is a valid target
    that `eda` can use. Such as:

       eda sim --tool=verilator hello-world


{Colors.green}--------------------------------------------------------------------{Colors.yellow}

   Beyond Hello World example:

   The following example is a DEPS.yml file for a more complex module simulation.
   It has two files in ./DEPS.yml and ./lib/DEPS.yml.

--- {Colors.byellow}./DEPS.yml{Colors.normal}{Colors.yellow}: ---

my_fifo:                         # <-- this is a design
  incdirs: . lib                 # <-- 'incdirs' define the paths searched to find `include files
  defines:
    FIFO_DEBUG                   # add a basic define
    FIFO_IMPLEMENTATION=uram     # add a define with a value
  deps:            # <-- 'deps' is a list of SV, Verilog, VHDL files in compile order
    - my_fifo.sv                 # an SV file pulled in directly
    - lib/bin_to_gray            # a target, in a subdirectory that has it's own DEPS

my_fifo_test:                    # <-- this is a TEST
  top: my_fifo_test              # the top will default to whatever target is provided
                                 # by the user, so this could be optional
  deps:
    - my_fifo                    # the target that is defined above
    - my_fifo_tb.sv              # an SV file pulled in directly

my_fifo_stress_test:             # <-- this is another TEST
  top: my_fifo_test              # not optional because top is not "my_fifo_stress_test"
  defines:
    STRESS_TEST                  # configures my_fifo_test to be more stressful
  deps:
    - my_fifo_test               # aside from the define, this is same as "my_fifo_test"

--- {Colors.byellow}lib/DEPS.yml{Colors.normal}{Colors.yellow}: ---

lib_pkg:                         # <-- this is a package required by bin_to_gray below
  deps:
    - assert_pkg.sv              # an SV package pulled in directly, before it's needed below
    - lib_pkg.sv                 # an SV package pulled in directly

bin_to_gray:                     # <-- this is the target that was required by ../my_fifo
  deps:
    - lib_pkg                    # a target package, listed first as SV requires packages
                                 # to be read before the code that uses them
    - bin_to_gray.sv             # an SV module pulled in directly

{Colors.green}--------------------------------------------------------------------{Colors.yellow}
'''


FULL_DEPS_HELP = f'''

{Colors.green}--------------------------------------------------------------------{Colors.yellow}

''' + get_deps_md_contents()



class CommandDepsHelp:
    '''command handler for: eda deps-help'''

    command_name = 'deps-help'

    def __init__(self, config: dict):
        # We don't inherit opencos.eda_base.Command, so we have to set a few
        # member vars for Command.help to work.
        self.args = {}
        self.args_help = {}
        self.config = config
        self.status = 0

    def process_tokens( # pylint: disable=unused-argument
        self, tokens: list, process_all: bool = True,
        pwd: str = os.getcwd()
    ) -> list:
        '''This is effectively our 'run' method, entrypoint from opencos.eda.main'''

        print(BASIC_DEPS_HELP)
        if util.args['verbose'] or util.args['debug']:
            print()
            print(FULL_DEPS_HELP)

        return []

    def help(self, tokens: list) -> None:
        '''Since we don't inherit from opencos.eda_base.Command, need our own help
        method
        '''
        Command.help(self, tokens=tokens, no_targets=True)
        print()
        print(BASIC_DEPS_HELP)
        print()
        print(FULL_DEPS_HELP)
