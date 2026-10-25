import pytest

from rgb_website.models import SurveySession
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


def test_direct_session_model_defaults_to_ten_trials(db_session) -> None:
    session = SurveySession(id="model-default-session")
    db_session.add(session)
    db_session.flush()

    assert session.trial_count == 10


def test_session_trial_count_must_be_ten_or_fifteen(db_session) -> None:
    service = SurveyService(db_session)

    with pytest.raises(ValueError, match="10 or 15 trials"):
        service.create_session("invalid-trial-session", trial_count=11)

    service.create_session("legacy-fifteen-session", trial_count=15)
    session = service.get_session("legacy-fifteen-session")
    assert session is not None
    assert session.trial_count == 15
    assert len(session.colors) == 15

    for trial_number in range(1, 16):
        color = service.get_next_color(session)
        assert color is not None
        service.add_response(
            session_id=session.id,
            color_id=color.color_id,
            trial_number=trial_number,
            emotion="Freude",
            experiment_version=session.experiment_version,
        )

    assert service.get_session(session.id).status == "completed"


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


def test_legacy_version_preserves_sadness_label(db_session) -> None:
    service = SurveyService(db_session)
    service.create_session("legacy-sadness", experiment_version="random-rgb-1.0")
    session = service.get_session("legacy-sadness")
    assert session is not None
    color = service.get_next_color(session)
    assert color is not None

    response = service.add_response(
        session_id="legacy-sadness",
        color_id=color.color_id,
        trial_number=1,
        emotion="Trauer",
        experiment_version="random-rgb-1.0",
    )

    assert response.emotion == "Trauer"
