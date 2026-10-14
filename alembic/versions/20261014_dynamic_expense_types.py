"""Allow dynamic expense types.

Revision ID: 20261014_dynamic_expense_types
Revises: 20260713_product_consignment
Create Date: 2026-10-14 09:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20261014_dynamic_expense_types"
down_revision = "20260713_product_consignment"
branch_labels = None
depends_on = None


LEGACY_EXPENSE_TYPES = (
    "listrik",
    "gaji",
    "air",
    "internet",
    "transportasi",
    "komunikasi",
    "konsumsi",
    "entertaint",
    "umum",
    "lain_lain",
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE expenses
            ALTER COLUMN expense_type TYPE VARCHAR(100)
            USING CASE
                WHEN expense_type::text = 'lain_lain' THEN 'lain-lain'
                ELSE expense_type::text
            END
            """
        )
        op.execute("DROP TYPE IF EXISTS expensetype")
        return

    with op.batch_alter_table("expenses") as batch_op:
        batch_op.alter_column(
            "expense_type",
            existing_type=sa.Enum(*LEGACY_EXPENSE_TYPES, name="expensetype"),
            type_=sa.String(length=100),
            existing_nullable=False,
        )
    op.execute(
        sa.text(
            "UPDATE expenses SET expense_type = 'lain-lain' "
            "WHERE expense_type = 'lain_lain'"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    allowed_values = ", ".join(f"'{value}'" for value in LEGACY_EXPENSE_TYPES)
    op.execute(
        sa.text(
            f"""
            UPDATE expenses
            SET expense_type = CASE
                WHEN expense_type = 'lain-lain' THEN 'lain_lain'
                WHEN expense_type IN ({allowed_values}) THEN expense_type
                ELSE 'umum'
            END
            """
        )
    )

    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE TYPE expensetype AS ENUM "
            f"({allowed_values})"
        )
        op.execute(
            """
            ALTER TABLE expenses
            ALTER COLUMN expense_type TYPE expensetype
            USING expense_type::expensetype
            """
        )
        return

    with op.batch_alter_table("expenses") as batch_op:
        batch_op.alter_column(
            "expense_type",
            existing_type=sa.String(length=100),
            type_=sa.Enum(*LEGACY_EXPENSE_TYPES, name="expensetype"),
            existing_nullable=False,
        )
