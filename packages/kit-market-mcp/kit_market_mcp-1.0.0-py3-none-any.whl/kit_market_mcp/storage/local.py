"""
Local filesystem storage backend for Kit Market.

Reads kits from local directory structure.
"""

import shutil
from pathlib import Path
from typing import Any, Optional

import yaml


class LocalKitStorage:
    """
    Storage backend that reads kits from local filesystem.

    Expected structure:
        kits/
        ├── manifest.yaml          # Global manifest (optional, can be generated)
        └── market/
            └── {kit-id}/
                ├── manifest.yaml  # Kit manifest
                ├── README.md
                ├── implementations/
                ├── examples/
                └── tests/
    """

    def __init__(self, kits_path: str = "kits/market", manifest_path: str = "kits/manifest.yaml"):
        """
        Initialize local storage.

        Args:
            kits_path: Path to kits market directory
            manifest_path: Path to global manifest file
        """
        self.kits_path = Path(kits_path)
        self.manifest_path = Path(manifest_path)
        self._manifest_cache: Optional[dict] = None

    def get_manifest(self) -> dict:
        """
        Get the global manifest with all kits.

        Returns:
            Manifest dictionary with 'kits' list
        """
        if self._manifest_cache:
            return self._manifest_cache

        # Try to load from manifest file
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                self._manifest_cache = yaml.safe_load(f) or {}
                return self._manifest_cache

        # Generate from scanning kit directories
        self._manifest_cache = self._scan_kits()
        return self._manifest_cache

    def _scan_kits(self) -> dict:
        """Scan kit directories and build manifest."""
        kits = []

        if not self.kits_path.exists():
            return {"kits": [], "total_kits": 0}

        for kit_dir in sorted(self.kits_path.iterdir()):
            if not kit_dir.is_dir() or kit_dir.name.startswith(("_", ".")):
                continue

            manifest_file = kit_dir / "manifest.yaml"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file) as f:
                    kit_manifest = yaml.safe_load(f) or {}

                kits.append({
                    "id": kit_manifest.get("id", kit_dir.name),
                    "name": kit_manifest.get("name", kit_dir.name),
                    "group": kit_manifest.get("group", ""),
                    "summary": kit_manifest.get("summary", ""),
                    "version": kit_manifest.get("version", "0.0.0"),
                    "tags": kit_manifest.get("tags", []),
                    "problems_solved": kit_manifest.get("problems_solved", []),
                    "when_to_use": kit_manifest.get("when_to_use", []),
                    "path": kit_dir.name,
                })
            except Exception:
                continue

        return {"kits": kits, "total_kits": len(kits)}

    def list_kits(self, group: Optional[str] = None) -> list[dict]:
        """
        List all kits, optionally filtered by group.

        Args:
            group: Optional group filter

        Returns:
            List of kit dictionaries
        """
        manifest = self.get_manifest()
        kits = manifest.get("kits", [])

        if group:
            kits = [k for k in kits if k.get("group") == group]

        return kits

    def get_kit(self, kit_id: str) -> Optional[dict]:
        """
        Get a specific kit by ID.

        Args:
            kit_id: Kit identifier

        Returns:
            Kit dictionary or None if not found
        """
        for kit in self.list_kits():
            if kit.get("id") == kit_id:
                return kit
        return None

    def get_kit_path(self, kit_id: str) -> Optional[Path]:
        """
        Get the filesystem path to a kit.

        Args:
            kit_id: Kit identifier

        Returns:
            Path to kit directory or None
        """
        kit = self.get_kit(kit_id)
        if kit:
            return self.kits_path / kit.get("path", kit_id)
        return None

    def get_kit_manifest(self, kit_id: str) -> Optional[dict]:
        """
        Get the full manifest for a specific kit.

        Args:
            kit_id: Kit identifier

        Returns:
            Full kit manifest or None
        """
        kit_path = self.get_kit_path(kit_id)
        if not kit_path:
            return None

        manifest_file = kit_path / "manifest.yaml"
        if not manifest_file.exists():
            return None

        with open(manifest_file) as f:
            return yaml.safe_load(f)

    def get_kit_readme(self, kit_id: str) -> Optional[str]:
        """
        Get the README content for a kit.

        Args:
            kit_id: Kit identifier

        Returns:
            README content or None
        """
        kit_path = self.get_kit_path(kit_id)
        if not kit_path:
            return None

        readme_file = kit_path / "README.md"
        if not readme_file.exists():
            return None

        return readme_file.read_text()

    def get_kit_examples(self, kit_id: str, language: str = "python") -> dict[str, str]:
        """
        Get example files for a kit.

        Args:
            kit_id: Kit identifier
            language: Programming language

        Returns:
            Dictionary of example name -> code content
        """
        kit_path = self.get_kit_path(kit_id)
        if not kit_path:
            return {}

        examples_path = kit_path / "examples" / language
        if not examples_path.exists():
            return {}

        examples = {}
        for f in examples_path.glob("*.py"):
            examples[f.stem] = f.read_text()

        return examples

    def copy_kit(
        self,
        kit_id: str,
        target_dir: str,
        language: str = "python",
        include_examples: bool = False,
        include_tests: bool = False,
    ) -> dict:
        """
        Copy a kit to target directory.

        Args:
            kit_id: Kit to copy
            target_dir: Destination directory
            language: Programming language
            include_examples: Copy examples too
            include_tests: Copy tests too

        Returns:
            Result dictionary with success status and details
        """
        kit_path = self.get_kit_path(kit_id)
        if not kit_path:
            return {"success": False, "error": f"Kit not found: {kit_id}"}

        impl_path = kit_path / "implementations" / language
        if not impl_path.exists():
            return {"success": False, "error": f"No {language} implementation found"}

        target_path = Path(target_dir)
        result = {
            "success": True,
            "kit_id": kit_id,
            "target_dir": str(target_path),
            "copied_files": [],
            "dependencies": [],
            "notes": [],
        }

        # Find main module directories
        main_modules = [
            d for d in impl_path.iterdir()
            if d.is_dir() and not d.name.startswith(("_", "."))
        ]

        if not main_modules:
            return {"success": False, "error": "No module directory found in kit"}

        # Copy main modules
        for module_dir in main_modules:
            dest_dir = target_path / module_dir.name

            if dest_dir.exists():
                result["notes"].append(f"Skipped {module_dir.name}/ (already exists)")
                continue

            target_path.mkdir(parents=True, exist_ok=True)
            shutil.copytree(module_dir, dest_dir)
            result["copied_files"].append(f"{module_dir.name}/")

        # Get dependencies from requirements.txt
        req_file = impl_path / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        result["dependencies"].append(line)

        # Copy examples if requested
        if include_examples:
            examples_path = kit_path / "examples" / language
            if examples_path.exists():
                examples_dest = target_path / "examples"
                examples_dest.mkdir(parents=True, exist_ok=True)
                for f in examples_path.glob("*.py"):
                    shutil.copy(f, examples_dest / f.name)
                    result["copied_files"].append(f"examples/{f.name}")

        # Copy tests if requested
        if include_tests:
            tests_path = kit_path / "tests" / language
            if tests_path.exists():
                tests_dest = target_path / "tests"
                tests_dest.mkdir(parents=True, exist_ok=True)
                for f in tests_path.glob("*.py"):
                    shutil.copy(f, tests_dest / f.name)
                    result["copied_files"].append(f"tests/{f.name}")

        return result
