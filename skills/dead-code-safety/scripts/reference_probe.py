#!/usr/bin/env python3
"""Read-only text reference probe for dead-code candidates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".lorchestre",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    "target",
}

TEXT_EXTS = {
    ".go",
    ".js",
    ".cjs",
    ".mjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".html",
    ".css",
    ".scss",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".sql",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Categorize text references for candidate dead code symbols.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--paths", nargs="*", default=["."], help="Relative paths to scan")
    parser.add_argument("--symbol", action="append", required=True, help="Symbol/name to search; repeatable")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--max-file-bytes", type=int, default=1_000_000)
    parser.add_argument("--max-matches-per-symbol", type=int, default=80)
    return parser.parse_args()


def is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def is_text_candidate(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTS:
        return True
    return path.name in {"Dockerfile", "Makefile", "justfile", "Taskfile"}


def iter_files(root: Path, rel_paths: list[str], max_file_bytes: int):
    for rel in rel_paths:
        start = (root / rel).resolve()
        if not start.exists():
            continue
        if start.is_file():
            candidates = [start]
        else:
            candidates = (p for p in start.rglob("*") if p.is_file())
        for path in candidates:
            try:
                rel_path = path.relative_to(root)
            except ValueError:
                continue
            if is_ignored(rel_path) or not is_text_candidate(path):
                continue
            try:
                if path.stat().st_size > max_file_bytes:
                    continue
            except OSError:
                continue
            yield path, rel_path


def classify_path(rel_path: Path) -> str:
    parts = {p.lower() for p in rel_path.parts}
    name = rel_path.name.lower()
    suffix = rel_path.suffix.lower()
    if "test" in parts or "tests" in parts or "__tests__" in parts or name.endswith(("_test.go", ".test.ts", ".test.tsx", ".test.js", ".spec.ts", ".spec.tsx", ".spec.js")):
        return "test"
    if "docs" in parts or suffix in {".md", ".mdx", ".rst", ".txt"}:
        return "docs"
    if name.endswith((".lock", ".lockb")) or name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "go.sum", "cargo.lock"}:
        return "generated_or_lock"
    if "generated" in parts or ".generated." in name or name.endswith((".pb.go", ".gen.go", ".min.js")):
        return "generated_or_lock"
    if suffix in {".json", ".yaml", ".yml", ".toml", ".xml"} or name in {"makefile", "dockerfile"}:
        return "config"
    return "source"


def compile_pattern(symbol: str) -> re.Pattern[str]:
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", symbol):
        return re.compile(rf"\b{re.escape(symbol)}\b")
    return re.compile(re.escape(symbol))


def scan_symbol(root: Path, files: list[tuple[Path, Path]], symbol: str, max_matches: int):
    pattern = compile_pattern(symbol)
    matches = []
    counts = {"source": 0, "test": 0, "docs": 0, "config": 0, "generated_or_lock": 0}

    for path, rel_path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        category = classify_path(rel_path)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not pattern.search(line):
                continue
            counts[category] = counts.get(category, 0) + 1
            if len(matches) < max_matches:
                matches.append(
                    {
                        "path": str(rel_path),
                        "line": lineno,
                        "category": category,
                        "text": line.strip()[:240],
                    }
                )

    return {"symbol": symbol, "counts": counts, "matches": matches}


def print_markdown(root: Path, results: list[dict]):
    print("# Reference Probe")
    print()
    print(f"- Root: `{root}`")
    print()
    for result in results:
        print(f"## `{result['symbol']}`")
        print()
        counts = result["counts"]
        total = sum(counts.values())
        print(f"- Total matches: {total}")
        for key in ("source", "test", "config", "docs", "generated_or_lock"):
            print(f"- {key}: {counts.get(key, 0)}")
        print()
        if result["matches"]:
            print("| Category | Location | Text |")
            print("| --- | --- | --- |")
            for match in result["matches"]:
                text = match["text"].replace("|", "\\|")
                print(f"| {match['category']} | `{match['path']}:{match['line']}` | `{text}` |")
            print()
        else:
            print("No text matches found.")
            print()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    files = list(iter_files(root, args.paths, args.max_file_bytes))
    results = [scan_symbol(root, files, symbol, args.max_matches_per_symbol) for symbol in args.symbol]
    if args.format == "json":
        print(json.dumps({"root": str(root), "results": results}, indent=2))
    else:
        print_markdown(root, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
