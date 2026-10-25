from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from rgb_website.database.session import get_db

router = APIRouter()
DatabaseSession = Annotated[Session, Depends(get_db)]
EXPECTED_SCHEMA_REVISION = "0005_session_gender"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness(db: DatabaseSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        revision = db.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application dependencies are not ready.",
        ) from error
    if revision != EXPECTED_SCHEMA_REVISION:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application dependencies are not ready.",
        )
    return {"status": "ready"}
