#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

from fowler_routing_common import (
    build_card_indexes,
    default_policy_path,
    load_json,
    load_routing_policy,
    rank_cards,
    score_text_match,
)
from query_book_cards import result_payload as card_result_payload


STATUS_BONUS = {
    "routing-ready": 30.0,
    "index-ready": 15.0,
    "raw-source-present": 4.0,
    "planned": 0.0,
}
MAX_LIST_MATCHES = 3
FIELD_WEIGHTS = {
    "title": 1.35,
    "description": 0.8,
    "domains": 1.0,
    "strengths": 1.05,
    "pick_when": 1.15,
    "primary_entrypoints": 0.95,
    "query_examples": 0.9,
    "avoid_when": 1.0,
    "limitations": 0.55,
}
BOOK_SELECTOR_PREFIX = "book:"
EXCERPT_WRAP_WIDTH = 100


def normalize_lookup_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def book_identity(registry_entry: dict, manifest: dict) -> dict[str, str]:
    alias = str(registry_entry.get("alias") or registry_entry["id"]).strip()
    title = str(manifest.get("title") or registry_entry["title"]).strip()
    author = str(registry_entry.get("author") or manifest.get("author") or "").strip()
    book_ref = f"book:{alias} | {title}"
    if author:
        book_ref = f"{book_ref} | {author}"
    return {
        "book_id": registry_entry["id"],
        "alias": alias,
        "title": title,
        "author": author,
        "book_ref": book_ref,
    }


def parse_book_selector(value: str) -> str:
    selector = value.strip()
    if selector.casefold().startswith(BOOK_SELECTOR_PREFIX):
        selector = selector[len(BOOK_SELECTOR_PREFIX):].strip()
    if "|" in selector:
        selector = selector.split("|", 1)[0].strip()
    if not selector:
        raise SystemExit("Book selector is empty.")
    return selector


def parse_query_book_selector(query: str) -> tuple[str | None, str]:
    stripped = query.strip()
    if not stripped.casefold().startswith(BOOK_SELECTOR_PREFIX):
        return None, query

    remainder = stripped[len(BOOK_SELECTOR_PREFIX):].strip()
    if not remainder:
        raise SystemExit("Use book:<alias> | <question> or provide a plain discovery query.")

    if "|" in remainder:
        selector, routed_query = remainder.split("|", 1)
        selector = selector.strip()
        routed_query = routed_query.strip()
        if not selector:
            raise SystemExit("Book selector is empty.")
        return selector, routed_query or selector

    return remainder, remainder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Choose the best indexed programming book for a query, then return routed matches from that book."
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Natural-language query to route across the registered book packs.",
    )
    parser.add_argument(
        "--registry",
        default="skills/book-router/references/library/registry.json",
        help="Path to the book-router registry JSON.",
    )
    parser.add_argument(
        "--list-books",
        action="store_true",
        help="List registered books as canonical book:<alias> references and exit.",
    )
    parser.add_argument(
        "--policy",
        default=default_policy_path(),
        help="Path to the shared routing policy.",
    )
    parser.add_argument(
        "--top-books",
        type=int,
        default=3,
        help="Number of ranked book candidates to show.",
    )
    parser.add_argument(
        "--top-results",
        type=int,
        default=5,
        help="Number of routed results to show from the selected book.",
    )
    parser.add_argument(
        "--book",
        help="Force a specific book by alias, id, or exact title instead of selecting automatically.",
    )
    parser.add_argument(
        "--kind",
        default="all",
        help="Restrict card queries to one card kind. Use 'all' to keep everything.",
    )
    parser.add_argument(
        "--read-context",
        type=int,
        default=0,
        help="Include the top result's read_next range plus N lines before and after.",
    )
    parser.add_argument(
        "--read-before",
        type=int,
        default=0,
        help="Include the top result's read_next range plus N lines before it.",
    )
    parser.add_argument(
        "--read-after",
        type=int,
        default=0,
        help="Include the top result's read_next range plus N lines after it.",
    )
    parser.add_argument(
        "--read-next-lines",
        type=int,
        default=0,
        help="Include only the N lines immediately after the top result's read_next range.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output.",
    )
    return parser.parse_args()


