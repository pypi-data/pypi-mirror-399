# RTLViz

Generate interactive block diagrams from Verilog source files.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Example Output

![RISC-V CPU Block Diagram](https://gist.githubusercontent.com/naveenvenk17/fbe1048bd00090735808eec366f88eca/raw/riscv_example.png)

## Installation

```bash
pip install rtlviz
```

If the `rtlviz` command is not in your PATH after installation:
```bash
python -m rtlviz generate ./src
```

## Quick Start

### Option 1: Command Line

```bash
rtlviz generate ./src -o diagram.html
```

### Option 2: AI Assistant Integration

Configure your IDE to use RTLViz as an MCP server:
```bash
rtlviz setup
```

Supported IDEs:
- Antigravity
- Claude Desktop
- Cursor
- VS Code Copilot
- Windsurf

After setup, ask your AI assistant:
> "Generate an RTL diagram for the Verilog files in ./src"

## Commands

### Generate Diagram

```bash
rtlviz generate <source_dir> -o <output.html>
rtlviz generate ./src -o diagram.html --title "My CPU"
```

### Configure IDE

```bash
rtlviz setup              # Auto-detect and configure all IDEs
rtlviz setup --cursor     # Configure specific IDE
```

## Features

- Automatic module and connection parsing from Verilog
- Pipeline stage detection (IF, ID, EX, MEM, WB)
- Orthogonal routing with color-coded functional clusters
- LLM-enhanced semantic labeling via MCP
- Interactive HTML output with pan, zoom, and SVG export

## Requirements

- Python 3.10+
- Internet connection (for Viz.js rendering)

## License

MIT License

## Links

- [GitHub](https://github.com/haran2001/rtlviz)
- [PyPI](https://pypi.org/project/rtlviz/)
