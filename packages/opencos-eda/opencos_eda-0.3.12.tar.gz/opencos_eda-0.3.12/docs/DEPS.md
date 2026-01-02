# DEPS.yml schema:

(Note this information, DEPS.md, is also available via: eda deps-help --verbose)

```
DEFAULTS: # <table> defaults applied to ALL targets in this file, local targets ** override ** the defaults.

METADATA: # <table> unstructured data, any UPPERCASE first level key is not considered a target.

target-spec:

  args: # <array or | separated str>
    - --waves
    - --sim_plusargs="+info=500"

  defines: # <table>
    SOME_DEFINE: value
    SOME_DEFINE_NO_VALUE:   # we just leave this blank, or use nil (yaml's None)

  plusargs: # <table>
    variable0: value
    variable1:              # blank for no value, or use nil (yaml's None)

  parameters: # <table>
    SomeParameter: value
    SOME_OTHER_PARAMETER: value

  incdirs: # <array>
    - some/relative/path

  top: # <string>

  deps: # <array or | space separated string>
    - some_relative_target       # <string> aka, a target
    - some_file.sv               # <string> aka, a file
    - sv@some_file.txt           # <string> aka, ext@file where we'd like a file not ending in .sv to be
                                 # treated as a .sv file for tools.
                                 # Supported for sv@, v@, vhdl@, cpp@, sdc@, f@, py@, makefile@
    - commands:                  # <table> with key 'commands' for a <array>:  support for built-in commands
                                 # Note this cannot be confused for other targets or files.
      - shell: # <string>
        var-subst-args: # <bool> default false. If true, substitute vars in commands, such as {fpga}
                        # substituted from eda arg --fpga=SomeFpga, such that {fpga} becomes SomeFpga
        var-subst-os-env:  #<bool> default false. If true, substitute vars in commands using os.environ vars,
                           # such as $FPGA could get substituted by env value for it.
        tee: # <string> optional filename, otherwise shell commands write to {target-spec}__shell_0.log
        run-from-work-dir: #<bool> default true. If false, runs from the directory of this DEPS file.
        filepath-subst-target-dir: #<bool> default true. If false, disables shell file path
	                           # substituion on this target's directory (this DEPS file dir).
        dirpath-subst-target-dir: #<bool> default false. If true, enables shell directory path
	                          # substituion on this target's directory (this DEPS file dir).
        run-after-tool: # <bool> default false. Set to true to run after any EDA tools, or
	                # any command handlers have completed.
      - shell: echo "Hello World!"
      - work-dir-add-sources: # <array or | space separated string>, this is how to add generated files
                              # to compile order list.
      - peakrdl:              # <string>     ## peakrdl command to generate CSRs

  reqs: # <array or | space separated string>
    - some_file.mem           # <string> aka, a non-source file required for this target.
                              # This file is checked for existence prior to invoking the tool involved, for example,
                              # in a simulation this would be done prior to a compile step.

  multi:
    ignore-this-target:  # <array of tables> eda commands to be ignored in `eda multi <command>` for this target only
                         # this is checked in the matching multi targets list, and is not inherited through dependencies.
      - commands: synth  # space separated strings
        tools: vivado    # space separated strings

      - commands: sim # omit tools, ignores 'sim' commands for all tools, for this target only, when this target
                      # is in the target list called by `eda multi`.

      - tools: vivado # omit commands, ignores all commands if tool is vivado, for this target only, when this target
                      # is in the target list called by `eda multi`.

    args: # <array> additional args added to all multi commands of this target.
          # Note that all args are POSIX with dashes, --sim-plusargs=value, etc.

  <eda-command>: # key is one of sim, flist, build, synth, etc.
                 # can be used instead of 'tags' to support different args or deps.
    args: # <array or | space separated string>
    defines: ## <table>
    plusargs: ## <table>
    parameters: ## <table>
    incdirs: ## <array>

  tags: # <table> this is the currently support tags features in a target.
    <tag-name>: # <string> key for table, can be anything, name is not used.
      with-tools: <array or | space separated string>
                  # If using one of these tools, apply these values.
                  # entries can be in the form: vivado, or vivado:2024.1
      with-commands: <array or | space separated string>
                  # apply if this was the `eda` command, such as: sim
      with-args: # <table> (optional) arg key/value pairs to match for this tag.
                 # this would be an alternative to running eda with --tags=value
                 # The existence of an argument with correct value would enable a tag.
                 # And example would be:
                 #   with-args:
                 #     waves: true
      args: <array or | space separated string> # args to be applied if this target is used, with a matching
                                          # tool in 'with-tools'.
      deps: <array or | space separated string, applied with tag>
      defines: <table, applied with tag>
      plusargs: <table, applied with tag>
      parameters: <table, applied with tag>
      incdirs: <array, applied with tag>
      replace-config-tools: <table>  # spec matching eda_config_defaults.yml::tools.<tool> (replace merge strategy)
      additive-config-tools: <table> # spec matching eda_config_defaults.yml::tools.<tool> (additive merge strategy)

```

## Examples

### Target with tag-mode:

```
target-foo-with-tags:
   deps: some_file1.sv some_file2.sv
   tags:

     # This can be invoked with eda --tool=vivado --gui
     xilinx_mode:
       with-args:
         gui: true
       with-tools: vivado
       deps: <some_deps_for_this_fpga>
       defines:
         XILINX_GUI_MODE: 1

     defaults:
       deps: some_dummy_dep_not_fpga

```


### Simple Target, with deps as an explicit list

This is the basic, common format for a target. target - deps - (array of files or other relative targets). The file order is compile order, top to bottom.

```
some-target:
  deps:
    - ../foo/some_prev_target
    - some_other_target
    - some_file.sv
```

### Simple Target, with deps as a string with \n separators

This is more terse variant ` deps: |` followed by a string of targets and source files.

```
some-target2:
  deps: |
    ../bar/some_prev_target2
    some_file2.sv
    some_other_target2
```

### Simple Target, non-table (strings)

The most terse variant for a target is a array or \n separated string, not a table, with no `deps` key, then it is assumed that all entries are other targets or sources.

```
some-target3: |
  ../bar/some_prev_target3
  some_file3.sv
  some_other_target3
```

You could also explicitly make a list without a `deps` key:
```
## target entry is an explicit list
some-target4:
  - ../bar/some_prev_target4
  - some_file4.sv
  - some_other_target4
```

You can also have space separated in a string:
```
some-target5: ../bar/some_prev_target5  some_file5.sv
```

### Defines with relative path

Defines with file path information relative to a DEPS.yml file are supported with special words `%PWD%` as a replacement for ./ in defines only. This is necessary because we do not do path substituion on defines.

Example:

```
my_define_target:
  deps:
    - my_dut.sv
    - my_testbench.sv
  defines:
    SOME_FILE: >
      "%PWD%/my_pcap.pcap"
```
