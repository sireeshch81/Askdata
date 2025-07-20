"""create ETL tracking table

Revision ID: 0001_create_etl_tracking
Create Date: 2025-07-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '0001_create_etl_tracking'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create ETL tracking table
    op.create_table(
        'etl_process_tracking',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_name', sa.String(length=100), nullable=False),
        sa.Column('source_table', sa.String(length=100), nullable=False),
        sa.Column('last_processed_id', sa.Integer(), nullable=False, default=0),
        sa.Column('last_run_time', sa.DateTime(), nullable=False),
        sa.Column('records_processed', sa.Integer(), default=0),
        sa.Column('status', sa.String(length=50), default='success'),
        sa.Column('error_message', sa.Text()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_name', 'source_table', name='job_source_idx')
    )


def downgrade():
    op.drop_table('etl_process_tracking')
