"""
Kit Market MCP Server

MCP server implementation using JSON-RPC 2.0 over stdio.
Compatible with Claude Code, Claude Desktop, and other MCP clients.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from .storage.local import LocalKitStorage
from .storage.remote import RemoteKitStorage
from .tools.search import search_kits
from .tools.info import get_kit_info
from .tools.install import install_kit

# Configure logging to stderr (stdout is used for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("kit-market-mcp")

# Server info
SERVER_NAME = "kit-market"
SERVER_VERSION = "1.0.0"

# Default API URL (Render.com hosted)
DEFAULT_API_URL = "https://kit-market-api.onrender.com"

# Initialize storage (supports both local and remote)
storage = None


def get_storage():
    """Get or initialize storage (local or remote based on env)."""
    global storage
    if storage is None:
        import os

        # Check for local mode first
        kits_path = os.environ.get("KIT_MARKET_PATH")
        if kits_path:
            # Use local filesystem
            manifest_path = os.environ.get("KIT_MARKET_MANIFEST", "kits/manifest.yaml")
            storage = LocalKitStorage(kits_path, manifest_path)
            logger.info(f"Initialized local storage: kits_path={kits_path}")
        else:
            # Use remote API (default to Render.com hosted)
            api_url = os.environ.get("KIT_MARKET_API_URL", DEFAULT_API_URL)
            storage = RemoteKitStorage(api_url)
            logger.info(f"Initialized remote storage: api_url={api_url}")
    return storage


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

TOOLS = [
    {
        "name": "kit_search",
        "description": "Search for kits by keyword or description. Use this when user needs a feature that might exist in the kit market.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'retry API', 'monitoring service', 'cache')"
                },
                "group": {
                    "type": "string",
                    "description": "Filter by group: patterns, utilities, integrations, data, testing",
                    "enum": ["patterns", "utilities", "integrations", "data", "testing"]
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "kit_list",
        "description": "List all available kits in the market, optionally filtered by group.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "group": {
                    "type": "string",
                    "description": "Filter by group: patterns, utilities, integrations, data, testing",
                    "enum": ["patterns", "utilities", "integrations", "data", "testing"]
                }
            }
        }
    },
    {
        "name": "kit_info",
        "description": "Get detailed information about a specific kit including README, examples, and integration guide.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kit_id": {
                    "type": "string",
                    "description": "Kit ID (e.g., 'patterns-watchdog', 'utilities-retry')"
                },
                "include_readme": {
                    "type": "boolean",
                    "description": "Include full README content",
                    "default": True
                },
                "include_examples": {
                    "type": "boolean",
                    "description": "Include example code",
                    "default": False
                }
            },
            "required": ["kit_id"]
        }
    },
    {
        "name": "kit_install",
        "description": "Install a kit into the target directory. This copies the kit code into the user's project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kit_id": {
                    "type": "string",
                    "description": "Kit ID to install"
                },
                "target_dir": {
                    "type": "string",
                    "description": "Target directory path (e.g., 'src/monitoring/')"
                },
                "include_examples": {
                    "type": "boolean",
                    "description": "Also copy example files",
                    "default": False
                },
                "include_tests": {
                    "type": "boolean",
                    "description": "Also copy test files",
                    "default": False
                }
            },
            "required": ["kit_id", "target_dir"]
        }
    },
]


# ============================================================================
# TOOL HANDLERS
# ============================================================================

def handle_kit_search(arguments: dict) -> str:
    """Handle kit_search tool call."""
    store = get_storage()
    results = search_kits(
        store=store,
        query=arguments["query"],
        group=arguments.get("group"),
        limit=arguments.get("limit", 5)
    )

    if not results:
        return "No kits found matching your query."

    lines = [f"Found {len(results)} kit(s):\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"## {i}. {r.name} (`{r.kit_id}`)")
        lines.append(f"**Group:** {r.group}")
        lines.append(f"**Summary:** {r.summary}")
        if r.score > 0:
            lines.append(f"**Relevance Score:** {r.score:.1f}")
        lines.append("")

    lines.append("\nUse `kit_info` to get more details about a specific kit.")
    return "\n".join(lines)


def handle_kit_list(arguments: dict) -> str:
    """Handle kit_list tool call."""
    store = get_storage()
    kits = store.list_kits(group=arguments.get("group"))

    if not kits:
        return "No kits available."

    lines = [f"# Kit Market ({len(kits)} kits)\n"]

    # Group by category
    by_group = {}
    for kit in kits:
        group = kit.get("group", "other")
        if group not in by_group:
            by_group[group] = []
        by_group[group].append(kit)

    for group, group_kits in sorted(by_group.items()):
        lines.append(f"## {group.title()} ({len(group_kits)})")
        for kit in group_kits:
            lines.append(f"- **{kit['name']}** (`{kit['id']}`): {kit.get('summary', 'N/A')}")
        lines.append("")

    return "\n".join(lines)


def handle_kit_info(arguments: dict) -> str:
    """Handle kit_info tool call."""
    store = get_storage()
    info = get_kit_info(
        store=store,
        kit_id=arguments["kit_id"],
        include_readme=arguments.get("include_readme", True),
        include_examples=arguments.get("include_examples", False)
    )

    if not info:
        return f"Kit not found: {arguments['kit_id']}"

    lines = [
        f"# {info['name']} (`{info['id']}`)",
        "",
        f"**Version:** {info.get('version', 'N/A')}",
        f"**Group:** {info.get('group', 'N/A')}",
        "",
        f"## Summary",
        info.get("summary", "N/A"),
        "",
    ]

    if info.get("problems_solved"):
        lines.append("## Problems Solved")
        for p in info["problems_solved"]:
            lines.append(f"- {p}")
        lines.append("")

    if info.get("when_to_use"):
        lines.append("## When to Use")
        for w in info["when_to_use"]:
            lines.append(f"- {w}")
        lines.append("")

    if info.get("dependencies"):
        lines.append("## Dependencies")
        for d in info["dependencies"]:
            lines.append(f"- `{d}`")
        lines.append("")

    if info.get("readme"):
        lines.append("---")
        lines.append("## Full Documentation")
        lines.append(info["readme"])

    return "\n".join(lines)


def handle_kit_install(arguments: dict) -> str:
    """Handle kit_install tool call."""
    store = get_storage()
    result = install_kit(
        store=store,
        kit_id=arguments["kit_id"],
        target_dir=arguments["target_dir"],
        include_examples=arguments.get("include_examples", False),
        include_tests=arguments.get("include_tests", False)
    )

    if not result.get("success"):
        return f"Installation failed: {result.get('error', 'Unknown error')}"

    lines = [
        "# Kit Installation Complete",
        "",
        f"**Kit:** {result['kit_id']}",
        f"**Target:** {result['target_dir']}",
        "",
        "## Copied Files",
    ]

    for f in result.get("copied_files", []):
        lines.append(f"- {f}")

    if result.get("dependencies"):
        lines.append("")
        lines.append("## Dependencies to Install")
        lines.append("```bash")
        lines.append(f"pip install {' '.join(result['dependencies'])}")
        lines.append("```")

    if result.get("notes"):
        lines.append("")
        lines.append("## Notes")
        for n in result["notes"]:
            lines.append(f"- {n}")

    return "\n".join(lines)


# ============================================================================
# JSON-RPC HANDLERS
# ============================================================================

def handle_initialize(params: dict) -> dict:
    """Handle initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {},
        },
        "serverInfo": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
        }
    }


