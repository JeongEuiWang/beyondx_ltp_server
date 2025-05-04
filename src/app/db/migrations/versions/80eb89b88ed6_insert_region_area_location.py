"""insert region / area / location

Revision ID: 80eb89b88ed6
Revises: c59e1eca1b0b
Create Date: 2025-04-09 16:52:16.421888

"""

from datetime import datetime, UTC
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pathlib import Path


# revision identifiers, used by Alembic.
revision: str = "80eb89b88ed6"
down_revision: Union[str, None] = "c59e1eca1b0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

import csv

PROJECT_ROOT = Path(__file__).parents[4]

FILE_PATH = (
    PROJECT_ROOT
    / "app"
    / "db"
    / "migrations"
    / "resource"
    / "Texas"
    / "Texas_location.csv"
)

AREA_MAP = {
    "a": 1,
    "b": 2,
    "c": 3,
}


# Insert Region:: Texas
def insert_region() -> None:
    rate_region_table = sa.table(
        "rate_region",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("created_at", sa.TIMESTAMP),
        sa.column("updated_at", sa.TIMESTAMP),
    )

    op.bulk_insert(
        rate_region_table,
        [
            {
                "id": 1,
                "name": "Texas",
                "description": "Dallas-Fort Worth Region",
                "created_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
        ],
    )


def insert_area() -> None:
    rate_area_table = sa.table(
        "rate_area",
        sa.column("id", sa.Integer),
        sa.column("region_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("min_order_amount", sa.Numeric(16, 4)),
        sa.column("max_load", sa.Numeric(16, 4)),
        sa.column("created_at", sa.TIMESTAMP),
        sa.column("updated_at", sa.TIMESTAMP),
    )

    op.bulk_insert(
        rate_area_table,
        [
            {
                "id": 1,
                "region_id": 1,
                "name": "A",
                "min_order_amount": 25,
                "max_load": 225,
                "created_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "id": 2,
                "region_id": 1,
                "name": "B",
                "min_order_amount": 30,
                "max_load": 250,
                "created_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "id": 3,
                "region_id": 1,
                "name": "C",
                "min_order_amount": 35,
                "max_load": 275,
                "created_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
        ],
    )
    pass


def extract_location(file_path: Path) -> list[dict]:
    with open(file_path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        attrs = []
        result = []
        for row in reader:
            if len(attrs) < 1:
                attrs = row
                continue
            temp_row_dict = dict()
            for key, value in zip(attrs, row):
                if key != "area":
                    temp_row_dict[key] = value
                else:
                    if value in AREA_MAP:
                        temp_row_dict["area_id"] = AREA_MAP[value]
                    else:
                        temp_row_dict["area_id"] = None
            temp_row_dict["region_id"] = 1 # Texas Region Id
            temp_row_dict["created_at"] = datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            temp_row_dict["updated_at"] = datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if temp_row_dict.get("area_id") is not None:
                result.append(temp_row_dict)
    return result


def insert_location(location_list: list[dict]) -> None:
    rate_location_table = sa.table(
        "rate_location",
        sa.column("id", sa.Integer),
        sa.column("region_id", sa.Integer),
        sa.column("area_id", sa.Integer),
        sa.column("state", sa.String),
        sa.column("county", sa.String),
        sa.column("city", sa.String),
        sa.column("zip_code", sa.String),
        sa.column("created_at", sa.TIMESTAMP),
        sa.column("updated_at", sa.TIMESTAMP),
    )

    op.bulk_insert(rate_location_table, location_list)


def upgrade() -> None:
    """Upgrade schema."""
    insert_region()
    insert_area()
    location_list = extract_location(FILE_PATH)
    insert_location(location_list)


def downgrade() -> None:
    """Downgrade schema."""
    pass
