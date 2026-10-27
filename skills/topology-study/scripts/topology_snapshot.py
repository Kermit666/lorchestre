#!/usr/bin/env python3
"""Read-only repository topology snapshot.

Collects cheap file, symbol, import, and test-peer facts for topology study.
It does not execute project code and does not decide architecture.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".next",
    ".cache",
    "coverage",
    "__pycache__",
}

SOURCE_EXTS = {
    ".go",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".py",
    ".rs",
    ".java",
    ".kt",
    ".kts",
    ".cs",
    ".rb",
    ".php",
}

TEST_PATTERNS = (
    ".test.",
    ".spec.",
    "_test.",
    "test_",
    "_spec.",
)

IMPORT_PATTERNS = {
    ".go": re.compile(r'^\s*import\s+(?:\(|"|\w)', re.MULTILINE),
    ".py": re.compile(r"^\s*(?:from\s+\S+\s+import|import\s+\S+)", re.MULTILINE),
    ".js": re.compile(r"^\s*(?:import\s|export\s.+from\s|const\s+\S+\s*=\s*require\()", re.MULTILINE),
    ".jsx": re.compile(r"^\s*(?:import\s|export\s.+from\s|const\s+\S+\s*=\s*require\()", re.MULTILINE),
    ".ts": re.compile(r"^\s*(?:import\s|export\s.+from\s|const\s+\S+\s*=\s*require\()", re.MULTILINE),
    ".tsx": re.compile(r"^\s*(?:import\s|export\s.+from\s|const\s+\S+\s*=\s*require\()", re.MULTILINE),
    ".mjs": re.compile(r"^\s*(?:import\s|export\s.+from\s)", re.MULTILINE),
    ".cjs": re.compile(r"^\s*const\s+\S+\s*=\s*require\(", re.MULTILINE),
    ".rs": re.compile(r"^\s*use\s+[\w:]+", re.MULTILINE),
}

SYMBOL_PATTERNS = {
    ".go": re.compile(r"^\s*(?:func|type)\s+(?:\([^)]+\)\s*)?([A-Za-z_]\w*)", re.MULTILINE),
    ".py": re.compile(r"^\s*(?:def|class)\s+([A-Za-z_]\w*)", re.MULTILINE),
    ".js": re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)", re.MULTILINE),
    ".jsx": re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)", re.MULTILINE),
    ".ts": re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)", re.MULTILINE),
    ".tsx": re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)", re.MULTILINE),
    ".rs": re.compile(r"^\s*(?:pub\s+)?(?:fn|struct|enum|trait|impl)\s+([A-Za-z_]\w*)", re.MULTILINE),
    ".java": re.compile(r"\b(?:class|interface|enum)\s+([A-Za-z_]\w*)", re.MULTILINE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--paths", nargs="*", default=["."], help="Paths under root to inspect")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--max-file-bytes", type=int, default=500_000)
    parser.add_argument("--top", type=int, default=20, help="Number of largest files to show")
    return parser.parse_args()


def iter_files(root: Path, paths: Iterable[str]) -> Iterable[Path]:
    for item in paths:
        start = (root / item).resolve()
        if not start.exists():
            continue
        if start.is_file():
            yield start
            continue
        for dirpath, dirnames, filenames in os.walk(start):
            dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix.lower() in SOURCE_EXTS:
                    yield path.resolve()


def is_test_path(path: Path) -> bool:
    lower = path.name.lower()
    parts = {part.lower() for part in path.parts}
    return any(pattern in lower for pattern in TEST_PATTERNS) or bool(parts & {"test", "tests", "__tests__"})


def read_text(path: Path, max_file_bytes: int) -> str:
    if path.stat().st_size > max_file_bytes:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def peer_candidates(rel: str) -> list[str]:
    path = Path(rel)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    candidates = [
        parent / f"{stem}.test{suffix}",
        parent / f"{stem}.spec{suffix}",
        parent / f"{stem}_test{suffix}",
        parent / f"test_{stem}{suffix}",
        Path("test") / parent / f"{stem}.test{suffix}",
        Path("tests") / parent / f"{stem}.test{suffix}",
    ]
    return [candidate.as_posix() for candidate in candidates]


def collect(root: Path, paths: list[str], max_file_bytes: int) -> dict:
    files = []
    all_rel_paths = set()
    for path in sorted(set(iter_files(root, paths))):
        rel = path.relative_to(root).as_posix()
        all_rel_paths.add(rel)
        text = read_text(path, max_file_bytes)
        ext = path.suffix.lower()
        import_count = len(IMPORT_PATTERNS.get(ext, re.compile("$^")).findall(text)) if text else 0
        symbols = SYMBOL_PATTERNS.get(ext, re.compile("$^")).findall(text)[:30] if text else []
        lines = text.count("\n") + (1 if text else 0)
        files.append(
            {
                "path": rel,
                "extension": ext,
                "folder": str(Path(rel).parent),
                "bytes": path.stat().st_size,
                "lines": lines,
                "is_test": is_test_path(path),
                "import_count": import_count,
                "symbols": symbols,
            }
        )

    for item in files:
        if item["is_test"]:
            item["test_peer"] = "not_applicable"
            continue
        peers = [candidate for candidate in peer_candidates(item["path"]) if candidate in all_rel_paths]
        item["test_peer"] = peers[0] if peers else "missing"

    folder_counts = Counter(item["folder"] for item in files)
    extension_counts = Counter(item["extension"] for item in files)
    duplicate_basenames = defaultdict(list)
    for item in files:
        duplicate_basenames[Path(item["path"]).stem].append(item["path"])
    duplicates = {name: paths for name, paths in duplicate_basenames.items() if len(paths) > 1}

    return {
        "root": root.as_posix(),
        "paths": paths,
        "file_count": len(files),
        "folder_counts": dict(folder_counts.most_common()),
        "extension_counts": dict(extension_counts.most_common()),
        "largest_files": sorted(files, key=lambda item: item["lines"], reverse=True),
        "missing_test_peers": [item for item in files if item.get("test_peer") == "missing"],
        "duplicate_basenames": duplicates,
        "files": files,
    }


def print_markdown(snapshot: dict, top: int) -> None:
    print("# Topology Snapshot")
    print()
    print(f"- Root: `{snapshot['root']}`")
    print(f"- Paths: {', '.join(f'`{path}`' for path in snapshot['paths'])}")
    print(f"- Source files: {snapshot['file_count']}")
    print()
    print("## Largest Files")
    print()
    for item in snapshot["largest_files"][:top]:
        print(f"- `{item['path']}`: {item['lines']} lines, {item['import_count']} imports, test peer: {item['test_peer']}")
    print()
    print("## Missing Test Peers")
    print()
    for item in snapshot["missing_test_peers"][:top]:
        print(f"- `{item['path']}`")
    if not snapshot["missing_test_peers"]:
        print("- None detected")
    print()
    print("## Duplicate Basenames")
    print()
    duplicates = list(snapshot["duplicate_basenames"].items())[:top]
    for name, paths in duplicates:
        joined = ", ".join(f"`{path}`" for path in paths)
        print(f"- `{name}`: {joined}")
    if not duplicates:
        print("- None detected")
    print()
    print("## Symbol Hints")
    print()
    for item in snapshot["largest_files"][:top]:
        if item["symbols"]:
            joined = ", ".join(item["symbols"][:10])
            print(f"- `{item['path']}`: {joined}")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    snapshot = collect(root, args.paths, args.max_file_bytes)
    if args.format == "json":
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    else:
        print_markdown(snapshot, args.top)


if __name__ == "__main__":
    main()
