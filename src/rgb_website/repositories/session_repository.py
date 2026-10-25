from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rgb_website.models import SessionColor, SurveySession


class SurveySessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, survey_session: SurveySession) -> SurveySession:
        self.db.add(survey_session)
        self.db.flush()
        return survey_session

    def get(self, session_id: str) -> SurveySession | None:
        return self.db.scalar(
            select(SurveySession).where(SurveySession.id == session_id)
        )

    def add_color(self, color: SessionColor) -> SessionColor:
        self.db.add(color)
        self.db.flush()
        return color

    def count_completed(self) -> int:
        return (
            self.db.scalar(
                select(func.count(SurveySession.id)).where(
                    SurveySession.status == "completed"
                )
            )
            or 0
        )
