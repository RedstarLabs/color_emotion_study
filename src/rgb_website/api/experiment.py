from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rgb_website.database.session import get_db
from rgb_website.experiment import TRIAL_COUNT
from rgb_website.schemas import (
    ExperimentStateResponse,
    StartExperimentRequest,
    StartExperimentResponse,
    SubmitResponseRequest,
    SubmitResponseResult,
)
from rgb_website.services import SurveyService

router = APIRouter(prefix="/api/experiments", tags=["experiments"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _state(service: SurveyService, session_id: str) -> ExperimentStateResponse:
    session = service.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found.",
        )
    answered_count = len(session.responses)
    if (session.status == "completed" and answered_count != session.trial_count) or (
        session.status == "in_progress" and answered_count >= session.trial_count
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Experiment state is inconsistent.",
        )
    next_color = service.get_next_color(session)
    return ExperimentStateResponse(
        session_id=session.id,
        status=session.status,
        answered_count=answered_count,
        total_count=session.trial_count,
        next_color=(
            {
                "id": next_color.color_id,
                "red": next_color.color_r,
                "green": next_color.color_g,
                "blue": next_color.color_b,
                "position": next_color.position,
            }
            if next_color
            else None
        ),
        experiment_version=session.experiment_version,
        gender=session.gender,
    )


@router.post(
    "",
    response_model=StartExperimentResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_experiment(
    db: DatabaseSession,
    payload: StartExperimentRequest,
) -> StartExperimentResponse:
    service = SurveyService(db)
    session = service.create_session(
        uuid4().hex,
        trial_count=TRIAL_COUNT,
        gender=payload.gender.value,
    )
    return _state(service, session.id)


@router.get("/{session_id}", response_model=ExperimentStateResponse)
def get_experiment(
    session_id: str,
    db: DatabaseSession,
) -> ExperimentStateResponse:
    return _state(SurveyService(db), session_id)


@router.post(
    "/{session_id}/responses",
    response_model=SubmitResponseResult,
)
def submit_response(
    session_id: str,
    payload: SubmitResponseRequest,
    db: DatabaseSession,
) -> SubmitResponseResult:
    service = SurveyService(db)
    try:
        service.add_response(
            session_id=session_id,
            color_id=payload.color_id,
            trial_number=payload.trial_number,
            emotion=payload.emotion,
            experiment_version=payload.experiment_version,
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Response conflicts with the current experiment state.",
        ) from error
    return SubmitResponseResult(**_state(service, session_id).model_dump())


@router.post("/{session_id}/abandon", response_model=ExperimentStateResponse)
def abandon_experiment(
    session_id: str,
    db: DatabaseSession,
) -> ExperimentStateResponse:
    service = SurveyService(db)
    try:
        service.abandon_session(session_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _state(service, session_id)
