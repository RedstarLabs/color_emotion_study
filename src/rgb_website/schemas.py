from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from rgb_website.experiment import PALETTE_VERSION, allowed_emotions_for_version


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    DIVERSE = "diverse"
    NOT_SPECIFIED = "not_specified"


class StartExperimentRequest(BaseModel):
    gender: Gender = Gender.NOT_SPECIFIED
    age_confirmed: bool
    information_acknowledged: bool
    participation_consent: bool

    @model_validator(mode="after")
    def validate_required_confirmations(self) -> StartExperimentRequest:
        if not self.age_confirmed:
            raise ValueError("Age confirmation is required.")
        if not self.information_acknowledged:
            raise ValueError("Study information must be acknowledged.")
        if not self.participation_consent:
            raise ValueError("Participation consent is required.")
        return self


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
    emotion: str = Field(min_length=1, max_length=64)
    trial_number: int = Field(ge=1, le=15)
    experiment_version: str = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def validate_emotion_for_version(self) -> SubmitResponseRequest:
        if self.emotion not in allowed_emotions_for_version(self.experiment_version):
            raise ValueError("Emotion is not allowed for this experiment version.")
        return self


class SubmitResponseResult(ExperimentStateResponse):
    accepted: bool = True
