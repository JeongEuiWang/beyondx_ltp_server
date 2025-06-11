"""create_admin_user

Revision ID: 7cb46db48fbc
Revises: 80eb89b88ed6
Create Date: 2025-06-10 00:49:02.881515

"""
from typing import Sequence, Union
from passlib.context import CryptContext

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '7cb46db48fbc'
down_revision: Union[str, None] = '80eb89b88ed6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_admin_user() -> None:
    connection = op.get_bind()
    
    result = connection.execute(
        text("SELECT COUNT(*) FROM `user` WHERE email = 'bx_admin@gmail.com'")
    ).scalar()
    
    if result > 0:
        print("Admin user already exists, skipping...")
        return
    
    admin_role_result = connection.execute(
        text("SELECT id FROM role WHERE role = 'ADMIN'")
    ).scalar()
    
    if not admin_role_result:
        raise ValueError("ADMIN role not found in database")
    
    user_level_result = connection.execute(
        text("SELECT id FROM user_level WHERE user_level = 'DEFAULT'")
    ).scalar()
    
    if not user_level_result:
        raise ValueError("DEFAULT user level not found in database")
    
    hashed_password = get_password_hash("bxadmin123!")
    
    user_table = sa.table(
        "user",
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("role_id", sa.Integer),
        sa.column("first_name", sa.String),
        sa.column("last_name", sa.String),
        sa.column("phone", sa.String),
        sa.column("user_level_id", sa.Integer),
        sa.column("total_payment_amount", sa.Numeric),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    
    from datetime import datetime
    now = datetime.utcnow()
    
    op.bulk_insert(
        user_table,
        [
            {
                "email": "bx_admin@gmail.com",
                "password": hashed_password,
                "role_id": admin_role_result,
                "first_name": "Admin",
                "last_name": "User",
                "phone": "000-0000-0000",
                "user_level_id": user_level_result,
                "total_payment_amount": 0,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )
    
    print("Admin user created successfully!")


def upgrade() -> None:
    """Upgrade schema."""
    create_admin_user()


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    connection.execute(
        text("DELETE FROM `user` WHERE email = 'bx_admin@gmail.com'")
    )
