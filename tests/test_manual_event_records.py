import copy
import csv
import json
from pathlib import Path

import pytest
import yaml

from workshop_market.quality.manual_event_records import validate_manual_event_record
from workshop_market.quality.metadata_contracts import MetadataValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"
SOURCE_REGISTER_PATH = PROJECT_ROOT / "docs" / "source_register" / "source_register.csv"
SELECTION_PATH = PROJECT_ROOT / "config" / "pilot" / "manual_source_selection.yml"
REVIEWS = PROJECT_ROOT / "docs" / "source_register" / "reviews"


def load_fixture() -> dict:
    return json.loads((FIXTURES / "manual_event_record_valid.json").read_text())


def load_sources() -> dict[str, dict[str, str]]:
    with SOURCE_REGISTER_PATH.open(newline="") as source_file:
        return {row["source_id"]: row for row in csv.DictReader(source_file)}


def load_selection() -> dict:
    return yaml.safe_load(SELECTION_PATH.read_text())


def test_valid_manual_event_record_passes() -> None:
    validate_manual_event_record(load_fixture())


def test_manual_record_unknown_source_fails() -> None:
    record = load_fixture()
    record["source_id"] = "unknown_source"

    with pytest.raises(MetadataValidationError, match="not in source register"):
        validate_manual_event_record(record)


def test_manual_record_unapproved_source_fails() -> None:
    record = load_fixture()
    record["source_id"] = "lavonne"

    with pytest.raises(MetadataValidationError, match="not approved for manual collection"):
        validate_manual_event_record(record)


def test_manual_record_invalid_city_fails() -> None:
    record = load_fixture()
    record["city_code"] = "pune"

    with pytest.raises(MetadataValidationError, match="city_code"):
        validate_manual_event_record(record)


def test_manual_record_invalid_category_fails() -> None:
    record = load_fixture()
    record["primary_category_code"] = "robotics"

    with pytest.raises(MetadataValidationError, match="primary_category_code"):
        validate_manual_event_record(record)


def test_manual_record_negative_price_fails() -> None:
    record = load_fixture()
    record["listed_price_inr"] = -1

    with pytest.raises(MetadataValidationError, match="listed_price_inr"):
        validate_manual_event_record(record)


def test_manual_record_discount_above_list_price_fails() -> None:
    record = load_fixture()
    record["discounted_price_inr"] = 2500

    with pytest.raises(MetadataValidationError, match="discounted_price_inr"):
        validate_manual_event_record(record)


def test_manual_record_minimum_age_above_maximum_fails() -> None:
    record = load_fixture()
    record["minimum_age"] = 60
    record["maximum_age"] = 18

    with pytest.raises(MetadataValidationError, match="minimum_age"):
        validate_manual_event_record(record)


def test_manual_record_seats_available_above_total_fails() -> None:
    record = load_fixture()
    record["seats_available"] = 20

    with pytest.raises(MetadataValidationError, match="seats_available"):
        validate_manual_event_record(record)


def test_manual_record_missing_source_url_fails() -> None:
    record = load_fixture()
    record["source_url"] = ""

    with pytest.raises(MetadataValidationError, match="source_url"):
        validate_manual_event_record(record)


def test_manual_record_missing_evidence_url_fails() -> None:
    record = load_fixture()
    record["evidence_url"] = ""

    with pytest.raises(MetadataValidationError, match="evidence_url"):
        validate_manual_event_record(record)


def test_manual_record_naive_observation_timestamp_fails() -> None:
    record = load_fixture()
    record["observed_at"] = "2026-08-05T12:00:00"

    with pytest.raises(MetadataValidationError, match="timezone"):
        validate_manual_event_record(record)


def test_manual_record_long_copied_description_fails() -> None:
    record = load_fixture()
    record["description_short_original"] = "This copied-looking source description is too long. " * 20

    with pytest.raises(MetadataValidationError, match="description_short_original"):
        validate_manual_event_record(record)


def test_manual_record_image_url_or_personal_data_fails() -> None:
    for field, value, match in [
        ("description_short_original", "Image at https://example.com/photo.jpg", "image URL"),
        ("reviewer_notes", "Contains customer email from source", "sensitive text"),
    ]:
        record = load_fixture()
        record[field] = value
        with pytest.raises(MetadataValidationError, match=match):
            validate_manual_event_record(record)


def test_manual_record_registration_closed_is_not_sold_out_fails() -> None:
    record = load_fixture()
    record["event_status_code"] = "registration_closed"
    record["sold_out_observed"] = True

    with pytest.raises(MetadataValidationError, match="sold_out_observed"):
        validate_manual_event_record(record)


