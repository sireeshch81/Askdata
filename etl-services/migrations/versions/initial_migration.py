"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-07-19 18:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create etl_job_status table
    op.create_table(
        'etl_job_status',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True, default=0),
        sa.Column('tables_processed', mysql.JSON(), nullable=True),
        sa.Column('errors', mysql.JSON(), nullable=True),
        sa.Column('last_processed_ids', mysql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKey('id')
    )
    
    # Create etl_job_config table
    op.create_table(
        'etl_job_config',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('schedule', sa.String(length=100), nullable=True),
        sa.Column('last_run_id', sa.Integer(), nullable=True),
        sa.Column('last_run_time', sa.DateTime(), nullable=True),
        sa.Column('config', mysql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKey('id'),
        sa.UniqueConstraint('job_name')
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('etl_job_config')
    op.drop_table('etl_job_status')