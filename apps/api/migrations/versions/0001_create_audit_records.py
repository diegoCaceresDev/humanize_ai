"""Create the initial audit record storage table.

Revision ID: 0001_create_audit_records
Revises:
Create Date: 2026-09-12
"""

from alembic import op


revision = "0001_create_audit_records"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_records (
            id UUID PRIMARY KEY,
            url VARCHAR(2000) NOT NULL,
            title VARCHAR(1000) NOT NULL DEFAULT '',
            score INTEGER NOT NULL,
            result JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_records")
