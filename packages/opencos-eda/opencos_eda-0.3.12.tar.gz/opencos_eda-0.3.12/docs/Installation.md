# Installation

## Prerequisites

- Linux or Windows+WSL.
- bash
- python3.8 or newer
- At least one simulator or synthesis tool
  - *[Verilator](https://verilator.org/guide/latest/)*
  - *[Xilinx Vivado](https://www.xilinx.com/support/download.html)*
      - [Alternate link amd.com](https://docs.amd.com/r/en-US/ug973-vivado-release-notes-install-license/Download-and-Installation)
  - *[Modelsim ASE](https://www.intel.com/content/www/us/en/software-kit/750666/modelsim-intel-fpgas-standard-edition-software-version-20-1-1.html)*

## Installation


Easiest is to install the package as a tool, which makes `eda` and `oc_cli` available in your environment:

Before starting, make sure `uv` is installed per the [instructions](https://docs.astral.sh/uv/getting-started/installation/):
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### PyPi

Install directly from PyPi:
```
uv tool install opencos-eda
```

If you intend to use cocotb with `eda`, you will need an optional dependency:
```
uv tool install opencos-eda[cocotb]
```

### Github repo

Alternately, you can install the package from the Github repo:

Clone this repo:
```
gh repo clone cognichip/opencos

# OR

git clone https://github.com/cognichip/opencos.git
```

Install the local package:
```
uv tool install /path/to/your/checkout/dir/of/opencos

# Or:
uv tool install /path/to/your/checkout/dir/of/opencos[cocotb]
```

### Verify installation

Check that `eda` is in your $PATH
```
which eda
```


## Developing

You may want to install the dev dependencies into the virtual environment:
(Note that cocotb is an optional dependency)
```
uv sync --locked --extra dev --extra cocotb
```

Run the tools by first activating the environment:
```
source .venv/bin/activate
eda
```

You can confirm which instance is being used:
```
which eda
```

Or let `uv` deal with the virtual environment management, which also guarantees you're running the local development version:
```
uv run eda
```

For developers checking cocotb related tests (via pytests, or running eda targets in examples/cocotb) you will need to make sure `find_libpython` returns a .so file. This is most easily fixed with:
```
uv python install 3.12
```
3.12, or a different version, based on the pinned version if present in root .python-version, or the python version you wish to test. `find_libpython` may have issues if your python installation was performed outside of `uv` (such as, an ubuntu22 install of python3.12 via ppa:deadsnakes/ppa).


## Recommended:

Xilinx Vivado suite

- NOTE: licenses are not required to build designs for certain targets (generally Alveo boards: U200, U50, etc).  Other Xilinx kits contain licenses supporting the device used in the kit (Kintex 7, etc).  For other situations, a license is required to build bitfiles.  Certain IPs (Xilinx 25GMAC for example) may require additional licenses – we are always looking for open source versions of such IP :)
- `https://www.xilinx.com/support/download.html`
- Minicom (or another serial terminal)
- For debugging.  `oc_cli` should be all that is needed, but at some point many folks will need a vanilla serial terminal.


## Installation Known issues

If you encounter issues with `uv sync`, ensure that `uv` is up to date:

```
uv --version

# Update uv if needed
uv self update
```

If you encounter issues with the version of Python, note that `uv` respects the `.python_version` (if present) and `requires-python` in `pyproject.toml`. See [docs](https://docs.astral.sh/uv/concepts/python-versions/).