def test_manual_record_cannot_use_fields_outside_source_scope(tmp_path: Path) -> None:
    sources = load_sources()
    row = copy.deepcopy(sources["mud_effects"])
    row["permitted_fields"] = "event_title_original; primary_category_code"
    source_register = tmp_path / "source_register.csv"
    with source_register.open("w", newline="") as source_file:
        writer = csv.DictWriter(source_file, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    with pytest.raises(MetadataValidationError, match="outside approved source scope"):
        validate_manual_event_record(load_fixture(), source_register_path=source_register)


def test_every_selected_manual_source_has_individual_review() -> None:
    selected = load_selection()["selected_sources"]
    for source in selected:
        review_path = REVIEWS / f"{source['source_id']}.yml"
        assert review_path.exists(), source["source_id"]
        review = yaml.safe_load(review_path.read_text())
        assert review["is_template"] is False
        assert review["source_id"] == source["source_id"]


def test_selected_sources_are_concrete_and_approved_only_for_manual_scope() -> None:
    sources = load_sources()
    selected = load_selection()["selected_sources"]
    generic_ids = {"organizer_websites", "public_studio_calendars", "coffee_specific_official_websites"}

    for selection in selected:
        source_id = selection["source_id"]
        row = sources[source_id]
        assert source_id not in generic_ids
        assert row["collection_decision"] == "approved_manual_collection"
        assert row["automation_permission_status"] == "Automated collection prohibited or unsuitable"
        assert "manual" in row["permitted_use_scope"]
        assert selection["collection_decision"] == "approved_manual_collection"


def test_manual_source_selection_covers_both_cities_and_all_categories() -> None:
    selected = load_selection()["selected_sources"]
    cities = {source["city"] for source in selected}
    city_categories: dict[str, set[str]] = {city: set() for city in cities}
    for source in selected:
        city_categories[source["city"]].update(source["category_codes"])

    required_categories = {
        "cooking_and_baking",
        "art_and_painting",
        "pottery_and_ceramics",
        "coffee_making",
    }

    assert cities == {"bengaluru", "hyderabad"}
    assert city_categories["bengaluru"] >= required_categories
    assert city_categories["hyderabad"] >= required_categories
    assert sum(1 for source in selected if source["city"] == "bengaluru") >= 3
    assert sum(1 for source in selected if source["city"] == "hyderabad") >= 3


def test_aestraa_maps_only_to_art_and_painting() -> None:
    sources = load_sources()
    selection = load_selection()
    review = yaml.safe_load((REVIEWS / "aestraa.yml").read_text())
    selected_aestraa = [
        source for source in selection["selected_sources"] if source["source_id"] == "aestraa"
    ]

    assert sources["aestraa"]["categories_supported"] == "Art and Painting"
    assert selected_aestraa
    assert selected_aestraa[0]["category_codes"] == ["art_and_painting"]
    assert review["source_identity"]["categories_supported"] == ["Art and Painting"]
    assert review["data_usefulness"]["workshop_categories_covered"] == ["Art and Painting"]


def test_manual_source_selection_targets_are_flexible_and_reasonable() -> None:
    selection = load_selection()
    selected = selection["selected_sources"]
    policy = selection["manual_collection_policy"]
    target_total = 0

    assert "approximately 40-70" in policy["desired_overall_record_range"]
    assert policy["range_is_mandatory"] is False
    assert policy["quality_and_uniqueness_priority"] is True
    assert "Falling below 40" in policy["shortfall_policy"]

    for source in selected:
        minimum = source["minimum_expected_records"]
        target = source["target_records"]
        maximum = source["maximum_records"]
        assert minimum <= target <= maximum
        assert minimum >= 0
        assert maximum <= 10
        assert source["record_shortfall_allowed"] is True
        assert source["observation_window"]
        assert isinstance(source["historical_records_allowed"], bool)
        assert source["historical_coverage_notes"]
        target_total += target

    assert 40 <= target_total <= 70


def test_distinct_record_rule_prevents_manufactured_quota_records() -> None:
    policy = load_selection()["manual_collection_policy"]
    rule = policy["distinct_record_rule"]

    assert "distinct workshop occurrence" in rule
    assert "distinct recurring" in rule
    assert "distinct course product" in rule
    assert "must not be duplicated" in rule
    assert "meet a source target" in rule
    assert policy["range_is_mandatory"] is False


def test_selection_includes_required_manual_pilot_characteristics() -> None:
    selected = load_selection()["selected_sources"]
    product_types = {product for source in selected for product in source["product_types"]}
    selected_ids = {source["source_id"] for source in selected}

    assert "recurring_class" in product_types or "professional_course" in product_types
    assert "individual_one_time_workshop" in product_types
    assert "escapades" in selected_ids
    assert "scai" in selected_ids


def test_somethings_brewing_is_not_approved_for_automated_collection() -> None:
    row = load_sources()["somethings_brewing"]

    assert row["automation_permission_status"] == "Automated collection prohibited or unsuitable"
    assert row["collection_decision"] == "pending_review"
    assert "scraping" in row["collection_decision_reason"].lower()


def test_no_source_is_approved_for_automation_without_permission_basis() -> None:
    for row in load_sources().values():
        if row["automation_permission_status"] in {"Official API permitted", "Public export permitted"}:
            assert row["collection_decision"] in {"approved_official_api", "approved_limited_public_collection"}
            assert row["api_documentation_url"].strip() or "permission" in row["permitted_use_scope"].lower()
            assert row["review_evidence_url"].strip()


def test_lavonne_is_reviewed_but_not_selected_for_manual_collection() -> None:
    selection = load_selection()
    selected_ids = {source["source_id"] for source in selection["selected_sources"]}
    excluded_ids = {source["source_id"] for source in selection["excluded_sources"]}
    row = load_sources()["lavonne"]

    assert "lavonne" not in selected_ids
    assert "lavonne" in excluded_ids
    assert row["collection_decision"] == "pending_review"
    assert row["automation_permission_status"] == "Automated collection prohibited or unsuitable"
