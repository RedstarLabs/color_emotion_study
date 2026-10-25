import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from rgb_website.config import get_settings
from rgb_website.database.session import get_db
from rgb_website.export import iter_csv_rows

router = APIRouter(prefix="/api/admin", tags=["admin"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _require_admin(token: str | None) -> None:
    configured_token = get_settings().admin_api_token
    if not configured_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrative export is not configured.",
        )
    if token is None:
        token_matches = False
    else:
        try:
            token_matches = secrets.compare_digest(
                token.encode("utf-8"),
                configured_token.encode("utf-8"),
            )
        except UnicodeEncodeError:
            token_matches = False
    if not token_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrative authentication required.",
        )


@router.get("/export")
def export_csv(
    db: DatabaseSession,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> StreamingResponse:
    _require_admin(x_admin_token)
    return StreamingResponse(
        iter_csv_rows(db),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="responses.csv"',
            "Cache-Control": "no-store",
        },
    )
