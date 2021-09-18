"""First migration.

Revision ID: 2e066540f754
Revises: 
Create Date: 2021-09-18 15:28:52.317474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e066540f754'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('themes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=False),
    sa.Column('theme_ref', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['theme_ref'], ['themes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.Column('question_ref', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['question_ref'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('themes')
    op.drop_table('admins')
    # ### end Alembic commands ###