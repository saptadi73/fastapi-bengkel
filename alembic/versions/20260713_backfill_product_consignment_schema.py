"""Backfill product consignment-related schema.

Revision ID: 20260713_backfill_product_consignment_schema
Revises: 20260713_require_supplier_customer_address
Create Date: 2026-07-13 00:30:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260713_backfill_product_consignment_schema"
down_revision = "20260713_require_supplier_customer_address"
branch_labels = None
depends_on = None


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    return any(
        column["name"] == column_name
        for column in inspector.get_columns(table_name)
    )


def _foreign_key_exists(inspector, table_name: str, constrained_columns: list[str]) -> bool:
    expected = list(constrained_columns)
    for foreign_key in inspector.get_foreign_keys(table_name):
        if foreign_key.get("constrained_columns") == expected:
            return True
    return False


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _column_exists(inspector, "product", "supplier_id"):
        op.add_column("product", sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=True))

    inspector = inspect(bind)
    if not _foreign_key_exists(inspector, "product", ["supplier_id"]):
        op.create_foreign_key(
            "fk_product_supplier_id_supplier",
            "product",
            "supplier",
            ["supplier_id"],
            ["id"],
        )

    inspector = inspect(bind)
    if not _column_exists(inspector, "product", "is_consignment"):
        op.add_column(
            "product",
            sa.Column(
                "is_consignment",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

    inspector = inspect(bind)
    if not _column_exists(inspector, "product", "consignment_commission"):
        op.add_column("product", sa.Column("consignment_commission", sa.Numeric(10, 2), nullable=True))

    inspector = inspect(bind)
    if not _column_exists(inspector, "product", "is_internal_consumption"):
        op.add_column(
            "product",
            sa.Column(
                "is_internal_consumption",
                sa.Boolean(),
                nullable=True,
                server_default=sa.text("false"),
            ),
        )

    # Keep defaults for backward-compatible inserts on older code paths.
    inspector = inspect(bind)
    if not _index_exists(inspector, "product", "idx_product_supplier_id"):
        op.create_index("idx_product_supplier_id", "product", ["supplier_id"], unique=False)

    inspector = inspect(bind)
    if not _index_exists(inspector, "product", "idx_product_is_consignment"):
        op.create_index("idx_product_is_consignment", "product", ["is_consignment"], unique=False)

    inspector = inspect(bind)
    if not inspector.has_table("consignment_receipt"):
        op.create_table(
            "consignment_receipt",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("receipt_number", sa.String(), nullable=False),
            sa.Column("receipt_date", sa.Date(), nullable=False),
            sa.Column("quantity_received", sa.Numeric(12, 2), nullable=False),
            sa.Column("unit_price", sa.Numeric(12, 2), nullable=True),
            sa.Column("total_value", sa.Numeric(14, 2), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("received_by", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
            sa.ForeignKeyConstraint(["supplier_id"], ["supplier.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("receipt_number"),
        )
        op.create_index(op.f("ix_consignment_receipt_id"), "consignment_receipt", ["id"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("consignment_receipt"):
        index_names = {index["name"] for index in inspector.get_indexes("consignment_receipt")}
        if op.f("ix_consignment_receipt_id") in index_names:
            op.drop_index(op.f("ix_consignment_receipt_id"), table_name="consignment_receipt")
        op.drop_table("consignment_receipt")

    inspector = inspect(bind)
    if _index_exists(inspector, "product", "idx_product_is_consignment"):
        op.drop_index("idx_product_is_consignment", table_name="product")

    inspector = inspect(bind)
    if _index_exists(inspector, "product", "idx_product_supplier_id"):
        op.drop_index("idx_product_supplier_id", table_name="product")

    inspector = inspect(bind)
    if _column_exists(inspector, "product", "is_internal_consumption"):
        op.drop_column("product", "is_internal_consumption")

    inspector = inspect(bind)
    if _column_exists(inspector, "product", "consignment_commission"):
        op.drop_column("product", "consignment_commission")

    inspector = inspect(bind)
    if _column_exists(inspector, "product", "is_consignment"):
        op.drop_column("product", "is_consignment")

    inspector = inspect(bind)
    if _foreign_key_exists(inspector, "product", ["supplier_id"]):
        op.drop_constraint("fk_product_supplier_id_supplier", "product", type_="foreignkey")

    inspector = inspect(bind)
    if _column_exists(inspector, "product", "supplier_id"):
        op.drop_column("product", "supplier_id")
