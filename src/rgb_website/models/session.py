from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rgb_website.database.base import Base
from rgb_website.experiment import PALETTE_VERSION

if TYPE_CHECKING:
    from rgb_website.models.response import Response
    from rgb_website.models.session_color import SessionColor


class SurveySession(Base):
    __tablename__ = "survey_sessions"
    __table_args__ = (
        CheckConstraint("trial_count IN (10, 15)", name="ck_sessions_trial_count"),
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'abandoned')",
            name="ck_sessions_status",
        ),
        CheckConstraint(
            "gender IS NULL OR gender IN "
            "('male', 'female', 'diverse', 'not_specified')",
            name="ck_sessions_gender",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    experiment_version: Mapped[str] = mapped_column(
        String(32),
        default=PALETTE_VERSION,
        nullable=False,
    )
    palette_version: Mapped[str] = mapped_column(
        String(32),
        default=PALETTE_VERSION,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "in_progress",
            "completed",
            "abandoned",
            name="survey_status",
            native_enum=False,
            length=11,
        ),
        default="in_progress",
        nullable=False,
    )
    trial_count: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )
    gender: Mapped[str | None] = mapped_column(
        Enum(
            "male",
            "female",
            "diverse",
            "not_specified",
            name="gender_value",
            native_enum=False,
            length=13,
        ),
        nullable=True,
    )

    responses: Mapped[list[Response]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    colors: Mapped[list[SessionColor]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionColor.position",
    )
