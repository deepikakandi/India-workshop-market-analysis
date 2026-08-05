"""Validation helpers for Day 5 manual event-record imports.

This module validates manually entered metadata only. It does not fetch pages,
call APIs, scrape websites, or parse live workshop payloads.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from workshop_market.quality.metadata_contracts import (
    MetadataValidationError,
    _json_schema_errors,
    _raise_if_errors,
    _timestamp_errors,
    load_source_register,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "config" / "schemas"
TAXONOMY_PATH = PROJECT_ROOT / "config" / "taxonomy" / "pilot_scope.yml"
SOURCE_REGISTER_PATH = PROJECT_ROOT / "docs" / "source_register" / "source_register.csv"
MANUAL_EVENT_SCHEMA_PATH = SCHEMA_ROOT / "manual_event_record.schema.json"

MANUAL_COLLECTION_DECISIONS = {
    "approved_manual_collection",
    "approved_limited_public_collection",
}
SENSITIVE_TEXT_PATTERN = re.compile(
    r"(authorization|cookie|set-cookie|token|password|passwd|secret|session|api[-_]?key|customer phone|customer email|personal data)",
    re.IGNORECASE,
)
IMAGE_URL_PATTERN = re.compile(r"https?://\S+\.(?:jpg|jpeg|png|gif|webp|svg)(?:\?\S*)?", re.IGNORECASE)
SOURCE_APPROVED_FIELD_CHECKS = {
    "event_title_original",
    "organizer_name_original",
    "venue_name_original",
    "city_original",
    "locality_original",
    "category_original",
    "description_short_original",
    "city_code",
    "primary_category_code",
    "subcategory_code",
    "secondary_category_codes",
    "product_type_code",
    "delivery_format_code",
    "operating_model_code",
    "audience_codes",
    "minimum_age",
    "maximum_age",
    "skill_level_code",
    "event_start_at",
    "event_end_at",
    "duration_minutes",
    "recurrence_text_original",
    "recurrence_type",
    "registration_deadline",
    "listed_price_inr",
    "discounted_price_inr",
    "tax_included",
    "additional_fee_inr",
    "pricing_unit_code",
    "price_tier_code",
    "materials_included",
    "take_home_product",
    "certificate_included",
    "event_status_code",
    "seats_total",
    "seats_available",
    "interested_count",
    "sold_out_observed",
    "waitlist_available",
    "booking_required",
    "demand_signal_notes",
}


def _split_semicolon(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def load_taxonomy(path: Path = TAXONOMY_PATH) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def taxonomy_codes(taxonomy_path: Path = TAXONOMY_PATH) -> dict[str, set[str]]:
    taxonomy = load_taxonomy(taxonomy_path)
    primary_categories = taxonomy["pilot"]["primary_categories"]
    subcategory_pairs = {
        (
            category["primary_category_code"],
            subcategory["subcategory_code"],
        )
        for category in primary_categories
        for subcategory in category["subcategories"]
    }
    return {
        "cities": {city["city_code"] for city in taxonomy["pilot"]["cities"]},
        "primary_categories": {category["primary_category_code"] for category in primary_categories},
        "subcategory_pairs": subcategory_pairs,
        "product_types": set(taxonomy["controlled_taxonomies"]["product_event_types"]),
        "delivery_formats": set(taxonomy["controlled_taxonomies"]["delivery_formats"]),
        "operating_models": set(taxonomy["controlled_taxonomies"]["operating_models"]),
        "audience_segments": {
            segment["audience_code"] for segment in taxonomy["controlled_taxonomies"]["audience_segments"]
        },
        "event_statuses": set(taxonomy["controlled_taxonomies"]["event_statuses"]),
        "skill_levels": set(taxonomy["controlled_taxonomies"]["skill_levels"]),
        "pricing_units": set(taxonomy["controlled_taxonomies"]["pricing_units"]),
        "price_tiers": {
            tier["price_tier_code"] for tier in taxonomy["controlled_taxonomies"]["price_tiers"]
        },
    }


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _source_permission_errors(record: dict[str, Any], source_register_path: Path) -> list[str]:
    errors: list[str] = []
    sources = load_source_register(source_register_path)
    source_id = record.get("source_id")
    row = sources.get(source_id)
    if row is None:
        return [f"source_id is not in source register: {source_id}"]

    decision = row.get("collection_decision", "")
    if decision not in MANUAL_COLLECTION_DECISIONS:
        errors.append(f"source_id {source_id} is not approved for manual collection: {decision}")

    evidence_fields = [
        "review_evidence_url",
        "reviewed_by",
        "reviewed_at",
        "collection_decision_reason",
        "permitted_use_scope",
        "permitted_fields",
        "prohibited_fields",
    ]
    missing = [field for field in evidence_fields if not row.get(field, "").strip()]
    if missing:
        errors.append(f"source_id {source_id} is missing review evidence fields: {', '.join(missing)}")

    permitted = _split_semicolon(row.get("permitted_fields", ""))
    populated_source_fields = {
        field
        for field in SOURCE_APPROVED_FIELD_CHECKS
        if field in record and _non_empty(record[field])
    }
    outside_scope = sorted(populated_source_fields - permitted)
    if outside_scope:
        errors.append(
            f"manual record contains fields outside approved source scope for {source_id}: {', '.join(outside_scope)}"
        )
    return errors


def _controlled_value_errors(record: dict[str, Any], taxonomy_path: Path) -> list[str]:
    codes = taxonomy_codes(taxonomy_path)
    errors: list[str] = []
    checks = [
        ("city_code", "cities"),
        ("primary_category_code", "primary_categories"),
        ("product_type_code", "product_types"),
        ("delivery_format_code", "delivery_formats"),
        ("operating_model_code", "operating_models"),
        ("event_status_code", "event_statuses"),
        ("skill_level_code", "skill_levels"),
        ("pricing_unit_code", "pricing_units"),
        ("price_tier_code", "price_tiers"),
    ]
    for field, group in checks:
        value = record.get(field)
        if value not in codes[group]:
            errors.append(f"{field} has invalid value: {value}")

    for field in ["secondary_category_codes", "audience_codes"]:
        values = record.get(field, [])
        if not isinstance(values, list):
            continue
        allowed = codes["primary_categories"] if field == "secondary_category_codes" else codes["audience_segments"]
        invalid = sorted({value for value in values if value not in allowed})
        if invalid:
            errors.append(f"{field} contains invalid values: {', '.join(invalid)}")

    subcategory = record.get("subcategory_code")
    if subcategory is not None:
        pair = (record.get("primary_category_code"), subcategory)
        if pair not in codes["subcategory_pairs"]:
            errors.append(
                f"subcategory_code {subcategory} is not valid for primary_category_code {record.get('primary_category_code')}"
            )
    return errors


def _business_rule_errors(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    listed_price = record.get("listed_price_inr")
    discounted_price = record.get("discounted_price_inr")
    if listed_price is not None and listed_price < 0:
        errors.append("listed_price_inr must be non-negative")
    if discounted_price is not None and discounted_price < 0:
        errors.append("discounted_price_inr must be non-negative")
    if listed_price is not None and discounted_price is not None and discounted_price > listed_price:
        errors.append("discounted_price_inr must not exceed listed_price_inr")

    minimum_age = record.get("minimum_age")
    maximum_age = record.get("maximum_age")
    if minimum_age is not None and maximum_age is not None and minimum_age > maximum_age:
        errors.append("minimum_age must not exceed maximum_age")

    seats_total = record.get("seats_total")
    seats_available = record.get("seats_available")
    if seats_total is not None and seats_available is not None and seats_available > seats_total:
        errors.append("seats_available must not exceed seats_total")

    if record.get("event_status_code") == "registration_closed" and record.get("sold_out_observed") is True:
        errors.append("sold_out_observed must not be inferred from registration_closed")

    description = record.get("description_short_original")
    if isinstance(description, str) and len(description) > 280:
        errors.append("description_short_original must be a short researcher-written summary")

    for key, value in record.items():
        if SENSITIVE_TEXT_PATTERN.search(key):
            errors.append(f"manual record contains disallowed sensitive field name: {key}")
        if isinstance(value, str):
            if SENSITIVE_TEXT_PATTERN.search(value):
                errors.append(f"manual record contains sensitive text in {key}")
            if IMAGE_URL_PATTERN.search(value):
                errors.append(f"manual record contains image URL in {key}")
    return errors


def validate_manual_event_record(
    record: dict[str, Any],
    *,
    source_register_path: Path = SOURCE_REGISTER_PATH,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> None:
    """Validate one manually entered event/course record."""

    errors = _json_schema_errors(record, MANUAL_EVENT_SCHEMA_PATH)
    if not isinstance(record.get("source_url"), str) or not record.get("source_url", "").strip():
        errors.append("source_url is required")
    if not isinstance(record.get("evidence_url"), str) or not record.get("evidence_url", "").strip():
        errors.append("evidence_url is required")
    errors.extend(
        _timestamp_errors(
            record,
            ["observed_at", "event_start_at", "event_end_at", "registration_deadline"],
        )
    )
    errors.extend(_source_permission_errors(record, source_register_path))
    errors.extend(_controlled_value_errors(record, taxonomy_path))
    errors.extend(_business_rule_errors(record))
    _raise_if_errors(errors)
