# 🎨 sphinxcolor

**Colorize your Sphinx build output with beautiful, customizable colors!**

`sphinxcolor` is a Python package that adds vibrant colors to `sphinx-build` output, making warnings, errors, and other messages easier to read and identify.

[![PyPI version](https://badge.fury.io/py/sphinxcolor.svg)](https://badge.fury.io/py/sphinxcolor)
[![Python Versions](https://img.shields.io/pypi/pyversions/sphinxcolor.svg)](https://pypi.org/project/sphinxcolor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://sphinxcolor.readthedocs.io/)

<p align="center">
  <img src="https://raw.githubusercontent.com/cumulus13/sphinxcolor/master/screenshot.png" alt="Screenshot">
</p>


## ✨ Features

- 🎨 **Customizable Colors**: Configure colors via TOML file
- 🔌 **Multiple Usage Modes**: 
  - Use as command-line pipe
  - Import as Sphinx extension
  - Use as standalone tool
- 🚀 **Rich Terminal Output**: Uses the `rich` library for beautiful formatting
- ⚡ **Fast**: Regex-based pattern matching for efficient processing
- 🛠️ **Configurable Patterns**: Customize what gets colored and how

## 📦 Installation

```bash
# Install from PyPI (when published)
pip install sphinxcolor

# Or install from source
git clone https://github.com/cumulus13/sphinxcolor.git
cd sphinxcolor
pip install -e .
```

## 🚀 Usage

### 1. Pipe Mode (Recommended)

The most common usage - pipe `sphinx-build` output through `sphinxcolor`:

**IMPORTANT**: Always use `2>&1` to merge stderr to stdout!

```bash
# Correct - merges stderr to stdout
sphinx-build -b html . _build 2>&1 | sphinxcolor

# Wrong - will have duplicate output
sphinx-build -b html . _build | sphinxcolor

# With make
make html | sphinxcolor

# With specific color on Windows
rm -rf _build && make html | sphinxcolor
```

### 2. As a Sphinx Extension

Add to your `conf.py`:

```python
# conf.py
extensions = [
    'sphinxcolor',
    # ... other extensions
]

# Optional: specify custom config path
sphinxcolor_config_path = 'path/to/custom/sphinxcolor.toml'

# Optional: disable if needed
sphinxcolor_enabled = True
```
### 3. As a Standalone Tool

```bash
# Process a log file
sphinxcolor build.log

# From stdin
cat build.log | sphinxcolor

# With custom config
sphinxcolor --config custom.toml < build.log

# Disable colors
sphinxcolor --no-color < build.log
```

## ⚙️ Configuration

Create a `sphinxcolor.toml` file in your project root, home directory (`~/.sphinxcolor.toml`), or config directory (`~/.config/sphinxcolor.toml`):

```toml
[colors]
# File path color (cyan)
filepath = "#00FFFF"

# WARNING text color (yellow)
warning = "#FFFF00"

# ERROR text color (red)  
error = "#FF0000"

# Docstring/location (purple)
docstring = "#aa55ff"

# Warning message (black on green)
message_fg = "#000000"
message_bg = "#00FF00"

# Tips/suggestions (white on purple)
tips_fg = "#FFFFFF"
tips_bg = "#5500FF"

[patterns]
# Customize regex patterns
filepath_pattern = '^([A-Z]:\\[^:]+|/[^:]+)'
warning_pattern = '\b(WARNING|Error|ERROR)\s*:'
tips_pattern = 'use :no-index: for one of them'
```

### Default Color Scheme

The example you provided will be colored as:

```
C:\PROJECTS\gntplib\gntplib\requests.py              <- Cyan (#00FFFF)
:docstring of gntplib.requests.Response.get_header:1 <- Purple (#aa55ff)
: WARNING:                                            <- Yellow (#FFFF00) bold
duplicate object description...                      <- Black on Green
use :no-index: for one of them                       <- White on Purple (#5500FF) bold
```

## 🎯 Example Output

Before `sphinxcolor`:
```
C:\PROJECTS\gntplib\gntplib\keys.py:docstring of gntplib.keys.Key:1: WARNING: duplicate object description of gntplib.keys.Key, other instance in api/core, use :no-index: for one of them
```

After `sphinxcolor`:
```
[Beautiful colored output with cyan paths, yellow warnings, purple locations, and highlighted messages!]
```

## 🔧 Advanced Usage

### Custom Configuration Location

```bash
# Specify config file
sphinxcolor --config /path/to/custom.toml < input.log
```

### In Python Scripts

```python
from sphinxcolor import SphinxColorizer, Config

# Create colorizer with custom config
config = Config('sphinxcolor.toml')
colorizer = SphinxColorizer(config)

# Process lines
with open('build.log', 'r') as f:
    colorizer.process_stream(f)
```

### Disable Temporarily

```bash
# Use --no-color flag
make html | sphinxcolor --no-color

# Or set environment variable
SPHINXCOLOR_ENABLED=0 make html | sphinxcolor
```

## 📝 Color Format

Colors can be specified in several formats:
- Hex colors: `#RRGGBB` (e.g., `#00FFFF`)
- Named colors: `red`, `blue`, `green`, etc.
- RGB colors: `rgb(255,0,0)`

## Requirements

- Python 3.8+
- rich >= 13.0.0
- tomli >= 2.0.0 (for Python < 3.11)

## Author

[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Made with ❤️ for the Sphinx community