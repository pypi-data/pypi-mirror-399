# Kit Market MCP Server

> MCP Server for AI-powered code kit discovery and integration

## Overview

Kit Market MCP Server allows AI agents (like Claude Code, Cursor, etc.) to:

- **Search** for code kits by keyword or description
- **Browse** available kits by category
- **Get details** about specific kits (README, examples, dependencies)
- **Install** kits directly into user projects

## Installation

### Option 1: Install from source

```bash
cd kits/mcp-server
pip install -e .
```

### Option 2: Install dependencies only

```bash
pip install mcp pyyaml httpx
```

## Configuration

### For Claude Code

Add to your Claude Code MCP settings (`~/.config/claude-code/settings.json` or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "kit-market": {
      "command": "python",
      "args": ["-m", "kit_market_mcp.server"],
      "cwd": "/path/to/your/project/kits/mcp-server/src",
      "env": {
        "KIT_MARKET_PATH": "/path/to/your/project/kits/market",
        "KIT_MARKET_MANIFEST": "/path/to/your/project/kits/manifest.yaml"
      }
    }
  }
}
```

### For Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "kit-market": {
      "command": "python",
      "args": ["-m", "kit_market_mcp.server"],
      "cwd": "/path/to/kits/mcp-server/src",
      "env": {
        "KIT_MARKET_PATH": "/path/to/kits/market",
        "KIT_MARKET_MANIFEST": "/path/to/kits/manifest.yaml"
      }
    }
  }
}
```

## Available Tools

### `kit_search`

Search for kits by keyword.

```
Input:
  - query: "monitoring service" (required)
  - group: "patterns" (optional)
  - limit: 5 (optional)

Output: List of matching kits with relevance scores
```

### `kit_list`

List all available kits.

```
Input:
  - group: "patterns" (optional filter)

Output: All kits grouped by category
```

### `kit_info`

Get detailed information about a kit.

```
Input:
  - kit_id: "patterns-watchdog" (required)
  - include_readme: true (optional)
  - include_examples: false (optional)

Output: Full kit details including README and examples
```

### `kit_install`

Install a kit into your project.

```
Input:
  - kit_id: "patterns-watchdog" (required)
  - target_dir: "src/monitoring/" (required)
  - include_examples: false (optional)
  - include_tests: false (optional)

Output: Installation result with copied files and dependencies
```

## Available Resources

### `kit://market/manifest`

Complete manifest of all available kits (JSON format).

### `kit://market/{kit-id}/readme`

README content for a specific kit (Markdown format).

## Example Conversation

```
User: I need to add retry logic for API calls in my project

Claude: [Calls kit_search with query="retry API"]

Claude: I found these kits that might help:

1. **Retry with Backoff** (utilities-retry)
   Automatic retry mechanism with exponential backoff
   Score: 8.5

Would you like me to show more details about any of these?

User: Yes, show me utilities-retry

Claude: [Calls kit_info with kit_id="utilities-retry"]

Claude: Here's the details about the Retry kit...
   Would you like me to install it?

User: Yes, install it to src/utils/

Claude: [Calls kit_install with kit_id="utilities-retry", target_dir="src/utils/"]

Claude: Done! I've installed the retry kit. Here's how to use it...
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KIT_MARKET_PATH` | Path to kits market directory | `kits/market` |
| `KIT_MARKET_MANIFEST` | Path to manifest file | `kits/manifest.yaml` |

## Development

### Run locally

```bash
cd kits/mcp-server/src
python -m kit_market_mcp.server
```

### Test tools

```bash
# The server communicates via stdio, so for testing you can use MCP Inspector
# or integrate with Claude Code directly
```

## Project Structure

```
kits/mcp-server/
├── README.md
├── pyproject.toml
└── src/
    └── kit_market_mcp/
        ├── __init__.py
        ├── server.py           # Main MCP server
        ├── storage/
        │   ├── __init__.py
        │   └── local.py        # Local filesystem storage
        └── tools/
            ├── __init__.py
            ├── search.py       # kit_search implementation
            ├── info.py         # kit_info implementation
            └── install.py      # kit_install implementation
```

## Future Enhancements

- [ ] Remote storage backend (GitHub, S3)
- [ ] Kit publishing tool
- [ ] Kit versioning and updates
- [ ] Community ratings and reviews
- [ ] Kit dependencies resolution
