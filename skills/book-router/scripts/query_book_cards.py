#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fowler_routing_common import (
    build_card_indexes,
    default_policy_path,
    load_json,
    load_routing_policy,
    rank_cards,
    score_shape_match,
    score_text_match,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query semantic book cards from the command line."
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Natural-language query to route against a book card file.",
    )
    parser.add_argument(
        "--cards",
        default="generated/fowler_cards.json",
        help="Path to the generated card file.",
    )
    parser.add_argument(
        "--policy",
        default=default_policy_path(),
        help="Path to the shared routing policy.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of ranked results to show.",
    )
    parser.add_argument(
        "--kind",
        default="all",
        help="Restrict results to one card kind. Use 'all' to keep everything.",
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


def strongest_lookup_match(query: str, card: dict) -> dict | None:
    best = None
    for detail in card["lookup_term_details"]:
        if not detail["enabled_for_ranking"]:
            continue
        score = score_text_match(query, detail["term"]) * float(detail["weight"])
        if score <= 0:
            continue
        candidate = {
            "channel": "lookup",
            "term": detail["term"],
            "source_kind": detail["source_kind"],
            "score": round(score, 4),
        }
        if best is None or candidate["score"] > best["score"]:
            best = candidate
    return best


def strongest_shape_match(query: str, card: dict) -> dict | None:
    best = None
    for shape in card.get("code_shapes", []):
        score = score_shape_match(query, shape)
        if score <= 0:
            continue
        candidate = {
            "channel": "code_shape",
            "shape": shape,
            "score": round(score, 4),
        }
        if best is None or candidate["score"] > best["score"]:
            best = candidate
    return best


def match_hints(query: str, card: dict) -> list[dict]:
    hints = []
    lookup = strongest_lookup_match(query, card)
    shape = strongest_shape_match(query, card)
    if lookup is not None:
        hints.append(lookup)
    if shape is not None:
        hints.append(shape)
    hints.sort(key=lambda item: (-item["score"], item["channel"]))
    return hints


def title_list(ids: list[str], cards_by_id: dict[str, dict], limit: int = 4) -> list[str]:
    return [cards_by_id[card_id]["title"] for card_id in ids[:limit] if card_id in cards_by_id]


def result_payload(
    *,
    rank: int,
    query: str,
    card_id: str,
    score: float,
    cards_by_id: dict[str, dict],
) -> dict:
    card = cards_by_id[card_id]
    result = {
        "rank": rank,
        "score": round(score, 4),
        "id": card["id"],
        "title": card["title"],
        "card_kind": card["card_kind"],
        "summary": card["summary"],
        "match_hints": match_hints(query, card),
    }
    for field in (
        "heuristic_code",
        "group_title",
        "pattern_family",
        "concept_family",
        "use_when",
        "guidance",
        "focus_areas",
        "signals",
    ):
        if field in card and card[field]:
            result[field] = card[field]
    source_anchor = card.get("source_anchor")
    if isinstance(source_anchor, dict):
        result["source_anchor"] = {
            key: source_anchor[key]
            for key in ("entry_id", "chapter", "start_line", "end_line", "input_path")
            if key in source_anchor
        }
    if "likely_refactorings" in card:
        result["likely_refactorings"] = title_list(card["likely_refactorings"], cards_by_id)
    if "related_smells" in card:
        result["related_smells"] = title_list(card["related_smells"], cards_by_id)
    if "related_topics" in card:
        result["related_topics"] = title_list(card["related_topics"], cards_by_id)
    if "related_patterns" in card:
        result["related_patterns"] = title_list(card["related_patterns"], cards_by_id)
    if "related_cards" in card:
        result["related_cards"] = title_list(card["related_cards"], cards_by_id)
    if "key_pattern_ids" in card:
        result["key_patterns"] = title_list(card["key_pattern_ids"], cards_by_id)
    if "key_concept_ids" in card:
        result["key_concepts"] = title_list(card["key_concept_ids"], cards_by_id)
    if "heuristic_ids" in card:
        result["heuristics"] = title_list(card["heuristic_ids"], cards_by_id)
    return result


def print_human_results(query: str, results: list[dict]) -> None:
    print(f"Query: {query}")
    if not results:
        print("\nNo matches found.")
        return

    for result in results:
        print(
            f"\n{result['rank']}. [{result['card_kind']}] {result['title']} "
            f"({result['id']}) score={result['score']:.2f}"
        )
        if result.get("heuristic_code"):
            print(f"   code: {result['heuristic_code']}  group: {result.get('group_title', '-')}")
        if result.get("pattern_family"):
            print(f"   family: {result['pattern_family']}")
        if result.get("concept_family"):
            print(f"   family: {result['concept_family']}")
        print(f"   {result['summary']}")
        hints = []
        for hint in result["match_hints"][:2]:
            if hint["channel"] == "lookup":
                hints.append(f"lookup '{hint['term']}' ({hint['source_kind']})")
            else:
                hints.append(f"code shape '{hint['shape']}'")
        if hints:
            print(f"   match: {', '.join(hints)}")
        if result.get("focus_areas"):
            print(f"   focus: {', '.join(result['focus_areas'][:5])}")
        if result.get("guidance"):
            print(f"   guidance: {result['guidance']}")
        if result.get("signals"):
            print(f"   signals: {', '.join(result['signals'][:4])}")
        if result.get("use_when"):
            print(f"   use when: {result['use_when']}")
        if result.get("likely_refactorings"):
            print(f"   likely moves: {', '.join(result['likely_refactorings'])}")
        if result.get("related_smells"):
            print(f"   related smells: {', '.join(result['related_smells'])}")
        if result.get("related_topics"):
            print(f"   related topics: {', '.join(result['related_topics'])}")
        if result.get("related_patterns"):
            print(f"   related patterns: {', '.join(result['related_patterns'])}")
        if result.get("related_cards"):
            print(f"   related: {', '.join(result['related_cards'])}")
        if result.get("key_patterns"):
            print(f"   key patterns: {', '.join(result['key_patterns'])}")
        if result.get("key_concepts"):
            print(f"   key concepts: {', '.join(result['key_concepts'])}")
        if result.get("heuristics"):
            print(f"   heuristics: {', '.join(result['heuristics'])}")
        if result.get("source_anchor"):
            anchor = result["source_anchor"]
            start = anchor.get("start_line")
            end = anchor.get("end_line")
            if start is not None and end is not None:
                print(f"   source anchor: lines {start}-{end}")


def main() -> None:
    args = parse_args()
    query = read_query(args)
    policy = load_routing_policy(Path(args.policy))
    cards_payload = load_json(Path(args.cards))
    cards = cards_payload["cards"]
    cards_by_id, order = build_card_indexes(cards)
    allowed_kinds = None if args.kind == "all" else {args.kind}
    ranked = rank_cards(
        query,
        cards,
        cards_by_id,
        order,
        policy,
        allowed_kinds=allowed_kinds,
    )[: max(args.top, 0)]
    results = [
        result_payload(
            rank=index,
            query=query,
            card_id=card_id,
            score=score,
            cards_by_id=cards_by_id,
        )
        for index, (card_id, score) in enumerate(ranked, start=1)
    ]
    if args.json:
        print(json.dumps({"query": query, "results": results}, ensure_ascii=False, indent=2))
        return
    print_human_results(query, results)


if __name__ == "__main__":
    main()
