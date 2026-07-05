"""Add user and donation user_id

Revision ID: e412574bcec3
Revises: 001_initial
Create Date: 2024-xx-xx xx:xx:xx.xxxxxx

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e412574bcec3'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаём таблицу user
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.create_index('ix_user_id', 'user', ['id'], unique=False)
    
    # Используем batch режим для добавления колонки и внешнего ключа в SQLite
    with op.batch_alter_table('donation') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_donation_user_id', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    # Используем batch режим для удаления внешнего ключа и колонки
    with op.batch_alter_table('donation') as batch_op:
        batch_op.drop_constraint('fk_donation_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
    
    op.drop_index('ix_user_id', table_name='user')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')