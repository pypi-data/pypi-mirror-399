"""
Kit Info Tool

Get detailed information about a specific kit.
"""

from typing import Any, Optional

from ..storage.local import LocalKitStorage


def get_kit_info(
    store: LocalKitStorage,
    kit_id: str,
    include_readme: bool = True,
    include_examples: bool = False,
) -> dict[str, Any]:
    """
    Get detailed information about a kit.

    Args:
        store: Kit storage backend
        kit_id: Kit identifier
        include_readme: Include full README content
        include_examples: Include example code

    Returns:
        Dictionary with kit information
    """
    # Get basic info from manifest
    kit = store.get_kit(kit_id)
    if not kit:
        return {}

    # Get full manifest for more details
    full_manifest = store.get_kit_manifest(kit_id) or {}

    info = {
        "id": kit.get("id"),
        "name": kit.get("name"),
        "version": full_manifest.get("version", kit.get("version", "unknown")),
        "group": kit.get("group"),
        "summary": kit.get("summary"),
        "description": full_manifest.get("description", ""),
        "tags": full_manifest.get("tags", []),
        "problems_solved": full_manifest.get("problems_solved", []),
        "when_to_use": full_manifest.get("when_to_use", []),
        "when_not_to_use": full_manifest.get("when_not_to_use", []),
        "benefits": full_manifest.get("benefits", []),
        "dependencies": [],
        "implementations": list(full_manifest.get("implementations", {}).keys()),
    }

    # Get dependencies
    deps = full_manifest.get("dependencies", {})
    if isinstance(deps, dict):
        info["dependencies"] = deps.get("required", [])
    elif isinstance(deps, list):
        info["dependencies"] = deps

    # Include README if requested
    if include_readme:
        readme = store.get_kit_readme(kit_id)
        if readme:
            info["readme"] = readme

    # Include examples if requested
    if include_examples:
        examples = store.get_kit_examples(kit_id)
        if examples:
            info["examples"] = examples

    return info