def read_query(args: argparse.Namespace) -> str:
    query = " ".join(args.query).strip()
    if not query and not sys.stdin.isatty():
        query = sys.stdin.read().strip()
    if not query:
        raise SystemExit("Provide a query as arguments or via stdin.")
    return query


def repo_root_from_registry(registry_path: Path) -> Path:
    resolved = registry_path.resolve()
    candidates = [resolved.parent, *resolved.parents]
    for candidate in candidates:
        if (candidate / "skills" / "book-router" / "SKILL.md").exists():
            return candidate
        if candidate.name == "book-router" and (candidate / "SKILL.md").exists():
            return candidate.parent.parent
    raise SystemExit(
        f"Could not infer repository root from registry path {resolved}."
    )


def resolve_repo_path(repo_root: Path, declared_path: str, *, relative_to: Path) -> Path:
    candidate = Path(declared_path)
    if candidate.is_absolute():
        return candidate

    repo_candidate = (repo_root / candidate).resolve()
    if repo_candidate.exists():
        return repo_candidate

    relative_candidate = (relative_to / candidate).resolve()
    if relative_candidate.exists():
        return relative_candidate

    return repo_candidate


def resolve_manifest_artifacts(
    manifest: dict,
    manifest_path: Path,
    repo_root: Path,
) -> dict[str, str]:
    resolved = {}
    for name, declared_path in manifest.get("artifacts", {}).items():
        resolved[name] = str(
            resolve_repo_path(
                repo_root,
                declared_path,
                relative_to=manifest_path.parent,
            )
        )
    return resolved


def attach_read_next(result: dict, artifact_paths: dict[str, str]) -> None:
    book_path = artifact_paths.get("cleaned_markdown")
    anchor = result.get("source_anchor")
    if not book_path or not isinstance(anchor, dict):
        return

    start_line = anchor.get("start_line")
    end_line = anchor.get("end_line")
    if not isinstance(start_line, int) or not isinstance(end_line, int):
        return

    result["read_next"] = {
        "book_path": book_path,
        "start_line": start_line,
        "end_line": end_line,
        "source": "source_anchor",
        "reason": (
            f"Read this book.md section before using {result['title']} "
            "as decision backing."
        ),
    }


def validate_read_options(args: argparse.Namespace) -> None:
    option_names = (
        "read_context",
        "read_before",
        "read_after",
        "read_next_lines",
    )
    for option_name in option_names:
        value = getattr(args, option_name)
        if value < 0:
            cli_name = option_name.replace("_", "-")
            raise SystemExit(f"--{cli_name} must be zero or greater.")

    if args.read_next_lines and (
        args.read_context or args.read_before or args.read_after
    ):
        raise SystemExit(
            "--read-next-lines cannot be combined with --read-context, "
            "--read-before, or --read-after."
        )


def read_excerpt_lines(
    *,
    book_path: Path,
    start_line: int,
    end_line: int,
    anchor_start_line: int,
    anchor_end_line: int,
    mode: str,
    before_lines: int = 0,
    after_lines: int = 0,
    next_lines: int = 0,
) -> dict:
    start_line = max(1, start_line)
    end_line = max(start_line, end_line)
    lines = []

    with book_path.open(encoding="utf-8") as handle:
        for line_number, text in enumerate(handle, start=1):
            if line_number < start_line:
                continue
            if line_number > end_line:
                break
            lines.append(
                {
                    "line": line_number,
                    "text": text.rstrip("\n"),
                    "anchor": anchor_start_line <= line_number <= anchor_end_line,
                }
            )

    actual_start = lines[0]["line"] if lines else start_line
    actual_end = lines[-1]["line"] if lines else start_line - 1
    return {
        "mode": mode,
        "book_path": str(book_path),
        "start_line": actual_start,
        "end_line": actual_end,
        "anchor_start_line": anchor_start_line,
        "anchor_end_line": anchor_end_line,
        "before_lines": before_lines,
        "after_lines": after_lines,
        "next_lines": next_lines,
        "lines": lines,
    }


