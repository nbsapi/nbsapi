"""description now part of unit

Revision ID: 53401ffc047b
Revises: bc341db95b36
Create Date: 2024-11-25 12:49:05.776745+00:00

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "53401ffc047b"
down_revision = "bc341db95b36"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_impact_description", table_name="impact")
    op.drop_column("impact", "description")
    op.add_column("impact_unit", sa.Column("description", sa.String(), nullable=True))
    op.create_index(
        op.f("ix_impact_unit_description"), "impact_unit", ["description"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_impact_unit_description"), table_name="impact_unit")
    op.drop_column("impact_unit", "description")
    op.add_column(
        "impact",
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.create_index("ix_impact_description", "impact", ["description"], unique=False)
    # ### end Alembic commands ###
