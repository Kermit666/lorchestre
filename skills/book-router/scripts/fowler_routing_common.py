#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


FIXED_CODE_SHAPES = [
    "boolean_flag_argument",
    "repeated_type_switch",
    "deep_message_chain",
    "duplicated_block",
    "too_many_parameters",
    "parameter_clump",
    "long_function",
    "large_class_many_fields",
    "data_holder_class",
    "shared_mutable_state",
    "primitive_type_code",
    "conditional_by_type",
    "temporary_field",
    "shotgun_change",
    "divergent_change",
    "dead_abstraction",
]
LOOKUP_SOURCE_KINDS = ("title", "alias", "manual", "generated")
SOURCE_PRIORITY = {
    "manual": 0,
    "title": 1,
    "alias": 2,
    "generated": 3,
}
OVERLAP_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "for",
    "in",
    "on",
    "to",
    "with",
    "from",
    "by",
    "into",
    "across",
    "through",
    "over",
    "under",
    "between",
    "among",
    "around",
    "before",
    "after",
    "during",
    "rather",
    "than",
    "instead",
    "not",
    "without",
    "vs",
    "versus",
}


def default_policy_path() -> str:
    return "data/fowler_routing_policy.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_lookup_term(text: str) -> str:
    simplified = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode(
        "ascii"
    )
    simplified = simplified.lower()
    simplified = re.sub(r"[^a-z0-9]+", " ", simplified)
    return re.sub(r"\s+", " ", simplified).strip()


