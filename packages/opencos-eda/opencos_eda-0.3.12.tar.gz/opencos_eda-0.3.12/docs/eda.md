# EDA Tool

## Install

Using `uv` (recommended):

From PyPI:
```
uv tool install opencos-eda
```

OR, from the repo:
```
uv tool install /path/to/your/checkout/dir/of/opencos
```

This makes the `eda` and `oc_cli` commands available in your environment.

## Basic Recipes

Run a single simulation using the default simulator (of those installed).
`oclib_fifo_test` is target in `./lib/tests/DEPS.yml`
```
eda sim lib/tests/oclib_fifo_test
```

Run the same single simulation, but use `verilator`, dump waves
```
eda sim --waves --tool verilator lib/tests/oclib_fifo_test
```

Run the same single simulation, but use `vivado` XSim, and run in GUI mode
```
eda sim --gui --tool vivado lib/tests/oclib_fifo_test
```

Run a compile + elab without a DEPS.yml file or target involved for dependencies
```
eda elab --tool verilator +incdir+. ./lib/oclib_assert_pkg.sv ./lib/oclib_simple_reset_sync.sv

## Basic CLI usage:
eda <command> [--args] [+incdir+DIR|+define+KEY=VALUE|+plusarg=value] file1.sv file2.sv file3.sv
```

## Example Regression testing

```
eda multi sim '.../*_test' --parallel 16
eda multi elab 'lib/*' --parallel 16
eda multi elab 'sim/*' --parallel 16
eda multi elab 'top/*' --parallel 16
```

If you'd like output to stdout, which is how our github Actions are run, use `--verbose` with `eda multi`
```
eda multi sim --verbose lib/tests/oc*test
```

## Example "sweep"

Sweeping a build across a range of parameters

```
eda sweep build u200 --seed=SEED "SEED=(1,2)" +define+OC_MEMORY_BIST_PORT_COUNT=PORTS "PORTS=[1,4,8,16,32]" +define+TARGET_PLL0_CLK_HZ=MHZ000000 "MHZ=(200,400,50)" --parallel 12
```

## Example for building treating non .sv file(s) as systemverilog

```
eda sim --tool verilator sv@several_modules.txt --top=my_module
```

Note that you can prefix source files with `sv@`, `v@`, `vhdl@` or `cpp@` if the file contents do not match their filename extension, and you would like `eda` to force use that file as, for example, systemverilog.


# Help

```
eda help
```

```
$ eda help
INFO: [EDA] eda: version X.Y.Z
INFO: [EDA] eda_config: --config-yml=eda_config_defaults.yml observed
INFO: [EDA] eda_config: using config: ..../site-packages/opencos/eda_config_defaults.yml
INFO: [EDA] *** OpenCOS EDA ***
INFO: [EDA] Detected slang (/usr/local/bin/slang), auto-setting up tool slang
INFO: [EDA] Detected verilator (/usr/local/bin/verilator), auto-setting up tool verilator
INFO: [EDA] Detected surelog (/usr/local/bin/surelog), auto-setting up tool surelog
INFO: [EDA] Detected gtkwave (/usr/bin/gtkwave), auto-setting up tool gtkwave
INFO: [EDA] Detected vivado (/tools/Xilinx/Vivado/VVVV.v/bin/vivado), auto-setting up tool vivado
INFO: [EDA] Detected slang_yosys (/usr/local/bin/yosys), auto-setting up tool slang_yosys
INFO: [EDA] Detected iverilog (/usr/local/bin/iverilog), auto-setting up tool iverilog

Usage:
    eda [<options>] <command> [options] <files|targets, ...>

Where <command> is one of:

    sim          - Simulates a DEPS target
    elab         - Elaborates a DEPS target (sort of sim based LINT)
    synth        - Synthesizes a DEPS target
    flist        - Create dependency from a DEPS target
    proj         - Create a project from a DEPS target for GUI sim/waves/debug
    multi        - Run multiple DEPS targets, serially or in parallel
    tools-multi  - Same as 'multi' but run on all available tools, or specfied using --tools
    sweep        - Sweep one or more arguments across a range, serially or in parallel
    build        - Build for a board, creating a project and running build flow
    waves        - Opens waveform from prior simulation
    upload       - Uploads a finished design into hardware
    open         - Opens a project
    export       - Export files related to a target, tool independent
    help         - This help (without args), or i.e. "eda help sim" for specific help

And <files|targets, ...> is one or more source file or DEPS markup file target,
    such as .v, .sv, .vhd[l], .cpp files, or a target key in a DEPS.[yml|yaml|toml|json].
    Note that you can prefix source files with `sv@`, `v@`, `vhdl@` or `cpp@` to
    force use that file as systemverilog, verilog, vhdl, or C++, respectively.


opencos common options:
  --version
  --color, --no-color   Use shell colors for info/warning/error messaging (default: True)
  --quiet, --no-quiet   Do not display info messaging
  --verbose, --no-verbose
                        Display additional messaging level 2 or higher
  --fancy, --no-fancy
  --debug, --no-debug   Display additional debug messaging level 1 or higher
  --debug-level DEBUG_LEVEL
                        Set debug level messaging (default: 0)
  --logfile LOGFILE     Write eda messaging to logfile (default disabled)
  --force-logfile FORCE_LOGFILE
                        Set to force overwrite the logfile
  --no-respawn          Legacy mode (default respawn disabled) for respawning eda.py using $OC_ROOT/bin

opencos eda config options:
  --config-yml CONFIG_YML
                        YAML filename to use for configuration (default eda_config_defaults.yml)

eda options:
  -q, --quit   For interactive mode (eda called with no options, command, or targets)
  --exit       same as --quit
  -h, --help
  --tool TOOL  Tool to use for this command, such as: modelsim_ase, verilator, modelsim_ase=/path/to/bin/vsim, verilator=/path/to/bin/verilator
  --eda-safe   disable all DEPS file deps shell commands, overrides values from --config-yml
```
