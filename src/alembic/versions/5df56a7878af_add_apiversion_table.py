"""add apiversion table

Revision ID: 5df56a7878af
Revises: 858ab3cfa441
Create Date: 2024-10-18 16:16:24.828579+00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5df56a7878af"
down_revision = "858ab3cfa441"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "apiversion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_apiversion_version"), "apiversion", ["version"], unique=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_apiversion_version"), table_name="apiversion")
    op.drop_table("apiversion")
    # ### end Alembic commands ###
