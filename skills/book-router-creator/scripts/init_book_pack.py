#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_REGISTRY = Path("skills/book-router/references/library/registry.json")
DEFAULT_BOOKS_DIR = Path("skills/book-router/references/books")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a new book-router pack manifest and registry entry."
    )
    parser.add_argument("--book-id", required=True, help="Lowercase hyphenated book id.")
    parser.add_argument("--title", required=True, help="Book title.")
    parser.add_argument("--author", required=True, help="Author name.")
    parser.add_argument(
        "--description",
        required=True,
        help="Decision-oriented description of what the book is best for.",
    )
    parser.add_argument(
        "--status",
        choices=["planned", "raw-source-present", "index-ready", "routing-ready"],
        help="Initial status. Defaults to raw-source-present if --raw-markdown is given, otherwise planned.",
    )
    parser.add_argument(
        "--raw-markdown",
        help="Optional repo-relative path to the raw source markdown.",
    )
    parser.add_argument("--domain", action="append", default=[], help="Routing domain cue.")
    parser.add_argument("--strength", action="append", default=[], help="Book strength cue.")
    parser.add_argument("--pick-when", action="append", default=[], help="When the book should win.")
    parser.add_argument("--avoid-when", action="append", default=[], help="When another book should win.")
    parser.add_argument(
        "--entrypoint",
        action="append",
        default=[],
        help="Primary routing entrypoint phrase.",
    )
    parser.add_argument(
        "--example",
        action="append",
        default=[],
        help="Example user query that should route to the book.",
    )
    parser.add_argument(
        "--limitation",
        action="append",
        default=[],
        help="Routing limitation phrase.",
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Path to the book-router registry JSON.",
    )
    parser.add_argument(
        "--books-dir",
        default=str(DEFAULT_BOOKS_DIR),
        help="Directory containing skill-local book packs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing manifest or registry entry with the same id.",
    )
    return parser.parse_args()


def ensure_book_id(book_id: str) -> str:
    normalized = book_id.strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise SystemExit(
            "book id must be lowercase hyphenated, for example 'domain-driven-design'."
        )
    return normalized


def unique_strings(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def infer_repo_root(registry_path: Path) -> Path:
    for candidate in [registry_path.parent, *registry_path.parents]:
        if (candidate / "skills" / "book-router" / "SKILL.md").exists():
            return candidate
    raise SystemExit(
        f"Could not infer repository root from registry path {registry_path}."
    )


def build_manifest(args: argparse.Namespace, book_id: str) -> dict:
    status = args.status or ("raw-source-present" if args.raw_markdown else "planned")
    artifacts = {}
    if args.raw_markdown:
        artifacts["raw_markdown"] = args.raw_markdown

    return {
        "schema_version": 1,
        "id": book_id,
        "title": args.title.strip(),
        "author": args.author.strip(),
        "status": status,
        "description": args.description.strip(),
        "strengths": unique_strings(args.strength),
        "pick_when": unique_strings(args.pick_when),
        "avoid_when": unique_strings(args.avoid_when),
        "artifacts": artifacts,
        "routing_notes": {
            "primary_entrypoints": unique_strings(args.entrypoint),
            "query_examples": unique_strings(args.example),
            "preferred_lookup_order": ["cards", "index", "cleaned_markdown"],
            "limitations": unique_strings(args.limitation),
        },
    }


def build_registry_entry(args: argparse.Namespace, book_id: str, manifest_path: Path, status: str) -> dict:
    return {
        "id": book_id,
        "title": args.title.strip(),
        "status": status,
        "description": args.description.strip(),
        "domains": unique_strings(args.domain),
        "strengths": unique_strings(args.strength),
        "pick_when": unique_strings(args.pick_when),
        "avoid_when": unique_strings(args.avoid_when),
        "manifest_path": str(manifest_path).replace("\\", "/"),
    }


def update_registry(registry_path: Path, entry: dict, *, force: bool) -> None:
    registry = load_json(registry_path)
    books = registry.get("books", [])
    existing_index = next(
        (index for index, book in enumerate(books) if book.get("id") == entry["id"]),
        None,
    )

    if existing_index is not None and not force:
        raise SystemExit(
            f"Registry already contains book id '{entry['id']}'. Use --force to replace it."
        )

    if existing_index is None:
        books.append(entry)
    else:
        books[existing_index] = entry

    books.sort(key=lambda book: book["id"])
    registry["books"] = books
    write_json(registry_path, registry)


def main() -> None:
    args = parse_args()
    book_id = ensure_book_id(args.book_id)

    registry_path = Path(args.registry).resolve()
    books_dir = Path(args.books_dir).resolve()
    repo_root = infer_repo_root(registry_path)
    book_dir = books_dir / book_id
    manifest_path = book_dir / "book.json"

    manifest = build_manifest(args, book_id)
    registry_entry = build_registry_entry(
        args,
        book_id,
        manifest_path.relative_to(repo_root),
        manifest["status"],
    )

    if manifest_path.exists() and not args.force:
        raise SystemExit(
            f"Manifest already exists at {manifest_path}. Use --force to replace it."
        )

    book_dir.mkdir(parents=True, exist_ok=True)
    write_json(manifest_path, manifest)
    update_registry(registry_path, registry_entry, force=args.force)

    print(
        json.dumps(
            {
                "ok": True,
                "book_id": book_id,
                "manifest_path": str(manifest_path),
                "registry_path": str(registry_path),
                "status": manifest["status"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