def attach_top_result_excerpt(
    payload: dict,
    *,
    before_lines: int = 0,
    after_lines: int = 0,
    next_lines: int = 0,
) -> None:
    if not payload.get("results"):
        return

    top_result = payload["results"][0]
    read_next = top_result.get("read_next")
    if not isinstance(read_next, dict):
        return

    book_path = Path(read_next["book_path"])
    anchor_start = int(read_next["start_line"])
    anchor_end = int(read_next["end_line"])

    if next_lines:
        excerpt = read_excerpt_lines(
            book_path=book_path,
            start_line=anchor_end + 1,
            end_line=anchor_end + next_lines,
            anchor_start_line=anchor_start,
            anchor_end_line=anchor_end,
            mode="next-lines",
            next_lines=next_lines,
        )
    else:
        excerpt = read_excerpt_lines(
            book_path=book_path,
            start_line=anchor_start - before_lines,
            end_line=anchor_end + after_lines,
            anchor_start_line=anchor_start,
            anchor_end_line=anchor_end,
            mode="anchor-expanded",
            before_lines=before_lines,
            after_lines=after_lines,
        )

    top_result["book_excerpt"] = excerpt


def weighted_list_score(query: str, values: list[str], *, weight: float) -> tuple[float, list[dict]]:
    matches = []
    for value in values:
        score = score_text_match(query, value)
        if score > 0:
            matches.append({"text": value, "score": round(score, 4)})
    matches.sort(key=lambda item: (-item["score"], item["text"]))
    weighted = 0.0
    used = []
    for index, match in enumerate(matches[:MAX_LIST_MATCHES]):
        contribution = match["score"] * weight * (0.7**index)
        weighted += contribution
        used.append(
            {
                "text": match["text"],
                "raw_score": match["score"],
                "weighted_score": round(contribution, 4),
            }
        )
    return round(weighted, 4), used


def score_book_metadata(query: str, registry_entry: dict, manifest: dict) -> tuple[float, list[dict]]:
    routing_notes = manifest.get("routing_notes", {})
    contributions = []

    def add(field: str, values: list[str]) -> float:
        score, matches = weighted_list_score(query, values, weight=FIELD_WEIGHTS[field])
        if score > 0:
            contributions.append({"field": field, "score": score, "matches": matches})
        return score

    score = 0.0
    status_score = STATUS_BONUS.get(manifest.get("status", registry_entry.get("status", "planned")), 0.0)
    if status_score:
        contributions.append({"field": "status", "score": status_score, "matches": [{"text": manifest.get("status", registry_entry.get("status", "planned")), "weighted_score": status_score}]})
        score += status_score

    score += add(
        "title",
        unique_strings(
            [
                registry_entry["title"],
                manifest["title"],
                registry_entry["id"],
            ]
        ),
    )
    score += add("description", [registry_entry.get("description", ""), manifest.get("description", "")])
    score += add("domains", registry_entry.get("domains", []))
    score += add("strengths", unique_strings(registry_entry.get("strengths", [])) + unique_strings(manifest.get("strengths", [])))
    score += add("pick_when", unique_strings(registry_entry.get("pick_when", [])) + unique_strings(manifest.get("pick_when", [])))
    score += add("primary_entrypoints", unique_strings(routing_notes.get("primary_entrypoints", [])))
    score += add("query_examples", unique_strings(routing_notes.get("query_examples", [])))

    avoid_score, avoid_matches = weighted_list_score(
        query,
        unique_strings(registry_entry.get("avoid_when", [])) + unique_strings(manifest.get("avoid_when", [])),
        weight=FIELD_WEIGHTS["avoid_when"],
    )
    if avoid_score > 0:
        contributions.append({"field": "avoid_when", "score": -avoid_score, "matches": avoid_matches})
        score -= avoid_score

    limitation_score, limitation_matches = weighted_list_score(
        query,
        unique_strings(routing_notes.get("limitations", [])),
        weight=FIELD_WEIGHTS["limitations"],
    )
    if limitation_score > 0:
        contributions.append({"field": "limitations", "score": -limitation_score, "matches": limitation_matches})
        score -= limitation_score

    return round(score, 4), contributions


