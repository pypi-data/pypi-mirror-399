"""
Remote Storage Backend

Fetches kits from Kit Market API server.
"""

import base64
import json
import os
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


class RemoteKitStorage:
    """Storage backend that fetches kits from remote API."""

    def __init__(self, api_url: str, timeout: int = 30):
        """
        Initialize remote storage.

        Args:
            api_url: Base URL of Kit Market API (e.g., "https://kit-market.example.com")
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def _request(self, endpoint: str) -> dict:
        """Make API request and return JSON response."""
        url = f"{self.api_url}{endpoint}"
        req = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 404:
                return None
            raise
        except URLError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")

    def list_kits(self, group: Optional[str] = None) -> list[dict]:
        """List all available kits."""
        endpoint = "/api/kits"
        if group:
            endpoint += f"?group={group}"

        result = self._request(endpoint)
        if not result:
            return []

        return result.get("kits", [])

    def search_kits(
        self,
        query: str,
        group: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search kits by keyword."""
        endpoint = f"/api/kits/search?q={query}&limit={limit}"
        if group:
            endpoint += f"&group={group}"

        result = self._request(endpoint)
        if not result:
            return []

        return result.get("results", [])

    def get_kit(self, kit_id: str) -> Optional[dict]:
        """Get kit metadata by ID."""
        result = self._request(f"/api/kits/{kit_id}?include_readme=false")
        return result

    def get_kit_readme(self, kit_id: str) -> Optional[str]:
        """Get kit README content."""
        result = self._request(f"/api/kits/{kit_id}?include_readme=true")
        if result:
            return result.get("readme")
        return None

    def get_manifest(self) -> dict:
        """Get full manifest."""
        result = self._request("/api/manifest")
        return result or {"kits": []}

    def copy_kit(
        self,
        kit_id: str,
        target_dir: str,
        language: str = "python",
        include_examples: bool = False,
        include_tests: bool = False,
    ) -> dict[str, Any]:
        """
        Download and copy kit files to target directory.

        Args:
            kit_id: Kit ID to install
            target_dir: Destination directory
            language: Programming language
            include_examples: Include example files
            include_tests: Include test files

        Returns:
            Result dictionary with success status and details
        """
        # Fetch kit files from API
        endpoint = f"/api/kits/{kit_id}/files?language={language}"
        if include_examples:
            endpoint += "&include_examples=true"
        if include_tests:
            endpoint += "&include_tests=true"

        result = self._request(endpoint)
        if not result:
            return {
                "success": False,
                "error": f"Kit not found: {kit_id}",
            }

        # Create target directory
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        copied_files = []
        files = result.get("files", [])

        for file_info in files:
            file_path = target_path / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Decode base64 content
            content = base64.b64decode(file_info["content"])
            file_path.write_bytes(content)
            copied_files.append(str(file_info["path"]))

        return {
            "success": True,
            "kit_id": kit_id,
            "target_dir": str(target_dir),
            "copied_files": copied_files,
            "dependencies": result.get("dependencies", []),
            "notes": [
                f"Installed from: {self.api_url}",
                "Remember to install dependencies listed above",
            ],
        }
