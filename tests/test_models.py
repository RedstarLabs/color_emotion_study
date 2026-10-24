import pytest

from rgb_website.services import SurveyService


def test_invalid_color_id_is_not_stored(db_session) -> None:
    service = SurveyService(db_session)
    service.create_session("session-1", "1.0")
    session = service.get_session("session-1")
    assert session is not None
    color = service.get_next_color(session)
    assert color is not None

    with pytest.raises(ValueError):
        service.add_response(
            session_id="session-1",
            color_id="not-in-session",
            trial_number=1,
            emotion="Freude",
            experiment_version="1.0",
        )

    assert service.get_responses("session-1") == []


def test_new_version_rejects_trust_but_legacy_version_preserves_it(db_session) -> None:
    service = SurveyService(db_session)
    service.create_session("new-session")
    new_session = service.get_session("new-session")
    assert new_session is not None
    new_color = service.get_next_color(new_session)
    assert new_color is not None

    with pytest.raises(ValueError):
        service.add_response(
            session_id="new-session",
            color_id=new_color.color_id,
            trial_number=1,
            emotion="Vertrauen",
            experiment_version="random-rgb-2.0",
        )

    service.create_session(
        "legacy-session",
        experiment_version="random-rgb-1.0",
        gender=None,
    )
    legacy_session = service.get_session("legacy-session")
    assert legacy_session is not None
    legacy_color = service.get_next_color(legacy_session)
    assert legacy_color is not None
    response = service.add_response(
        session_id="legacy-session",
        color_id=legacy_color.color_id,
        trial_number=1,
        emotion="Vertrauen",
        experiment_version="random-rgb-1.0",
    )

    assert response.emotion == "Vertrauen"