def unique_strings(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if not isinstance(value, str):
            continue
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def load_book_candidates(registry_path: Path) -> tuple[Path, list[dict]]:
    registry = load_json(registry_path)
    repo_root = repo_root_from_registry(registry_path)
    candidates = []
    for entry in registry["books"]:
        manifest_path = resolve_repo_path(
            repo_root,
            entry["manifest_path"],
            relative_to=registry_path.parent,
        )
        manifest = load_json(manifest_path)
        candidates.append(
            {
                "registry_entry": entry,
                "manifest": manifest,
                "manifest_path": manifest_path,
                "repo_root": repo_root,
            }
        )
    return repo_root, candidates


def resolve_book_selector(selector: str, candidates: list[dict]) -> dict:
    normalized_selector = normalize_lookup_value(parse_book_selector(selector))
    matches = []
    for candidate in candidates:
        identity = book_identity(candidate["registry_entry"], candidate["manifest"])
        lookup_values = [
            identity["alias"],
            identity["book_id"],
            identity["title"],
        ]
        if any(normalize_lookup_value(value) == normalized_selector for value in lookup_values):
            matches.append(candidate)

    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise SystemExit(
            f"Unknown book selector {selector!r}. Use book:<alias> | <question>. "
            "Run with --list-books to verify canonical book references."
        )
    raise SystemExit(
        f"Ambiguous book selector {selector!r}. "
        "Run with --list-books to verify canonical book references."
    )


def list_registered_books(registry_path: Path) -> list[dict]:
    _repo_root, candidates = load_book_candidates(registry_path)
    books = []
    for candidate in candidates:
        identity = book_identity(candidate["registry_entry"], candidate["manifest"])
        books.append(
            {
                **identity,
                "status": candidate["manifest"].get(
                    "status",
                    candidate["registry_entry"].get("status", "planned"),
                ),
                "manifest_path": str(candidate["manifest_path"]),
            }
        )
    return books


def print_book_list(books: list[dict]) -> None:
    print("Available books:")
    for book in books:
        print(
            f"- {book['book_ref']} "
            f"(id={book['book_id']}, status={book['status']})"
        )


def print_excerpt_line(line: dict) -> None:
    marker = ">" if line["anchor"] else " "
    first_prefix = f"   {line['line']:>6}{marker} "
    continuation_prefix = "   " + (" " * 6) + "  "
    text = line["text"]

    if not text:
        print(first_prefix)
        return

    wrapped = textwrap.wrap(
        text,
        width=EXCERPT_WRAP_WIDTH,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not wrapped:
        print(first_prefix)
        return

    print(f"{first_prefix}{wrapped[0]}")
    for continuation in wrapped[1:]:
        print(f"{continuation_prefix}{continuation}")


def rank_index_entries(query: str, index_payload: dict, *, limit: int = 5) -> list[dict]:
    ranked = []
    for chapter in index_payload.get("chapters", []):
        terms = [chapter["title"], chapter.get("route_hint", "")]
        score, matches = weighted_list_score(query, terms, weight=1.0)
        if score <= 0:
            continue
        ranked.append(
            {
                "id": chapter["id"],
                "title": chapter["title"],
                "kind": "chapter",
                "score": score,
                "summary": chapter.get("route_hint", ""),
                "match_hints": matches,
                "source_anchor": {
                    "entry_id": chapter["id"],
                    "chapter": chapter.get("chapter", chapter.get("title")),
                    "start_line": chapter.get("start_line"),
                    "end_line": chapter.get("end_line"),
                },
            }
        )
    for entry in index_payload.get("entries", []):
        terms = entry.get("lookup_terms", []) or [entry["title"]]
        score, matches = weighted_list_score(query, terms, weight=1.0)
        if score <= 0:
            continue
        ranked.append(
            {
                "id": entry["id"],
                "title": entry["title"],
                "kind": entry["kind"],
                "score": score,
                "summary": entry.get("summary", ""),
                "match_hints": matches,
                "source_anchor": {
                    "entry_id": entry["id"],
                    "chapter": entry.get("chapter"),
                    "start_line": entry.get("start_line"),
                    "end_line": entry.get("end_line"),
                },
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    return ranked[: max(limit, 0)]


def normalize_index_result(result: dict, rank: int) -> dict:
    match_hints = [
        {
            "channel": "lookup",
            "term": hint["text"],
            "source_kind": "index",
            "score": round(float(hint["weighted_score"]), 4),
        }
        for hint in result.get("match_hints", [])
    ]
    return {
        "rank": rank,
        "score": round(float(result["score"]), 4),
        "id": result["id"],
        "title": result["title"],
        "card_kind": result["kind"],
        "summary": result.get("summary", ""),
        "match_hints": match_hints,
        "source_anchor": {
            key: value
            for key, value in result.get("source_anchor", {}).items()
            if value is not None
        },
    }


def query_book_candidates(
    query: str,
    manifest: dict,
    manifest_path: Path,
    repo_root: Path,
    policy: dict,
    *,
    top_results: int,
    allowed_kinds: set[str] | None,
) -> tuple[float, list[dict], str, dict[str, str]]:
    artifacts = manifest.get("artifacts", {})
    artifact_paths = resolve_manifest_artifacts(manifest, manifest_path, repo_root)
    if "cards" in artifacts:
        cards_path = Path(artifact_paths["cards"])
        cards_payload = load_json(cards_path)
        cards = cards_payload["cards"]
        cards_by_id, order = build_card_indexes(cards)
        ranked = rank_cards(
            query,
            cards,
            cards_by_id,
            order,
            policy,
            allowed_kinds=allowed_kinds,
        )[: max(top_results, 0)]
        results = [
            card_result_payload(
                rank=index,
                query=query,
                card_id=card_id,
                score=score,
                cards_by_id=cards_by_id,
            )
            for index, (card_id, score) in enumerate(ranked, start=1)
        ]
        for result in results:
            attach_read_next(result, artifact_paths)
        top_score = ranked[0][1] if ranked else 0.0
        return round(float(top_score), 4), results, "cards", artifact_paths
    if "index" in artifacts:
        index_path = Path(artifact_paths["index"])
        ranked = rank_index_entries(query, load_json(index_path), limit=top_results)
        results = [
            normalize_index_result(result, rank=index)
            for index, result in enumerate(ranked, start=1)
        ]
        for result in results:
            attach_read_next(result, artifact_paths)
        top_score = results[0]["score"] if results else 0.0
        return round(float(top_score), 4), results, "index", artifact_paths
    return 0.0, [], "none", artifact_paths


def recommendation_label(
    *,
    rank: int,
    score_share: float,
    score_gap_from_top: float,
    total_score: float,
    low_confidence_threshold: float,
) -> str:
    if rank == 0:
        return "top-suggestion"
    if score_share >= 0.78 or score_gap_from_top <= 80:
        return "also-worth-checking"
    if total_score >= (low_confidence_threshold * 0.5) or score_share >= 0.45:
        return "background-option"
    return "weak-match"


def annotate_book_rankings(book_rankings: list[dict], policy: dict) -> list[dict]:
    if not book_rankings:
        return []

    top_score = max(book["total_score"] for book in book_rankings)
    top_artifact_score = max(book["artifact_score"] for book in book_rankings)
    second_score = book_rankings[1]["total_score"] if len(book_rankings) > 1 else 0.0

    annotated = []
    for rank, book in enumerate(book_rankings):
        score_share = round((book["total_score"] / top_score), 4) if top_score > 0 else 0.0
        artifact_share = (
            round((book["artifact_score"] / top_artifact_score), 4)
            if top_artifact_score > 0
            else 0.0
        )
        score_gap_from_top = round(top_score - book["total_score"], 4)
        next_gap = (
            round(book["total_score"] - book_rankings[rank + 1]["total_score"], 4)
            if rank + 1 < len(book_rankings)
            else None
        )
        annotated_book = dict(book)
        annotated_book.update(
            {
                "rank": rank + 1,
                "score_share_of_top": score_share,
                "artifact_share_of_top": artifact_share,
                "score_gap_from_top": score_gap_from_top,
                "score_gap_to_next": next_gap,
                "recommendation": recommendation_label(
                    rank=rank,
                    score_share=score_share,
                    score_gap_from_top=score_gap_from_top,
                    total_score=book["total_score"],
                    low_confidence_threshold=float(policy["low_confidence_threshold"]),
                ),
            }
        )
        annotated.append(annotated_book)

    close_call = False
    if len(annotated) > 1 and top_score > 0:
        runner_up_share = annotated[1]["score_share_of_top"]
        runner_up_gap = round(top_score - second_score, 4)
        close_call = runner_up_share >= 0.8 or runner_up_gap <= 80

    annotated[0]["is_close_call"] = close_call
    if len(annotated) > 1:
        annotated[1]["is_close_call"] = close_call
    return annotated


def route_query(
    query: str,
    *,
    registry_path: Path,
    policy_path: Path,
    forced_book: str | None = None,
    top_books: int = 3,
    top_results: int = 5,
    kind: str = "all",
) -> dict:
    policy = load_routing_policy(policy_path)
    repo_root, candidates = load_book_candidates(registry_path)
    allowed_kinds = None if kind == "all" else {kind}
    query_selector, routed_query = parse_query_book_selector(query)
    selected_book_id = None
    explicit_selector = None

    if query_selector:
        query_selected = resolve_book_selector(query_selector, candidates)
        selected_book_id = query_selected["registry_entry"]["id"]
        explicit_selector = query_selector

    if forced_book:
        forced_selected = resolve_book_selector(forced_book, candidates)
        forced_book_id = forced_selected["registry_entry"]["id"]
        if selected_book_id and selected_book_id != forced_book_id:
            raise SystemExit(
                f"Conflicting book selectors: query selected {query_selector!r}, "
                f"--book selected {forced_book!r}."
            )
        selected_book_id = forced_book_id
        explicit_selector = forced_book

    selection_mode = "specific-book" if selected_book_id else "soft-ranked"
    book_rankings = []

    for candidate in candidates:
        registry_entry = candidate["registry_entry"]
        manifest = candidate["manifest"]
        if selected_book_id and registry_entry["id"] != selected_book_id:
            continue
        metadata_score, metadata_expl = score_book_metadata(routed_query, registry_entry, manifest)
        artifact_score, routed_results, artifact_kind, artifact_paths = query_book_candidates(
            routed_query,
            manifest,
            candidate["manifest_path"],
            repo_root,
            policy,
            top_results=top_results,
            allowed_kinds=allowed_kinds,
        )
        total_score = round(metadata_score + artifact_score, 4)
        identity = book_identity(registry_entry, manifest)
        book_rankings.append(
            {
                **identity,
                "status": manifest["status"],
                "manifest_path": str(candidate["manifest_path"]),
                "metadata_score": metadata_score,
                "artifact_score": artifact_score,
                "total_score": total_score,
                "metadata_explanation": metadata_expl,
                "artifact_kind": artifact_kind,
                "artifact_paths": artifact_paths,
                "results": routed_results,
            }
        )

    if not book_rankings:
        raise SystemExit(
            "No books available for selection"
            f"{f' with selector {explicit_selector!r}' if explicit_selector else ''}."
        )

    book_rankings.sort(key=lambda item: (-item["total_score"], -item["artifact_score"], item["book_id"]))
    book_rankings = annotate_book_rankings(book_rankings, policy)
    selected = book_rankings[0]
    confidence = "high" if selected["total_score"] >= policy["low_confidence_threshold"] else "low"
    payload = {
        "query": routed_query,
        "selection_mode": selection_mode,
        "top_suggestion": {
            "book_id": selected["book_id"],
            "alias": selected["alias"],
            "title": selected["title"],
            "author": selected["author"],
            "book_ref": selected["book_ref"],
            "status": selected["status"],
            "confidence": confidence,
            "total_score": selected["total_score"],
            "metadata_score": selected["metadata_score"],
            "artifact_score": selected["artifact_score"],
            "artifact_kind": selected["artifact_kind"],
            "score_share_of_top": selected["score_share_of_top"],
            "score_gap_to_next": selected["score_gap_to_next"],
            "is_close_call": selected.get("is_close_call", False),
            "recommendation": selected["recommendation"],
            "artifact_paths": selected.get("artifact_paths", {}),
        },
        "selected_book": {
            "book_id": selected["book_id"],
            "alias": selected["alias"],
            "title": selected["title"],
            "author": selected["author"],
            "book_ref": selected["book_ref"],
            "status": selected["status"],
            "confidence": confidence,
            "total_score": selected["total_score"],
            "metadata_score": selected["metadata_score"],
            "artifact_score": selected["artifact_score"],
            "artifact_kind": selected["artifact_kind"],
            "artifact_paths": selected.get("artifact_paths", {}),
        },
        "results": selected["results"],
        "book_rankings": book_rankings[: max(top_books, 0)],
    }
    if routed_query != query:
        payload["input_query"] = query
    if explicit_selector:
        payload["book_selector"] = parse_book_selector(explicit_selector)
    return payload


def print_human(payload: dict) -> None:
    query = payload["query"]
    selected = payload["top_suggestion"]
    if payload.get("input_query"):
        print(f"Input query: {payload['input_query']}")
    print(f"Query: {query}")
    selection_label = (
        "Selected book"
        if payload.get("selection_mode") == "specific-book"
        else "Top suggestion"
    )
    print(
        f"\n{selection_label}: {selected['book_ref']} ({selected['book_id']}) "
        f"status={selected['status']} confidence={selected['confidence']} "
        f"score={selected['total_score']:.2f}"
    )
    print(f"  selection={payload['selection_mode']}")
    print(
        f"  metadata={selected['metadata_score']:.2f} "
        f"artifact={selected['artifact_score']:.2f} via {selected['artifact_kind']}"
    )
    if selected.get("is_close_call"):
        print("  note: close call, the next book is also worth checking.")

    if payload["results"]:
        print("\nTop matches:")
        for result in payload["results"]:
            print(
                f"\n{result['rank']}. [{result['card_kind']}] {result['title']} "
                f"({result['id']}) score={result['score']:.2f}"
            )
            print(f"   {result['summary']}")
            hints = []
            for hint in result.get("match_hints", [])[:2]:
                if hint.get("channel") == "lookup":
                    hints.append(
                        f"lookup '{hint.get('term', '?')}' ({hint.get('source_kind', 'unknown')})"
                    )
                else:
                    hints.append(f"code shape '{hint.get('shape', '?')}'")
            if hints:
                print(f"   match: {', '.join(hints)}")
            if result.get("heuristic_code"):
                print(f"   code: {result['heuristic_code']}  group: {result.get('group_title', '-')}")
            if result.get("focus_areas"):
                print(f"   focus: {', '.join(result['focus_areas'][:5])}")
            if result.get("guidance"):
                print(f"   guidance: {result['guidance']}")
            if result.get("likely_refactorings"):
                print(f"   likely moves: {', '.join(result['likely_refactorings'])}")
            if result.get("related_smells"):
                print(f"   related smells: {', '.join(result['related_smells'])}")
            if result.get("related_topics"):
                print(f"   related topics: {', '.join(result['related_topics'])}")
            if result.get("heuristics"):
                print(f"   heuristics: {', '.join(result['heuristics'])}")
            if result.get("read_next"):
                read_next = result["read_next"]
                print(
                    "   read next: "
                    f"{read_next['book_path']}:{read_next['start_line']}"
                    f"-{read_next['end_line']}"
                )
                print(f"   reason: {read_next['reason']}")
            if result.get("book_excerpt"):
                excerpt = result["book_excerpt"]
                print(
                    "   book excerpt: "
                    f"{excerpt['book_path']}:{excerpt['start_line']}"
                    f"-{excerpt['end_line']} mode={excerpt['mode']}"
                )
                for line in excerpt["lines"]:
                    print_excerpt_line(line)
    else:
        print("\nNo routed results were found inside the selected book.")

    print("\nBook rankings:")
    for rank, book in enumerate(payload["book_rankings"], start=1):
        print(
            f"{rank}. {book['book_ref']} ({book['book_id']}) "
            f"score={book['total_score']:.2f} "
            f"[metadata={book['metadata_score']:.2f}, artifact={book['artifact_score']:.2f}] "
            f"{book['recommendation']} share={book['score_share_of_top']:.2f}"
        )


def main() -> None:
    args = parse_args()
    validate_read_options(args)
    if args.list_books:
        books = list_registered_books(Path(args.registry))
        if args.json:
            print(json.dumps({"books": books}, ensure_ascii=False, indent=2))
        else:
            print_book_list(books)
        return

    query = read_query(args)
    payload = route_query(
        query,
        registry_path=Path(args.registry),
        policy_path=Path(args.policy),
        forced_book=args.book,
        top_books=args.top_books,
        top_results=args.top_results,
        kind=args.kind,
    )
    if (
        args.read_context
        or args.read_before
        or args.read_after
        or args.read_next_lines
    ):
        attach_top_result_excerpt(
            payload,
            before_lines=max(args.read_context, args.read_before),
            after_lines=max(args.read_context, args.read_after),
            next_lines=args.read_next_lines,
        )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print_human(payload)


if __name__ == "__main__":
    main()
