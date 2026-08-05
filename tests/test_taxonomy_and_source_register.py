import csv
import json
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = PROJECT_ROOT / "config" / "taxonomy" / "pilot_scope.yml"
SOURCE_REGISTER_PATH = PROJECT_ROOT / "docs" / "source_register" / "source_register.csv"
SOURCE_BACKLOG_PATH = PROJECT_ROOT / "docs" / "source_register" / "source_discovery_backlog.csv"


def load_taxonomy() -> dict:
    return yaml.safe_load(TAXONOMY_PATH.read_text())


def load_source_register() -> list[dict[str, str]]:
    with SOURCE_REGISTER_PATH.open(newline="") as source_file:
        return list(csv.DictReader(source_file))


def load_source_backlog() -> list[dict[str, str]]:
    with SOURCE_BACKLOG_PATH.open(newline="") as source_file:
        return list(csv.DictReader(source_file))


def test_pilot_cities_are_bengaluru_and_hyderabad() -> None:
    taxonomy = load_taxonomy()
    cities = [city["city_name"] for city in taxonomy["pilot"]["cities"]]

    assert cities == ["Bengaluru", "Hyderabad"]


def test_exactly_four_primary_pilot_categories_and_coffee_exists() -> None:
    taxonomy = load_taxonomy()
    categories = taxonomy["pilot"]["primary_categories"]
    category_names = [category["primary_category_name"] for category in categories]
    category_codes = [category["primary_category_code"] for category in categories]

    assert len(categories) == 4
    assert "Coffee Making" in category_names
    assert "coffee_making" in category_codes


def test_excluded_categories_are_not_pilot_categories() -> None:
    taxonomy = load_taxonomy()
    category_text = " ".join(
        [
            category["primary_category_name"]
            for category in taxonomy["pilot"]["primary_categories"]
        ]
    ).lower()

    assert "stem" not in category_text
    assert "coding" not in category_text
    assert "robotics" not in category_text


def test_category_codes_are_unique() -> None:
    taxonomy = load_taxonomy()
    codes = [
        category["primary_category_code"]
        for category in taxonomy["pilot"]["primary_categories"]
    ]

    assert len(codes) == len(set(codes))


def test_subcategory_codes_are_unique_within_primary_category() -> None:
    taxonomy = load_taxonomy()

    for category in taxonomy["pilot"]["primary_categories"]:
        codes = [
            subcategory["subcategory_code"]
            for subcategory in category["subcategories"]
        ]
        assert len(codes) == len(set(codes)), category["primary_category_code"]


def test_every_subcategory_maps_to_valid_primary_category() -> None:
    taxonomy = load_taxonomy()
    primary_codes = {
        category["primary_category_code"]
        for category in taxonomy["pilot"]["primary_categories"]
    }

    for category in taxonomy["pilot"]["primary_categories"]:
        assert category["primary_category_code"] in primary_codes
        assert category["subcategories"]


def test_price_tiers_do_not_overlap() -> None:
    taxonomy = load_taxonomy()
    tiers = taxonomy["controlled_taxonomies"]["price_tiers"]
    finite_ranges = [
        (tier["price_tier_code"], tier["min_inr"], tier["max_inr"])
        for tier in tiers
        if tier["max_inr"] is not None
    ]

    for index, (code, min_inr, max_inr) in enumerate(finite_ranges):
        assert min_inr <= max_inr, code
        for other_code, other_min, other_max in finite_ranges[index + 1 :]:
            assert max_inr < other_min or other_max < min_inr, (code, other_code)

    high_premium = next(
        tier for tier in tiers if tier["price_tier_code"] == "high_premium"
    )
    assert high_premium["min_inr"] == 5000
    assert high_premium["max_inr"] is None


def test_event_status_values_are_unique_and_registration_closed_is_separate() -> None:
    taxonomy = load_taxonomy()
    statuses = taxonomy["controlled_taxonomies"]["event_statuses"]

    assert len(statuses) == len(set(statuses))
    assert "registration_closed" in statuses
    assert "sold_out" in statuses
    assert statuses.index("registration_closed") != statuses.index("sold_out")


