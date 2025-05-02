"""insert initial data

Revision ID: c59e1eca1b0b
Revises: d42710133ba8
Create Date: 2025-04-09 16:22:34.070438

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.model._enum import UserLevelEnum, RoleEnum


# revision identifiers, used by Alembic.
revision: str = "c59e1eca1b0b"
down_revision: Union[str, None] = "9bc0e72ea289"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def insert_role() -> None:
    role_table = sa.table(
        "role",
        sa.column("id", sa.Integer),
        sa.column("role", sa.Enum(RoleEnum)),
    )
    op.bulk_insert(
        role_table,
        [
            {"id": 1, "role": RoleEnum.USER},
            {"id": 2, "role": RoleEnum.ADMIN},
        ],
    )


def insert_user_level() -> None:
    user_level_table = sa.table(
        "user_level",
        sa.column("id", sa.Integer),
        sa.column("user_level", sa.Enum(UserLevelEnum)),
        sa.column("required_amount", sa.Numeric(16, 4)),
        sa.column("discount_rate", sa.Numeric(16, 4)),
    )
    op.bulk_insert(
        user_level_table,
        [
            {
                "id": 1,
                "user_level": UserLevelEnum.DEFAULT,
                "required_amount": 0,
                "discount_rate": 0,
            },
            {
                "id": 2,
                "user_level": UserLevelEnum.SILVER,
                "required_amount": 1000000,
                "discount_rate": 0.1,
            },
            {
                "id": 3,
                "user_level": UserLevelEnum.GOLD,
                "required_amount": 5000000,
                "discount_rate": 0.15,
            },
            {
                "id": 4,
                "user_level": UserLevelEnum.VIP,
                "required_amount": 10000000,
                "discount_rate": 0.2,
            },
        ],
    )


def insert_cargo_transportation() -> None:
    cargo_transportation_table = sa.table(
        "cargo_transportation",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        cargo_transportation_table,
        [
            {"id": 1, "name": "LTL", "description": "LTL"},
            {"id": 2, "name": "Truckload(FTL)", "description": "Truckload(FTL)"},
            {"id": 3, "name": "Flatbed", "description": "Flatbed"},
        ],
    )


def insert_cargo_accessorial() -> None:
    cargo_accessorial_table = sa.table(
        "cargo_accessorial",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(
        cargo_accessorial_table,
        [
            {"id": 1, "name": "Inside Delivery", "description": "-"},
            {"id": 2, "name": "Two Person", "description": "-"},
            {"id": 3, "name": "Lift Gate", "description": "-"},
        ],
    )


def insert_cargo_package() -> None:
    cargo_package_table = sa.table(
        "cargo_package",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column(
            "width",
            sa.Numeric(16, 4),
        ),
        sa.column("length", sa.Numeric(16, 4)),
        sa.column("height", sa.Numeric(16, 4)),
    )
    op.bulk_insert(
        cargo_package_table,
        [
            {
                "id": 1,
                "name": 'Pallet(48" * 40")',
                "width": 48,
                "length": 40,
                "height": None,
            },
            {
                "id": 2,
                "name": 'Pallet(48" * 48")',
                "width": 48,
                "length": 48,
                "height": None,
            },
            {
                "id": 3,
                "name": 'Pallet(60" * 48")',
                "width": 60,
                "length": 48,
                "height": None,
            },
            {"id": 4, "name": "Box", "width": None, "length": None, "height": None},
            {"id": 5, "name": "PCS", "width": None, "length": None, "height": None},
            {"id": 6, "name": "Skid", "width": None, "length": None, "height": None},
            {
                "id": 7,
                "name": "Wooden Crate",
                "width": None,
                "length": None,
                "height": None,
            },
        ],
    )


def upgrade() -> None:
    """Upgrade schema."""
    insert_role()
    insert_user_level()
    insert_cargo_transportation()
    insert_cargo_accessorial()
    insert_cargo_package()


def downgrade() -> None:
    """Downgrade schema."""
    pass