def unique_preserve(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _normalize_phrase_variants(raw_variants: dict[str, list[str]]) -> list[tuple[list[str], list[str]]]:
    normalized = []
    for source_text, replacements in raw_variants.items():
        source_tokens = normalize_lookup_term(source_text).split()
        if not source_tokens:
            continue
        for replacement in replacements:
            replacement_tokens = normalize_lookup_term(replacement).split()
            if replacement_tokens:
                normalized.append((source_tokens, replacement_tokens))
    normalized.sort(key=lambda item: (-len(item[0]), item[0]))
    return normalized


def load_routing_policy(path: Path) -> dict:
    policy = load_json(path)
    required_keys = {
        "schema_version",
        "lookup_source_weights",
        "relation_boost_weights",
        "generated_phrase_variants",
        "deny_patterns",
        "low_confidence_threshold",
    }
    missing = sorted(required_keys - set(policy))
    if missing:
        raise ValueError(f"Routing policy is missing keys: {missing}")
    if set(policy["lookup_source_weights"]) != set(LOOKUP_SOURCE_KINDS):
        raise ValueError("lookup_source_weights must define title, alias, manual, and generated.")
    policy["_compiled_deny_patterns"] = [
        re.compile(pattern) for pattern in policy["deny_patterns"]
    ]
    policy["_compiled_phrase_variants"] = _normalize_phrase_variants(
        policy["generated_phrase_variants"]
    )
    return policy


def generated_variant_terms(term: str, policy: dict) -> list[str]:
    tokens = normalize_lookup_term(term).split()
    if not tokens:
        return []

    variants = set()
    for source_tokens, replacement_tokens in policy["_compiled_phrase_variants"]:
        window = len(source_tokens)
        if window > len(tokens):
            continue
        for index in range(len(tokens) - window + 1):
            if tokens[index : index + window] != source_tokens:
                continue
            variant_tokens = (
                tokens[:index] + replacement_tokens + tokens[index + window :]
            )
            variant = " ".join(variant_tokens).strip()
            if variant and variant != " ".join(tokens):
                variants.add(variant)
    return sorted(variants)


def _detail_sort_key(detail: dict) -> tuple[int, float, int, str]:
    return (
        0 if detail["enabled_for_ranking"] else 1,
        -float(detail["weight"]),
        SOURCE_PRIORITY[detail["source_kind"]],
        detail["term"],
    )


def _pick_better_lookup_detail(current: dict, candidate: dict) -> dict:
    current_key = _detail_sort_key(current)
    candidate_key = _detail_sort_key(candidate)
    return candidate if candidate_key < current_key else current


def term_matches_deny_patterns(term: str, policy: dict) -> bool:
    return any(pattern.search(term) for pattern in policy["_compiled_deny_patterns"])


def _lookup_detail(term: str, source_kind: str, policy: dict) -> dict | None:
    normalized = normalize_lookup_term(term)
    if not normalized:
        return None
    if source_kind not in LOOKUP_SOURCE_KINDS:
        raise ValueError(f"Unknown lookup term source_kind '{source_kind}'.")
    return {
        "term": normalized,
        "source_kind": source_kind,
        "enabled_for_ranking": not term_matches_deny_patterns(normalized, policy),
        "weight": float(policy["lookup_source_weights"][source_kind]),
    }


def build_lookup_term_details(
    *,
    title: str,
    aliases: list[str],
    manual_terms: list[str],
    policy: dict,
) -> list[dict]:
    details_by_term: dict[str, dict] = {}

    def add_term(term: str, source_kind: str) -> None:
        detail = _lookup_detail(term, source_kind, policy)
        if detail is None:
            return
        current = details_by_term.get(detail["term"])
        if current is None:
            details_by_term[detail["term"]] = detail
        else:
            details_by_term[detail["term"]] = _pick_better_lookup_detail(current, detail)

    add_term(title, "title")
    for variant in generated_variant_terms(title, policy):
        add_term(variant, "generated")

    for alias in aliases:
        add_term(alias, "alias")
        for variant in generated_variant_terms(alias, policy):
            add_term(variant, "generated")

    for term in manual_terms:
        add_term(term, "manual")

    return sorted(details_by_term.values(), key=_detail_sort_key)


def merge_lookup_term_details(
    *,
    existing_details: list[dict],
    extra_aliases: list[str],
    extra_manual_terms: list[str],
    policy: dict,
) -> list[dict]:
    details_by_term: dict[str, dict] = {}

    def add_existing(detail: dict) -> None:
        normalized = normalize_lookup_term(detail["term"])
        if not normalized:
            return
        source_kind = detail["source_kind"]
        existing = {
            "term": normalized,
            "source_kind": source_kind,
            "enabled_for_ranking": not term_matches_deny_patterns(normalized, policy),
            "weight": float(policy["lookup_source_weights"][source_kind]),
        }
        current = details_by_term.get(normalized)
        if current is None:
            details_by_term[normalized] = existing
        else:
            details_by_term[normalized] = _pick_better_lookup_detail(current, existing)

    def add_term(term: str, source_kind: str) -> None:
        detail = _lookup_detail(term, source_kind, policy)
        if detail is None:
            return
        current = details_by_term.get(detail["term"])
        if current is None:
            details_by_term[detail["term"]] = detail
        else:
            details_by_term[detail["term"]] = _pick_better_lookup_detail(current, detail)

    for detail in existing_details:
        add_existing(detail)

    for alias in extra_aliases:
        add_term(alias, "alias")
        for variant in generated_variant_terms(alias, policy):
            add_term(variant, "generated")

    for term in extra_manual_terms:
        add_term(term, "manual")

    return sorted(details_by_term.values(), key=_detail_sort_key)


def rankable_lookup_terms(details: list[dict]) -> list[str]:
    return [detail["term"] for detail in details if detail["enabled_for_ranking"]]


def tokenize(text: str) -> list[str]:
    normalized = normalize_lookup_term(text)
    return normalized.split() if normalized else []


def _content_tokens(text: str) -> list[str]:
    return [token for token in tokenize(text) if token not in OVERLAP_STOPWORDS]


def _term_is_negated_in_query(query_text: str, candidate: str) -> bool:
    query = normalize_lookup_term(query_text)
    term = normalize_lookup_term(candidate)
    if not query or not term:
        return False
    escaped = re.escape(term)
    patterns = (
        rf"\bnot(?:\s+\w+){{0,2}}\s+{escaped}\b",
        rf"\bwithout(?:\s+\w+){{0,2}}\s+{escaped}\b",
        rf"\binstead of(?:\s+\w+){{0,2}}\s+{escaped}\b",
        rf"\brather than(?:\s+\w+){{0,2}}\s+{escaped}\b",
    )
    return any(re.search(pattern, query) for pattern in patterns)


def score_text_match(query_text: str, candidate: str) -> float:
    query = normalize_lookup_term(query_text)
    term = normalize_lookup_term(candidate)
    if not query or not term:
        return 0.0
    if _term_is_negated_in_query(query, term):
        return 0.0
    query_tokens = tokenize(query)
    term_tokens = tokenize(term)
    if query == term:
        return 160 + (len(term_tokens) * 12)
    if term in query:
        return 120 + (len(term_tokens) * 10)
    query_overlap_tokens = _content_tokens(query) or query_tokens
    term_overlap_tokens = _content_tokens(term) or term_tokens
    overlap = len(set(query_overlap_tokens) & set(term_overlap_tokens))
    if overlap == 0:
        return 0.0
    coverage = overlap / len(set(term_overlap_tokens))
    if len(term_overlap_tokens) == 1:
        return 18.0 if coverage == 1 else 0.0
    if overlap < 2:
        return 0.0
    return round((coverage * 42) + (overlap * 8), 2)


def score_shape_match(query_text: str, shape: str) -> float:
    return score_text_match(query_text, shape.replace("_", " "))


def build_card_indexes(cards: list[dict]) -> tuple[dict[str, dict], dict[str, int]]:
    cards_by_id = {card["id"]: card for card in cards}
    order = {card["id"]: index for index, card in enumerate(cards)}
    return cards_by_id, order


def rank_cards(
    query: str,
    cards: list[dict],
    cards_by_id: dict[str, dict],
    order: dict[str, int],
    policy: dict,
    *,
    allowed_kinds: set[str] | None = None,
) -> list[tuple[str, float]]:
    direct_scores: dict[str, float] = defaultdict(float)
    boosted_scores: dict[str, float] = defaultdict(float)

    for card in cards:
        card_id = card["id"]
        if allowed_kinds is not None and card["card_kind"] not in allowed_kinds:
            continue
        for detail in card["lookup_term_details"]:
            if not detail["enabled_for_ranking"]:
                continue
            direct_scores[card_id] += score_text_match(query, detail["term"]) * float(
                detail["weight"]
            )
        for shape in card.get("code_shapes", []):
            direct_scores[card_id] += score_shape_match(query, shape)

    for card_id, score in direct_scores.items():
        if score <= 0:
            continue
        boosted_scores[card_id] += round(score, 4)
        source_card = cards_by_id[card_id]
        for field, weight in policy["relation_boost_weights"].items():
            if weight <= 0:
                continue
            for related_id in source_card.get(field, []):
                if (
                    allowed_kinds is not None
                    and cards_by_id[related_id]["card_kind"] not in allowed_kinds
                ):
                    continue
                boosted_scores[related_id] += round(score * float(weight), 4)

    ranked = [(card_id, score) for card_id, score in boosted_scores.items() if score > 0]
    ranked.sort(key=lambda item: (-item[1], order[item[0]], item[0]))
    return ranked