def test_mirrored_fixture_matches_canonical_taxonomy() -> None:
    taxonomy = load_taxonomy()
    fixture = json.loads((PROJECT_ROOT / "tests" / "fixtures" / "pilot_scope.json").read_text())

    assert fixture["pilot_cities"] == [
        {
            "city_code": city["city_code"],
            "city_name": city["city_name"],
            "metro_region": city["metro_region"],
        }
        for city in taxonomy["pilot"]["cities"]
    ]
    assert fixture["pilot_categories"] == [
        {
            "primary_category_code": category["primary_category_code"],
            "primary_category_name": category["primary_category_name"],
        }
        for category in taxonomy["pilot"]["primary_categories"]
    ]


def test_required_source_register_columns_exist() -> None:
    with SOURCE_REGISTER_PATH.open(newline="") as source_file:
        reader = csv.DictReader(source_file)
        columns = set(reader.fieldnames or [])

    required_columns = {
        "source_id",
        "source_name",
        "source_type",
        "base_url",
        "cities_supported",
        "categories_supported",
        "product_types_supported",
        "current_or_historical",
        "earliest_observed_date",
        "expected_update_frequency",
        "available_fields",
        "demand_signals_available",
        "access_method",
        "authentication_required",
        "cost_or_subscription",
        "robots_or_terms_review_status",
        "automation_permission_status",
        "rate_limit_or_collection_limit",
        "historical_depth",
        "data_quality_rating",
        "source_reliability",
        "duplicate_risk",
        "pilot_priority",
        "manual_validation_required",
        "known_limitations",
        "last_reviewed_date",
        "reviewer_notes",
        "terms_url",
        "privacy_url",
        "robots_url",
        "api_documentation_url",
        "review_evidence_url",
        "reviewed_by",
        "reviewed_at",
        "collection_decision",
        "collection_decision_reason",
        "permitted_use_scope",
        "permitted_fields",
        "prohibited_fields",
        "re_review_date",
        "written_permission_required",
        "data_retention_limit",
        "attribution_required",
    }

    assert required_columns.issubset(columns)


def test_source_register_controlled_values_are_valid() -> None:
    rows = load_source_register()
    valid_reliability = {"High", "Medium", "Low"}
    valid_historical_depth = {
        "Current only",
        "Less than 6 months",
        "6-12 months",
        "1-3 years",
        "More than 3 years",
        "Unknown",
    }
    valid_duplicate_risk = {"Low", "Medium", "High"}
    valid_priority = {"Essential", "Supporting", "Optional", "Excluded"}
    valid_access_status = {
        "Official API permitted",
        "Public export permitted",
        "Manual collection permitted",
        "Public-page collection pending review",
        "Automated collection prohibited or unsuitable",
        "Unknown; legal/terms review required",
    }
    valid_review_status = {"not_reviewed", "pending_review", "reviewed"}
    valid_collection_decisions = {
        "approved_official_api",
        "approved_manual_collection",
        "approved_limited_public_collection",
        "pending_review",
        "rejected",
        "not_technically_feasible",
    }

    assert rows
    for row in rows:
        assert row["source_reliability"] in valid_reliability
        assert row["historical_depth"] in valid_historical_depth
        assert row["duplicate_risk"] in valid_duplicate_risk
        assert row["pilot_priority"] in valid_priority
        assert row["automation_permission_status"] in valid_access_status
        assert row["robots_or_terms_review_status"] in valid_review_status
        assert row["collection_decision"] in valid_collection_decisions


def test_every_source_register_row_represents_concrete_source() -> None:
    rows = load_source_register()
    generic_source_ids = {
        "organizer_websites",
        "public_studio_calendars",
        "coffee_specific_official_websites",
        "local_coffee_training_studios_to_discover",
    }
    generic_source_names = {
        "Organizer websites",
        "Public studio calendars",
        "Coffee-specific official websites",
        "Relevant Bengaluru and Hyderabad coffee schools, roasters, cafes, and training studios found during later discovery",
    }

    assert rows
    for row in rows:
        assert row["source_id"] not in generic_source_ids
        assert row["source_name"] not in generic_source_names


