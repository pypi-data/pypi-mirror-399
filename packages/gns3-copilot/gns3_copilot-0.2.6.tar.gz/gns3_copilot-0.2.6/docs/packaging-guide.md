# GNS3 Copilot Packaging Guide

This document explains the packaging configuration for GNS3 Copilot when distributing via PyPI.

## Overview

GNS3 Copilot uses modern Python packaging with `pyproject.toml` and `setuptools`. The project is built and distributed as a standard Python package that can be installed via `pip`.

## Package Contents

### Included Files and Directories

#### 1. Top-Level Files
- `LICENSE` - MIT License file
- `README.md` - English documentation
- `README_ZH.md` - Chinese documentation
- `pyproject.toml` - Project configuration

#### 2. Python Source Code (`src/gns3_copilot/`)
All Python modules in the source directory are included:

- **`agent/`** - LangGraph AI Agent framework
  - `gns3_copilot.py` - Main agent implementation

- **`gns3_client/`** - GNS3 server client
  - `custom_gns3fy.py` - Enhanced GNS3 client
  - `gns3_project_create.py` - Project creation
  - `gns3_project_open.py` - Project management
  - `gns3_project_update.py` - Project updates
  - `gns3_projects_list.py` - Project listing
  - `gns3_topology_reader.py` - Topology analysis

- **`tools_v2/`** - Tool integration layer
  - `config_tools_nornir.py` - Configuration tools
  - `display_tools_nornir.py` - Display command tools
  - `linux_tools_nornir.py` - Linux device tools
  - `vpcs_tools_telnetlib3.py` - VPCS tools
  - `gns3_create_node.py` - Node creation
  - `gns3_create_link.py` - Link creation
  - `gns3_start_node.py` - Node management
  - `gns3_get_node_temp.py` - Template retrieval

- **`ui_model/`** - Streamlit UI components
  - `chat.py` - Chat interface
  - `settings.py` - Settings page
  - `help.py` - Help documentation
  - `utils/` - UI helper functions
  - `styles/` - CSS stylesheets

- **`prompts/`** - LLM prompt templates
  - `base_prompt.py` - Base prompt
  - `prompt_loader.py` - Prompt loader
  - `english_level_prompt_*.py` - Proficiency level prompts
  - `voice_prompt_*.py` - Voice interaction prompts

- **`public_model/`** - Common models
  - `openai_tts.py` - Text-to-speech
  - `openai_stt.py` - Speech-to-text
  - `parse_tool_content.py` - Result parser
  - `get_gns3_device_port.py` - Port information

- **`log_config/`** - Logging configuration
  - `logging_config.py` - Logging setup

- **Root Python files**
  - `__init__.py` - Package initialization
  - `app.py` - Streamlit application
  - `main.py` - CLI entry point

#### 3. CSS Stylesheets
- `ui_model/styles/main.css` - Streamlit UI custom styles

#### 4. Command-Line Scripts
- `gns3-copilot` - CLI entry point (maps to `gns3_copilot.main:main`)

### Excluded Files and Directories

The following are **NOT** included in the PyPI package:

- **`tests/`** - All test files and test data
- **`Architecture/`** - Architecture diagrams and documentation
- **`docs/`** - Documentation files
- **`audio/`** - Audio files
- **`log/`** - Log files
- **`*.json`, `*.yaml`, `*.yml`, `*.txt`, `*.jpeg`, `*.gif`** - Non-code data files

## Configuration Files

### `pyproject.toml`

The main configuration file with these key sections:

#### Build System
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"
```

#### Package Discovery
```toml
[tool.setuptools]
package-dir = {"" = "src"}
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"gns3_copilot" = ["ui_model/styles/*.css"]
```

This configuration:
- Sets the source directory to `src/`
- Enables package data inclusion
- Includes all Python packages under `src/`
- **Explicitly includes CSS files** from `ui_model/styles/`

#### Project Metadata
```toml
[project]
name = "gns3-copilot"
dynamic = ["version"]
description = "AI-powered network automation assistant for GNS3"
license = "MIT"
requires-python = ">=3.10"
```

#### Dependencies
The project includes dependencies for:
- AI frameworks (LangChain, LangGraph)
- Network automation (Nornir, Netmiko)
- Model providers (OpenAI, Anthropic, Google, etc.)
- Web UI (Streamlit)
- And various utility libraries

### `MANIFEST.in`

Controls what files are included/excluded during package building:

```
# Include top-level files
include LICENSE
include README.md
include README_ZH.md
include pyproject.toml

# Include all Python files
recursive-include src/gns3_copilot *.py

# Exclude tests
global-exclude tests/*
prune tests/

# Exclude Architecture
global-exclude Architecture/*
prune Architecture/

# Exclude other data files
global-exclude *.json *.yaml *.yml *.txt *.jpeg *.gif
global-exclude notebok_en.md notebok_zh.md
```

## Building the Package

### Prerequisites

```bash
pip install build setuptools wheel
```

### Build Commands

To build source and wheel distributions:

```bash
python -m build
```

This creates:
- `dist/gns3-copilot-x.y.z.tar.gz` - Source distribution (sdist)
- `dist/gns3_copilot-x.y.z-py3-none-any.whl` - Wheel distribution

### Local Installation Test

To test installing the package locally:

```bash
pip install -e .
```

Or install from the built distribution:

```bash
pip install dist/gns3_copilot-x.y.z-py3-none-any.whl
```

## Publishing to PyPI

### Test PyPI

```bash
python -m build
python -m twine upload --repository testpypi dist/*
```

### Production PyPI

```bash
python -m build
python -m twine upload dist/*
```

## Important Notes

### CSS File Inclusion

The CSS file (`ui_model/styles/main.css`) is included via the `package-data` configuration in `pyproject.toml`. This is critical for the Streamlit UI to display correctly.

If you add new non-Python files that need to be packaged, update the `package-data` section:

```toml
[tool.setuptools.package-data]
"gns3_copilot" = [
    "ui_model/styles/*.css",
    "path/to/other/files/*"
]
```

### Version Management

The version is managed by `setuptools_scm` based on git tags. The configuration uses:

```toml
[tool.setuptools_scm]
version_scheme = "post-release"
local_scheme = "no-local-version"
```

Create a git tag to set the version:

```bash
git tag v1.0.0
git push --tags
```

### MANIFEST.in vs package-data

- **MANIFEST.in** - Controls which files are considered for inclusion
- **package-data** - Explicitly specifies which files to include

For the most reliable packaging, use both:
1. MANIFEST.in to exclude unwanted files
2. package-data to explicitly include needed non-Python files

## Troubleshooting

### Files Not Packaged

If files are missing from the package:

1. Check if they're in `MANIFEST.in`
2. Verify they're in `package-data` configuration
3. Ensure the file paths are correct relative to the package root

### CSS Not Loading

If Streamlit styles don't work after installation:

1. Verify the CSS file is in the package: `python -c "import gns3_copilot; import os; print(os.listdir(os.path.dirname(gns3_copilot.__file__)))"`
2. Check the package data configuration
3. Rebuild and reinstall the package

### Version Issues

If version detection fails:

1. Ensure git is installed
2. Check that the repository has proper tags
3. Verify `setuptools_scm` is installed

## References

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
