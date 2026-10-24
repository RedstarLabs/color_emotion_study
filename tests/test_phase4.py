from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from rgb_website.config import Settings, get_settings
from rgb_website.database.base import Base
from rgb_website.database.session import get_db
from rgb_website.export import _safe_text, iter_csv_rows
from rgb_website.main import create_app


@pytest.fixture
def phase4_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    app = create_app()

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_random_colors_accept_rgb_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    values = iter((0, 255, 0, 255, 0, 255))
    monkeypatch.setattr("rgb_website.experiment.randbelow", lambda _: next(values))

    from rgb_website.experiment import generate_random_color

    color = generate_random_color("trial-1")
    assert (color.red, color.green, color.blue) == (0, 255, 0)


def test_trial_count_is_configurable_and_snapshotted(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFAULT_TRIAL_COUNT", "15")
    get_settings.cache_clear()
    started = phase4_client.post("/api/experiments")

    assert started.status_code == 201
    body = started.json()
    assert body["total_count"] == 15

    monkeypatch.setenv("DEFAULT_TRIAL_COUNT", "10")
    get_settings.cache_clear()
    state = phase4_client.get(f"/api/experiments/{body['session_id']}")
    assert state.json()["total_count"] == 15


def test_fifteen_trial_session_completes(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFAULT_TRIAL_COUNT", "15")
    get_settings.cache_clear()
    started = phase4_client.post("/api/experiments").json()
    endpoint = f"/api/experiments/{started['session_id']}/responses"

    for trial_number in range(1, 16):
        state = phase4_client.get(f"/api/experiments/{started['session_id']}").json()
        response = phase4_client.post(
            endpoint,
            json={
                "color_id": state["next_color"]["id"],
                "emotion": "Überraschung",
                "trial_number": trial_number,
                "experiment_version": state["experiment_version"],
            },
        )
        assert response.status_code == 200

    assert (
        phase4_client.get(f"/api/experiments/{started['session_id']}").json()["status"]
        == "completed"
    )


def test_invalid_trial_count_configuration_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(default_trial_count=11)


def test_export_requires_token_and_protects_formula_text(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ADMIN_API_TOKEN", "test-token")
    get_settings.cache_clear()
    session_id = phase4_client.post("/api/experiments").json()["session_id"]
    state = phase4_client.get(f"/api/experiments/{session_id}").json()
    phase4_client.post(
        f"/api/experiments/{session_id}/responses",
        json={
            "color_id": state["next_color"]["id"],
            "emotion": "Freude",
            "trial_number": 1,
            "experiment_version": state["experiment_version"],
        },
    )

    assert phase4_client.get("/api/admin/export").status_code == 401
    exported = phase4_client.get(
        "/api/admin/export",
        headers={"X-Admin-Token": "test-token"},
    )
    assert exported.status_code == 200
    assert exported.headers["cache-control"] == "no-store"
    assert "response_timestamp" in exported.text.splitlines()[0]
    assert "gender" in exported.text.splitlines()[0]
    assert _safe_text("=formula") == "'=formula"


def test_export_is_closed_when_token_is_not_configured(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ADMIN_API_TOKEN", raising=False)
    get_settings.cache_clear()

    assert phase4_client.get("/api/admin/export").status_code == 503


def test_legacy_trust_and_optional_gender_are_exported_unchanged(
    db_session,
) -> None:
    from rgb_website.services import SurveyService

    service = SurveyService(db_session)
    service.create_session(
        "legacy-export",
        experiment_version="random-rgb-1.0",
        gender=None,
    )
    session = service.get_session("legacy-export")
    assert session is not None
    color = service.get_next_color(session)
    assert color is not None
    service.add_response(
        session_id="legacy-export",
        color_id=color.color_id,
        trial_number=1,
        emotion="Vertrauen",
        experiment_version="random-rgb-1.0",
    )

    rows = list(iter_csv_rows(db_session))
    assert "gender" in rows[0]
    assert "Vertrauen" in rows[1]


def test_named_constraints_are_present() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    names = {
        constraint["name"]
        for table in ("responses", "session_colors", "survey_sessions")
        for constraint in inspect(engine).get_check_constraints(table)
    }
    assert {
        "ck_responses_trial_number",
        "ck_responses_color_r",
        "ck_colors_position",
        "ck_sessions_trial_count",
        "ck_sessions_status",
        "ck_sessions_gender",
    } <= names
    Base.metadata.drop_all(engine)