def test_generic_discovery_rows_are_stored_in_backlog() -> None:
    rows = load_source_backlog()
    source_families = {row["source_family"] for row in rows}
    required_families = {
        "Organizer websites",
        "Public studio calendars",
        "Coffee-specific official websites",
        "Relevant local coffee schools, roasters, cafes, and training studios",
    }

    assert required_families.issubset(source_families)


def test_required_source_discovery_backlog_columns_exist() -> None:
    with SOURCE_BACKLOG_PATH.open(newline="") as source_file:
        reader = csv.DictReader(source_file)
        columns = set(reader.fieldnames or [])

    required_columns = {
        "discovery_id",
        "source_family",
        "city",
        "category",
        "discovery_query_or_method",
        "priority",
        "status",
        "notes",
    }

    assert required_columns.issubset(columns)


def test_no_source_is_approved_for_automated_collection() -> None:
    rows = load_source_register()
    automation_approval_values = {"Official API permitted", "Public export permitted"}

    assert all(row["automation_permission_status"] not in automation_approval_values for row in rows)


def test_day4_manual_approvals_remain_manual_only() -> None:
    rows = load_source_register()
    manual_sources = [row for row in rows if row["collection_decision"] == "approved_manual_collection"]

    assert manual_sources
    for row in manual_sources:
        assert row["automation_permission_status"] == "Automated collection prohibited or unsuitable"
        assert "manual" in row["permitted_use_scope"]
        assert row["review_evidence_url"].strip()


def test_district_and_bookmyshow_are_not_approved_for_automated_bulk_collection() -> None:
    rows = {row["source_id"]: row for row in load_source_register()}

    for source_id in ["district", "bookmyshow"]:
        row = rows[source_id]
        assert row["collection_decision"] == "pending_review"
        assert row["automation_permission_status"] == "Automated collection prohibited or unsuitable"
        assert "bulk" in row["collection_decision_reason"].lower()
        assert row["written_permission_required"] == "yes"


def test_review_evidence_fields_are_recorded_for_preliminary_reviews() -> None:
    rows = {row["source_id"]: row for row in load_source_register()}

    assert rows["district"]["terms_url"] == "https://www.district.in/policies/terms-of-service"
    assert rows["district"]["reviewed_by"] == "Codex"
    assert rows["district"]["reviewed_at"]
    assert rows["district"]["re_review_date"] == "2026-09-04"
    assert rows["bookmyshow"]["terms_url"] == "https://in.bookmyshow.com/terms-and-conditions"
    assert rows["bookmyshow"]["robots_url"] == "https://in.bookmyshow.com/robots.txt"
    assert "sitemap" in rows["bookmyshow"]["review_evidence_url"]


def test_no_source_has_automation_approval_without_review() -> None:
    rows = load_source_register()
    approved_values = {"Official API permitted", "Public export permitted", "Manual collection permitted"}

    for row in rows:
        if row["automation_permission_status"] in approved_values:
            assert row["robots_or_terms_review_status"] == "reviewed"
            assert row["reviewer_notes"].strip()


def test_approved_collection_decision_requires_evidence_and_reviewer() -> None:
    rows = load_source_register()
    approved_decisions = {
        "approved_official_api",
        "approved_manual_collection",
        "approved_limited_public_collection",
    }

    for row in rows:
        if row["collection_decision"] in approved_decisions:
            assert row["review_evidence_url"].strip()
            assert row["reviewed_by"].strip()
            assert row["reviewed_at"].strip()
            assert row["collection_decision_reason"].strip()
            assert row["permitted_use_scope"].strip()
            assert row["permitted_fields"].strip()
            assert row["prohibited_fields"].strip()
            assert row["terms_url"].strip() or row["api_documentation_url"].strip()
