"""Utility script to synchronise project assets listed in projects.json with files on disk.

This script inspects the static asset folders under app/static/projects, groups
available files by media type, and updates the assets section of each project
entry in data/projects.json. Existing manual entries (those without the
"automated" flag) are preserved. Automatically discovered files are tagged with
"automated": true so they can be safely regenerated.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "data" / "projects.json"
STATIC_ROOT = ROOT_DIR / "app" / "static" / "projects"


@dataclass
class AssetDiscovery:
    """Metadata about a discovered static asset."""

    category: str
    file_path: Path
    title: str
    description: str
    asset_type: str

    @property
    def json_payload(self) -> Dict[str, object]:
        relative = self.file_path.relative_to(STATIC_ROOT).as_posix()
        display_mode = infer_display_mode(self.asset_type)
        return {
            "title": self.title,
            "file": f"/projects/{relative}",
            "description": self.description,
            "type": self.asset_type,
            "automated": True,
            **({"displayMode": display_mode} if display_mode else {}),
        }


def infer_asset_folder(project: Dict[str, object]) -> Optional[str]:
    """Determine the folder name that holds a project's static assets."""
    thumbnail = project.get("thumbnail")
    if isinstance(thumbnail, str) and thumbnail.strip():
        parts = Path(thumbnail.strip().lstrip("/")).parts
        if len(parts) >= 2 and parts[0] == "projects":
            return parts[1]
    project_id = project.get("id")
    if isinstance(project_id, str) and project_id.strip():
        return project_id.strip()
    return None


def title_from_filename(name: str) -> str:
    base = Path(name).stem.replace("_", " ").replace("-", " ").strip()
    return base.title() if base else name


def classify_extension(path: Path) -> Optional[AssetDiscovery]:
    suffix = path.suffix.lower()
    name = path.name.lower()

    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return AssetDiscovery(
            category="images",
            file_path=path,
            title=title_from_filename(path.name),
            description="Static image asset discovered automatically.",
            asset_type="image",
        )
    if suffix == ".svg":
        return AssetDiscovery(
            category="images",
            file_path=path,
            title=title_from_filename(path.name),
            description="Vector asset discovered automatically.",
            asset_type="image",
        )
    if suffix in {".html", ".htm"}:
        inferred_category = "plots" if any(keyword in name for keyword in ("plot", "chart", "viz", "dashboard")) else "html"
        inferred_type = "plot" if inferred_category == "plots" else "html"
        return AssetDiscovery(
            category=inferred_category,
            file_path=path,
            title=title_from_filename(path.name),
            description="HTML artifact discovered automatically.",
            asset_type=inferred_type,
        )
    if suffix in {".json", ".csv"}:
        return AssetDiscovery(
            category="data",
            file_path=path,
            title=title_from_filename(path.name),
            description="Data extract discovered automatically.",
            asset_type="data",
        )
    if suffix == ".ipynb":
        return AssetDiscovery(
            category="notebooks",
            file_path=path,
            title=title_from_filename(path.name),
            description="Notebook discovered automatically.",
            asset_type="notebook",
        )
    return None


def discover_assets(folder: Path) -> List[AssetDiscovery]:
    discoveries: List[AssetDiscovery] = []
    if not folder.exists() or not folder.is_dir():
        return discoveries

    for file in folder.iterdir():
        if file.is_dir():
            continue
        if file.name.lower() == "thumbnail.svg":
            continue
        discovery = classify_extension(file)
        if discovery:
            discoveries.append(discovery)
    return discoveries


def infer_display_mode(asset_type: str) -> Optional[str]:
    """Map asset types to preferred display modes for embedding."""

    normalized = asset_type.lower()
    if normalized in {"notebook", "html", "document"}:
        return "scrollable"
    if normalized in {"plot", "image", "diagram"}:
        return "unscrollable"
    return None


def merge_assets(
    existing: Dict[str, List[Dict[str, object]]],
    discovered: Iterable[AssetDiscovery],
) -> Optional[Dict[str, List[Dict[str, object]]]]:
    categories = set(existing.keys()) | {item.category for item in discovered}
    merged: Dict[str, List[Dict[str, object]]] = {}

    for category in categories:
        manual_items = [item for item in existing.get(category, []) if not item.get("automated")]
        auto_items = [item.json_payload for item in discovered if item.category == category]
        combined = manual_items + auto_items
        if combined:
            merged[category] = combined

    return merged or None


def update_project_assets(project: Dict[str, object], dry_run: bool = False) -> bool:
    folder_name = infer_asset_folder(project)
    if not folder_name:
        return False

    asset_folder = STATIC_ROOT / folder_name
    discoveries = discover_assets(asset_folder)

    if not discoveries and not project.get("assets"):
        return False

    current_assets = project.get("assets") or {}
    if not isinstance(current_assets, dict):
        current_assets = {}

    merged_assets = merge_assets(current_assets, discoveries)
    if merged_assets == current_assets or (merged_assets is None and not current_assets):
        return False

    if dry_run:
        return True

    if merged_assets is None:
        project.pop("assets", None)
    else:
        project["assets"] = merged_assets
    return True


def run_sync(selected_projects: Optional[List[str]], dry_run: bool) -> int:
    if not DATA_FILE.exists():
        print(f"Data file not found: {DATA_FILE}", file=sys.stderr)
        return 1
    if not STATIC_ROOT.exists():
        print(f"Static asset directory not found: {STATIC_ROOT}", file=sys.stderr)
        return 1

    with DATA_FILE.open("r", encoding="utf-8") as handle:
        projects = json.load(handle)

    if not isinstance(projects, list):
        print("projects.json must contain a list of project entries", file=sys.stderr)
        return 1

    project_ids = {proj.get("id"): proj for proj in projects if isinstance(proj, dict)}

    targets = selected_projects or list(project_ids.keys())
    missing = [pid for pid in targets if pid not in project_ids]
    if missing:
        print(f"Skipping unknown project ids: {', '.join(missing)}", file=sys.stderr)

    updated = False
    for project_id in targets:
        project = project_ids.get(project_id)
        if not project:
            continue
        changed = update_project_assets(project, dry_run=dry_run)
        status = "updated" if changed else "unchanged"
        print(f"[{status}] {project_id}")
        updated = updated or changed

    if dry_run or not updated:
        return 0

    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(projects, handle, indent=2)
        handle.write("\n")
    print("projects.json updated with discovered assets.")
    return 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronise project assets with static files.")
    parser.add_argument(
        "--project",
        dest="projects",
        action="append",
        help="Limit the sync to a specific project id. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report changes without modifying projects.json.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    return run_sync(args.projects, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
