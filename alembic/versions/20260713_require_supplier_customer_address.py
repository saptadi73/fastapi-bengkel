"""Require address on supplier and customer

Revision ID: 20260713_supplier_address
Revises:
Create Date: 2026-07-13 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260713_supplier_address"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE supplier
            SET alamat = 'Alamat belum diisi'
            WHERE alamat IS NULL OR btrim(alamat) = ''
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE customer
            SET alamat = 'Alamat belum diisi'
            WHERE alamat IS NULL OR btrim(alamat) = ''
            """
        )
    )

    op.alter_column("supplier", "alamat", existing_type=sa.String(), nullable=False)
    op.alter_column("customer", "alamat", existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    op.alter_column("customer", "alamat", existing_type=sa.String(), nullable=True)
    op.alter_column("supplier", "alamat", existing_type=sa.String(), nullable=True)
