"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаём таблицу charityproject
    op.create_table(
        'charityproject',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('full_amount', sa.Integer(), nullable=False),
        sa.Column('invested_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fully_invested', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.Column('close_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_charityproject_id', 'charityproject', ['id'])
    op.create_index('ix_charityproject_name', 'charityproject', ['name'], unique=True)
    
    # Создаём таблицу donation
    op.create_table(
        'donation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('full_amount', sa.Integer(), nullable=False),
        sa.Column('invested_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fully_invested', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.Column('close_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_donation_id', 'donation', ['id'])


def downgrade() -> None:
    op.drop_index('ix_donation_id', table_name='donation')
    op.drop_table('donation')
    op.drop_index('ix_charityproject_name', table_name='charityproject')
    op.drop_index('ix_charityproject_id', table_name='charityproject')
    op.drop_table('charityproject')