from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from rgb_website.experiment import PALETTE_VERSION, Emotion


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    DIVERSE = "diverse"
    NOT_SPECIFIED = "not_specified"


class StartExperimentRequest(BaseModel):
    gender: Gender = Gender.NOT_SPECIFIED


class ColorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(min_length=1, max_length=32)
    red: int = Field(ge=0, le=255)
    green: int = Field(ge=0, le=255)
    blue: int = Field(ge=0, le=255)
    position: int = Field(ge=1, le=15)


class ExperimentStateResponse(BaseModel):
    session_id: str
    status: Literal["in_progress", "completed", "abandoned"]
    answered_count: int = Field(ge=0, le=15)
    total_count: int = Field(ge=10, le=15)
    next_color: ColorResponse | None
    experiment_version: str = PALETTE_VERSION
    gender: Gender | None


class StartExperimentResponse(ExperimentStateResponse):
    pass


class SubmitResponseRequest(BaseModel):
    color_id: str = Field(min_length=1, max_length=32)
    emotion: Emotion
    trial_number: int = Field(ge=1, le=15)
    experiment_version: str = Field(min_length=1, max_length=32)


class SubmitResponseResult(ExperimentStateResponse):
    accepted: bool = True
