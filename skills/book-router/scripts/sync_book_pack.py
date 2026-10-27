#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy rebuilt book artifacts into a book-router skill pack."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the skill-local book manifest JSON.",
    )
    parser.add_argument(
        "--cleaned-source",
        required=True,
        help="Path to the rebuilt cleaned markdown source.",
    )
    parser.add_argument(
        "--index-source",
        help="Path to the rebuilt index JSON source.",
    )
    parser.add_argument(
        "--cards-source",
        help="Path to the rebuilt cards JSON source.",
    )
    return parser.parse_args()


def copy_into_pack(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    repo_root = Path.cwd()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest["artifacts"]

    copy_into_pack(Path(args.cleaned_source), repo_root / artifacts["cleaned_markdown"])
    if "index" in artifacts:
        if not args.index_source:
            raise SystemExit("--index-source is required for manifests with an index artifact.")
        copy_into_pack(Path(args.index_source), repo_root / artifacts["index"])
    if "cards" in artifacts:
        if not args.cards_source:
            raise SystemExit("--cards-source is required for manifests with a cards artifact.")
        copy_into_pack(Path(args.cards_source), repo_root / artifacts["cards"])


if __name__ == "__main__":
    main()
