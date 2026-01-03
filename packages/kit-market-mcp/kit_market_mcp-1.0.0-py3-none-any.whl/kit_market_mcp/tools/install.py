"""
Kit Install Tool

Install a kit into the user's project.
"""

from typing import Any

from ..storage.local import LocalKitStorage


def install_kit(
    store: LocalKitStorage,
    kit_id: str,
    target_dir: str,
    include_examples: bool = False,
    include_tests: bool = False,
    language: str = "python",
) -> dict[str, Any]:
    """
    Install a kit into the target directory.

    Args:
        store: Kit storage backend
        kit_id: Kit to install
        target_dir: Destination directory
        include_examples: Also copy example files
        include_tests: Also copy test files
        language: Programming language

    Returns:
        Result dictionary with success status and details
    """
    return store.copy_kit(
        kit_id=kit_id,
        target_dir=target_dir,
        language=language,
        include_examples=include_examples,
        include_tests=include_tests,
    )
