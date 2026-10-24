"""Add optional self-reported gender to survey sessions.

Revision ID: 0005_session_gender
Revises: 0004_session_abandonment
Create Date: 2026-10-24
"""

import sqlalchemy as sa

from alembic import op

revision = "0005_session_gender"
down_revision = "0004_session_abandonment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("survey_sessions") as batch_op:
        batch_op.add_column(
            sa.Column(
                "gender",
                sa.Enum(
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
        )
        batch_op.create_check_constraint(
            "ck_sessions_gender",
            "gender IS NULL OR gender IN "
            "('male', 'female', 'diverse', 'not_specified')",
        )


def downgrade() -> None:
    with op.batch_alter_table("survey_sessions") as batch_op:
        batch_op.drop_constraint("ck_sessions_gender", type_="check")
        batch_op.drop_column("gender")
