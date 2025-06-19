"""Add Deltares compatibility features

Revision ID: add_deltares_compatibility
Revises: ea7ce84afd65
Create Date: 2025-06-19 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_deltares_compatibility"
down_revision: str | None = "ea7ce84afd65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create measure_types table
    op.create_table(
        "measure_types",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_color", sa.String(), nullable=True),
        sa.Column("default_inflow", sa.Float(), nullable=True),
        sa.Column("default_depth", sa.Float(), nullable=True),
        sa.Column("default_width", sa.Float(), nullable=True),
        sa.Column("default_radius", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_measure_types_id"), "measure_types", ["id"], unique=False)

    # Add new columns to naturebasedsolution table
    op.add_column(
        "naturebasedsolution", sa.Column("measure_id", sa.String(), nullable=True)
    )
    op.add_column("naturebasedsolution", sa.Column("area", sa.Float(), nullable=True))
    op.add_column("naturebasedsolution", sa.Column("length", sa.Float(), nullable=True))

    # Create foreign key constraint
    op.create_foreign_key(
        "fk_naturebasedsolution_measure_id",
        "naturebasedsolution",
        "measure_types",
        ["measure_id"],
        ["id"],
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint(
        "fk_naturebasedsolution_measure_id", "naturebasedsolution", type_="foreignkey"
    )

    # Drop columns from naturebasedsolution table
    op.drop_column("naturebasedsolution", "length")
    op.drop_column("naturebasedsolution", "area")
    op.drop_column("naturebasedsolution", "measure_id")

    # Drop measure_types table
    op.drop_index(op.f("ix_measure_types_id"), table_name="measure_types")
    op.drop_table("measure_types")
