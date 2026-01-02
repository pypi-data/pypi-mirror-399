# RTLViz

Generate interactive block diagrams from Verilog source files.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Installation

### Step 1: Install Package
```bash
pip install rtlviz
```

### Step 2: Setup IDE
Spins up the MCP server config for all popular IDEs.
```bash
rtlviz setup
```

### Step 3: Manual IDE Setup (if Step 2 fails)

If the automatic setup doesn't work, you can manually configure your IDE's MCP settings (e.g., `claude_desktop_config.json`).

**Command:** `rtlviz-server` works if installed in PATH. Otherwise use `python -m rtlviz`.

**JSON Config:**
```json
{
  "mcpServers": {
    "rtlviz": {
      "command": "python",
      "args": ["-m", "rtlviz"]
    }
  }
}
```

## Usage

### AI Agent 

After setup, ask your AI assistant (Role: Software Engineer):

> "Use rtlviz MCP to generate a diagram for the Verilog files in `<path to code>`"

The diagram will automatically open in your browser.

**Recommended Models:**
For best results, use state-of-the-art reasoning models:
- **Claude:** Opus 4.5 , Sonnet 4.5
- **Google:** Gemini 3
- **OpenAI:** GPT-5.2

## Example Output

![RISC-V CPU Block Diagram](https://gist.githubusercontent.com/naveenvenk17/fbe1048bd00090735808eec366f88eca/raw/riscv_example.png)

## Features

- **Automatic Parsing** - Extractions modules and connections from Verilog
- **Pipeline Detection** - Identifies CPU stages (IF, ID, EX, MEM, WB)
- **Beautiful Diagrams** - Orthogonal routing with semantic clustering
- **Interactive** - Pan, zoom, and export to SVG
- **Auto-Open** - Instantly opens generated diagrams in browser

## Requirements

- Python 3.10+
- Internet connection (for Viz.js rendering)

## Authors

- Naveen Venkat (naveenvenkat1711@gmail.com)
- Hari Ayyappane (hari.ayyaps@gamil.com)

## License

MIT License
