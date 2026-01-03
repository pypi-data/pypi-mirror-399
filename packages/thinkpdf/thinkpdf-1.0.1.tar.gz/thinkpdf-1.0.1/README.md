
# thinkpdf


Convert PDFs to clean Markdown for LLMs. Includes MCP Server for AI coding assistants.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PyPI](https://img.shields.io/pypi/v/thinkpdf.svg)](https://pypi.org/project/thinkpdf/)

## Features

| Feature | Description |
|---------|-------------|
| **Smart Detection** | Auto-chooses best engine for each PDF |
| **High Table Accuracy** | Uses IBM Docling's TableFormer |
| **Fast Mode** | pdfmd for simple documents |
| **Smart Cache** | Never reprocess the same PDF |
| **MCP Server** | For AI coding assistants |

## Installation

```bash
pip install thinkpdf
```

For maximum quality (requires GPU):
```bash
pip install thinkpdf[docling]
```

## Usage

### MCP Server

Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "thinkpdf": {
      "command": "python",
      "args": ["-m", "thinkpdf.mcp_server"]
    }
  }
}
```

Then just ask:
> "Read the PDF at D:\docs\manual.pdf and explain it"

### Python API

```python
from thinkpdf import convert

# Simple conversion
markdown = convert("document.pdf")
print(markdown)

# With output file
convert("document.pdf", "output.md")
```

### CLI

```bash
thinkpdf document.pdf -o output.md
```

## How It Works

1. Analyzes PDF complexity (tables, scans, simple text)
2. Chooses best engine (Docling for complex, pdfmd for simple)
3. Checks cache (instant if already converted)
4. Converts to structured Markdown
5. Caches result for next time


## MCP Tools

When using as MCP server:

| Tool | Description |
|------|-------------|
| `read_pdf` | Convert and return content directly |
| `convert_pdf` | Convert and save to file |
| `get_document_info` | Get PDF metadata |


## Requirements

- Python 3.10+
- PyMuPDF (included)
- Docling (optional, for best quality)

## License

**AGPLv3** - Open source license. Commercial use requires sharing source code.

