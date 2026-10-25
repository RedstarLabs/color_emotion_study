from collections.abc import Generator

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from rgb_website.config import get_settings
from rgb_website.database.base import Base
from rgb_website.database.session import get_db
from rgb_website.export import _safe_text, iter_csv_rows
from rgb_website.main import create_app

START_CONFIRMATIONS = {
    "age_confirmed": True,
    "information_acknowledged": True,
    "participation_consent": True,
}


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


def test_new_sessions_use_ten_trials_even_if_legacy_inputs_are_sent(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFAULT_TRIAL_COUNT", "10")
    started = phase4_client.post(
        "/api/experiments",
        json={**START_CONFIRMATIONS, "trial_count": 10},
    )

    assert started.status_code == 201
    body = started.json()
    assert body["total_count"] == 10


def test_ten_trial_session_completes(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    started = phase4_client.post("/api/experiments", json=START_CONFIRMATIONS).json()
    endpoint = f"/api/experiments/{started['session_id']}/responses"

    for trial_number in range(1, 11):
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


def test_export_requires_token_and_protects_formula_text(
    phase4_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ADMIN_API_TOKEN", "test-token")
    get_settings.cache_clear()
    session_id = phase4_client.post(
        "/api/experiments",
        json=START_CONFIRMATIONS,
    ).json()["session_id"]
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
    assert (
        phase4_client.get(
            "/api/admin/export",
            headers={"X-Admin-Token": "wrong-token"},
        ).status_code
        == 401
    )
    exported = phase4_client.get(
        "/api/admin/export",
        headers={"X-Admin-Token": "test-token"},
    )
    assert exported.status_code == 200
    assert exported.headers["cache-control"] == "no-store"
    assert exported.headers["x-content-type-options"] == "nosniff"
    assert "response_timestamp" in exported.text.splitlines()[0]
    assert "gender" in exported.text.splitlines()[0]
    assert _safe_text("=formula") == "'=formula"


def test_admin_rejects_unicode_token_without_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from rgb_website.api.admin import _require_admin

    monkeypatch.setenv("ADMIN_API_TOKEN", "test-token")
    get_settings.cache_clear()

    with pytest.raises(HTTPException) as error:
        _require_admin("falsches-Töken-😀")

    assert error.value.status_code == 401


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
        trial_count=15,
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
    service.create_session("current-export", trial_count=10)
    current_session = service.get_session("current-export")
    assert current_session is not None
    current_color = service.get_next_color(current_session)
    assert current_color is not None
    service.add_response(
        session_id="current-export",
        color_id=current_color.color_id,
        trial_number=1,
        emotion="Freude",
        experiment_version="random-rgb-2.0",
    )

    rows = list(iter_csv_rows(db_session))
    assert "gender" in rows[0]
    assert any("Vertrauen" in row for row in rows[1:])
    assert any(",15," in row for row in rows[1:])
    assert any(",10," in row for row in rows[1:])


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