def handle_list_tools(params: dict) -> dict:
    """Handle tools/list request."""
    return {"tools": TOOLS}


def handle_call_tool(params: dict) -> dict:
    """Handle tools/call request."""
    name = params.get("name")
    arguments = params.get("arguments", {})

    try:
        if name == "kit_search":
            result = handle_kit_search(arguments)
        elif name == "kit_list":
            result = handle_kit_list(arguments)
        elif name == "kit_info":
            result = handle_kit_info(arguments)
        elif name == "kit_install":
            result = handle_kit_install(arguments)
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True
            }

        return {
            "content": [{"type": "text", "text": result}]
        }

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def handle_list_resources(params: dict) -> dict:
    """Handle resources/list request."""
    store = get_storage()
    resources = [
        {
            "uri": "kit://market/manifest",
            "name": "Kit Market Manifest",
            "description": "Complete list of all available kits with metadata",
            "mimeType": "application/json"
        }
    ]

    for kit in store.list_kits():
        resources.append({
            "uri": f"kit://market/{kit['id']}/readme",
            "name": f"{kit['name']} - README",
            "description": kit.get("summary", ""),
            "mimeType": "text/markdown"
        })

    return {"resources": resources}


def handle_read_resource(params: dict) -> dict:
    """Handle resources/read request."""
    store = get_storage()
    uri = params.get("uri", "")

    if uri == "kit://market/manifest":
        manifest = store.get_manifest()
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(manifest, indent=2)
            }]
        }

    if uri.startswith("kit://market/") and uri.endswith("/readme"):
        kit_id = uri.replace("kit://market/", "").replace("/readme", "")
        readme = store.get_kit_readme(kit_id)
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "text/markdown",
                "text": readme or f"README not found for kit: {kit_id}"
            }]
        }

    return {
        "contents": [{
            "uri": uri,
            "mimeType": "text/plain",
            "text": f"Unknown resource: {uri}"
        }]
    }


# ============================================================================
# MAIN SERVER LOOP
# ============================================================================

def process_request(request: dict) -> dict:
    """Process a JSON-RPC request and return response."""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    logger.info(f"Processing request: {method}")

    handlers = {
        "initialize": handle_initialize,
        "tools/list": handle_list_tools,
        "tools/call": handle_call_tool,
        "resources/list": handle_list_resources,
        "resources/read": handle_read_resource,
        "notifications/initialized": lambda p: None,  # No response needed
        "ping": lambda p: {},
    }

    handler = handlers.get(method)

    if handler is None:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

    try:
        result = handler(params)
        if result is None:  # Notification, no response
            return None
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error handling {method}: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }


def run_server():
    """Run the MCP server (stdio mode)."""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = process_request(request)

            if response is not None:
                print(json.dumps(response), flush=True)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response), flush=True)


def main():
    """Entry point."""
    run_server()


if __name__ == "__main__":
    main()
