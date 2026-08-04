import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_expected_top_level_structure_exists() -> None:
    expected_paths = [
        "config",
        "data/raw",
        "data/interim",
        "data/processed",
        "db/init",
        "dbt/models/staging",
        "dbt/models/intermediate",
        "dbt/models/marts/powerbi",
        "docs/dashboard",
        "docs/notebook_plans",
        "docs/project_scope",
        "docs/source_register",
        "notebooks/eda",
        "reports/powerbi",
        "scripts",
        "src/workshop_market/collection",
        "src/workshop_market/cleaning",
        "src/workshop_market/quality",
        "tests/unit",
        "tests/integration",
    ]

    missing = [path for path in expected_paths if not (PROJECT_ROOT / path).exists()]

    assert missing == []


def test_environment_template_has_no_real_secret_values() -> None:
    env_example = PROJECT_ROOT / ".env.example"

    assert env_example.exists()
    assert "<set-local-password>" in env_example.read_text()


def test_pilot_scope_fixture_matches_current_plan() -> None:
    fixture = PROJECT_ROOT / "tests" / "fixtures" / "pilot_scope.json"
    pilot_scope = json.loads(fixture.read_text())

    assert pilot_scope["pilot_cities"] == ["Bengaluru", "Hyderabad"]
    assert pilot_scope["pilot_categories"] == [
        "Cooking and Baking",
        "Art and Painting",
        "Pottery and Ceramics",
        "Coffee Making",
    ]
