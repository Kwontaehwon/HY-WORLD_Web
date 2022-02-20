"""empty message

Revision ID: 6ecbbf4be4b2
Revises: 36b378cb93e1
Create Date: 2022-02-17 02:45:19.281934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ecbbf4be4b2'
down_revision = '36b378cb93e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('category_name', sa.String(length=20), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('has_answer', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('category_name', name=op.f('pk_category'))
    )
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=20), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_question_category_category'), 'category', ['category'], ['category_name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_question_category_category'), type_='foreignkey')
        batch_op.drop_column('category')

    op.drop_table('category')
    # ### end Alembic commands ###