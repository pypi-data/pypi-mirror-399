#!/usr/bin/env bash

# How to use?
# 1) run:
#        eda_show_autocomplete
#    for instructions, will likely show you the location of this file,
#    eda_deps_bash_completion.bash, for you to source. Does not require uv.
#
# 2) Given the result from (1), and if you use uv, add the following to your
#    ~/.bashrc:
#        # Make sure 'eda' is a valid executable when not in a venv:
#        if ! type -P "eda" &>/dev/null; then
#            uv tool install --python 3.14 opencos-eda >/dev/null 2>&1
#            echo "uv tool installed opencos-eda"
#        fi
#        if [ -f PATH-FROM-STEP-1 ]; then
#            . PATH-FROM-STEP-1
#        fi
#
# 3) copy this script locally and source it.
#    For example:
#    > source ~/sh/eda_deps_bash_completion.bash
#    You can put this in your .bashrc. Note you will need a venv active or
#    "eda" isn't in your path yet.
#
# 4) Have it sourced when you start your venv. Note this doesn't play as nicely
#    with "uv" due to having a less stable .venv, but you can add this to your
#    VENV_NAME/bin/activate script:
#    (bottom of activate script, assuming python3.XX):
#     script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#     . $script_dir/../lib/python3.XX/site-packages/opencos/eda_deps_bash_completion.bash


# scripts via pyproject.toml:
# what we want to add target completion to:
SCRIPT_NAME="eda"
# how we get the completion targets:
EXTRACTION_SCRIPT_NAME="eda_targets"

EDA_WORDS="sim lint elab synth flist proj multi tools-multi sweep build \
    waves upload open export shell targets lec \
    +define+ +incdirs+ \
    --help --quiet --verbose --debug \
    --tool --seed --top --keep --force --fake --lint --work-dir \
    --stop-before-compile --stop-after-compile --stop-before-elaborate \
    --export --export-run --export-json \
"

_eda_script_completion() {

    # Set up for additional completions
    local cur="${COMP_WORDS[COMP_CWORD]}"

    # If we have a DEPS markup file and the current word starts with a key indicator
    local completions=""
    local keys=""
    if [[ $(type -P "$EXTRACTION_SCRIPT_NAME") ]]; then
        keys=$("$EXTRACTION_SCRIPT_NAME" "$cur")
        if [[ -n "$keys" ]]; then
            completions=($(compgen -W "$keys $EDA_WORDS" -- "$cur"))
        fi
    fi

    if [ -z "${completions}" ]; then
        # If we didn't find anything in a DEPS.[yml|yaml|toml|json], then use:
        # -- a bunch of known eda words or args.
        # 2. a glob the current word to mimic normal bash:
        completions=($(compgen -W "$EDA_WORDS" -G "${cur}*" -- "$cur"))
    fi

    COMPREPLY=("${completions[@]}")
}


if [[ $(type -P "$EXTRACTION_SCRIPT_NAME") ]]; then
    complete -F _eda_script_completion "$SCRIPT_NAME"
fi
