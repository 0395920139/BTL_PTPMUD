"""init

Revision ID: 8b9dfaa686f6
Revises: 4dba2ecc5994
Create Date: 2020-12-01 14:17:52.565924

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b9dfaa686f6'
down_revision = '4dba2ecc5994'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('schedule', sa.Column('Subjects_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'schedule', 'subjects', ['Subjects_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'schedule', type_='foreignkey')
    op.drop_column('schedule', 'Subjects_id')
    # ### end Alembic commands ###