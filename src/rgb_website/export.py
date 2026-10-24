import csv
from collections.abc import Iterator
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from rgb_website.models import Response, SurveySession

CSV_COLUMNS = (
    "session_id",
    "session_status",
    "experiment_version",
    "gender",
    "trial_count",
    "trial_number",
    "color_id",
    "color_r",
    "color_g",
    "color_b",
    "emotion",
    "response_timestamp",
)


def _safe_text(value: str | None) -> str:
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


def _csv_row(values: list[object]) -> str:
    buffer = StringIO()
    csv.writer(buffer, lineterminator="\r\n").writerow(values)
    return buffer.getvalue()


def iter_csv_rows(db: Session) -> Iterator[str]:
    yield _csv_row(list(CSV_COLUMNS))
    statement = (
        select(SurveySession, Response)
        .join(Response, Response.session_id == SurveySession.id)
        .order_by(SurveySession.id, Response.trial_number)
    )
    for session, response in db.execute(statement):
        yield _csv_row(
            [
                _safe_text(session.id),
                _safe_text(session.status),
                _safe_text(session.experiment_version),
                _safe_text(session.gender),
                session.trial_count,
                response.trial_number,
                _safe_text(response.color_id),
                response.color_r,
                response.color_g,
                response.color_b,
                _safe_text(response.emotion),
                response.response_timestamp.isoformat()
                if response.response_timestamp
                else "",
            ]
        )
