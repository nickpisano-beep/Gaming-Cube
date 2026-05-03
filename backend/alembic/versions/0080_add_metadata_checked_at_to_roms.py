"""Add metadata_checked_at to roms table

Revision ID: 0080_add_metadata_checked_at_to_roms
Revises: 0079_add_rom_files_rom_id_index
Create Date: 2026-05-03 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0080_add_metadata_checked_at_to_roms"
down_revision = "0079_add_rom_files_rom_id_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("roms", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "metadata_checked_at",
                sa.TIMESTAMP(timezone=True),
                nullable=True,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("roms", schema=None) as batch_op:
        batch_op.drop_column("metadata_checked_at")
