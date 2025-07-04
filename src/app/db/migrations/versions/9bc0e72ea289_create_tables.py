"""create tables

Revision ID: 9bc0e72ea289
Revises:
Create Date: 2025-04-10 23:15:59.529231

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9bc0e72ea289"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cargo_accessorial",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cargo_package",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("length", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cargo_transportation",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_level",
        sa.Column(
            "user_level",
            sa.Enum("DEFAULT", "SILVER", "GOLD", "VIP", name="userlevelenum"),
            nullable=False,
        ),
        sa.Column("required_amount", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("discount_rate", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rate_region",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "role",
        sa.Column("role", sa.Enum("USER", "ADMIN", name="roleenum"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rate_area",
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("min_load", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("max_load", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("max_load_weight", sa.Integer()),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["rate_region.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("region_id", "name", name="uq_region_area_name"),
    )
    op.create_table(
        "rate_area_cost",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("min_weight", sa.Integer()),
        sa.Column("max_weight", sa.Integer()),
        sa.Column("price_per_weight", sa.Numeric(precision=16, scale=4)),
        sa.ForeignKeyConstraint(
            ["area_id"],
            ["rate_area.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=255), nullable=False),
        sa.Column("user_level_id", sa.Integer(), nullable=False),
        sa.Column(
            "total_payment_amount", sa.Numeric(precision=16, scale=4), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_level_id"],
            ["user_level.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "rate_location",
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=255), nullable=False),
        sa.Column("county", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("zip_code", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["area_id"],
            ["rate_area.id"],
        ),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["rate_region.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("area_id", "zip_code", name="uq_rate_location"),
    )
    op.create_index(
        "ix_rate_location_region_id",
        "rate_location",
        ["region_id"],
    )
    op.create_index(
        "ix_rate_location_region_area",
        "rate_location",
        ["region_id", "area_id"],
    )
    op.create_table(
        "user_address",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=255), nullable=False),
        sa.Column("county", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("zip_code", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column(
            "location_type",
            sa.Enum("COMMERCIAL", "RESIDENTIAL", "AIRPORT", name="locationtypeenum"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "quote",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("cargo_transportation_id", sa.Integer(), nullable=False),
        sa.Column("is_priority", sa.Boolean(), nullable=False),
        sa.Column("total_weight", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("base_price", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("extra_price", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column(
            "order_status",
            sa.Enum(
                "ESTIMATE",
                "SUBMIT",
                "ACCEPT",
                "REJECT",
                "COMPLETED",
                name="orderstatusenum",
            ),
            nullable=False,
        ),
        sa.Column("order_primary", sa.String(length=255), nullable=True),
        sa.Column("order_additional_request", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cargo_transportation_id"],
            ["cargo_transportation.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "quote_cargo",
        sa.Column("quote_id", sa.String(length=32), nullable=False),
        
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("length", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("package_description", sa.Text(), nullable=True),
        sa.Column("cargo_stackable", sa.Boolean(), nullable=False),
        sa.Column("cargo_temperature", sa.Text(), nullable=True),
        sa.Column("is_hazardous", sa.Boolean(), nullable=False),
        sa.Column("hazardous_detail", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["quote.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "quote_location",
        sa.Column("quote_id", sa.String(length=32), nullable=False),
        sa.Column("state", sa.String(length=255), nullable=False),
        sa.Column("county", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("zip_code", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column(
            "location_type",
            sa.Enum("COMMERCIAL", "RESIDENTIAL", "AIRPORT", name="locationtypeenum"),
            nullable=False,
        ),
        sa.Column(
            "shipment_type",
            sa.Enum("PICKUP", "DELIVERY", name="shipmenttypeenum"),
            nullable=False,
        ),
        sa.Column("request_datetime", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["quote.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "quote_id", "shipment_type", name="uq_quote_location_shipment_type"
        ),
    )
    op.create_table(
        "quote_location_accessorial",
        sa.Column("quote_location_id", sa.Integer(), nullable=False),
        sa.Column("cargo_accessorial_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cargo_accessorial_id"],
            ["cargo_accessorial.id"],
        ),
        sa.ForeignKeyConstraint(
            ["quote_location_id"],
            ["quote_location.id"],
        ),
        sa.PrimaryKeyConstraint("quote_location_id", "cargo_accessorial_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("quote_location_accessorial")
    op.drop_table("quote_location")
    op.drop_table("quote_cargo")
    op.drop_table("quote")
    op.drop_table("user_address")
    op.drop_table("rate_location")
    op.drop_table("user")
    op.drop_table("user_level")
    op.drop_table("role")
    op.drop_table("rate_area_cost")
    op.drop_table("rate_area")
    op.drop_table("rate_region")
    op.drop_table("cargo_transportation")
    op.drop_table("cargo_package")
    op.drop_table("cargo_accessorial")
