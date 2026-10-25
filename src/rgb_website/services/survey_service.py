from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rgb_website.experiment import (
    PALETTE_VERSION,
    TRIAL_COUNT,
    allowed_emotions_for_version,
    generate_random_colors,
)
from rgb_website.models import Response, SessionColor, SurveySession
from rgb_website.repositories import ResponseRepository, SurveySessionRepository


class SurveyService:
    def __init__(self, db: Session) -> None:
        self.sessions = SurveySessionRepository(db)
        self.responses = ResponseRepository(db)
        self.db = db

    def create_session(
        self,
        session_id: str,
        experiment_version: str = PALETTE_VERSION,
        trial_count: int = TRIAL_COUNT,
        gender: str | None = "not_specified",
    ) -> SurveySession:
        if trial_count not in (10, 15):
            raise ValueError("Survey sessions must contain 10 or 15 trials.")
        if gender is not None and gender not in {
            "male",
            "female",
            "diverse",
            "not_specified",
        }:
            raise ValueError("Gender is not allowed.")
        survey_session = SurveySession(
            id=session_id,
            experiment_version=experiment_version,
            palette_version=PALETTE_VERSION,
            trial_count=trial_count,
            gender=gender,
        )
        try:
            self.sessions.add(survey_session)
            for position, color in enumerate(
                generate_random_colors(trial_count),
                start=1,
            ):
                self.sessions.add_color(
                    SessionColor(
                        session_id=session_id,
                        color_id=color.id,
                        position=position,
                        color_r=color.red,
                        color_g=color.green,
                        color_b=color.blue,
                    )
                )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        return survey_session

    def get_next_color(self, session: SurveySession) -> SessionColor | None:
        if session.status != "in_progress":
            return None
        answered_ids = {response.color_id for response in session.responses}
        return next(
            (color for color in session.colors if color.color_id not in answered_ids),
            None,
        )

    def add_response(
        self,
        *,
        session_id: str,
        color_id: str,
        trial_number: int,
        emotion: str,
        experiment_version: str,
    ) -> Response:
        session = self.sessions.get(session_id)
        if session is None:
            raise LookupError("Unknown survey session.")
        if session.status != "in_progress":
            raise ValueError("Survey session is already completed.")
        next_color = self.get_next_color(session)
        if next_color is None or next_color.color_id != color_id:
            raise ValueError("Color is not the current color for this session.")
        if trial_number != next_color.position:
            raise ValueError("Trial number does not match the current color.")
        if experiment_version != session.experiment_version:
            raise ValueError("Experiment version does not match the session.")
        if emotion not in allowed_emotions_for_version(session.experiment_version):
            raise ValueError("Emotion is not allowed.")
        response = Response(
            session_id=session_id,
            color_id=color_id,
            trial_number=trial_number,
            color_r=next_color.color_r,
            color_g=next_color.color_g,
            color_b=next_color.color_b,
            emotion=emotion,
            color_order=next_color.position,
            experiment_version=experiment_version,
            response_timestamp=datetime.now(UTC),
        )
        try:
            self.responses.add(response)
            if self.responses.count_for_session(session_id) == session.trial_count:
                session.status = "completed"
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        return response

    def abandon_session(self, session_id: str) -> SurveySession:
        session = self.sessions.get(session_id)
        if session is None:
            raise LookupError("Unknown survey session.")
        if session.status != "in_progress":
            raise ValueError("Only an active survey session can be abandoned.")
        session.status = "abandoned"
        self.db.commit()
        return session

    def get_session(self, session_id: str) -> SurveySession | None:
        return self.sessions.get(session_id)

    def get_responses(self, session_id: str) -> list[Response]:
        return self.responses.get_for_session(session_id)
