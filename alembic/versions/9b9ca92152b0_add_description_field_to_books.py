"""Add description field to books

Revision ID: 9b9ca92152b0
Revises: 684625057560
Create Date: 2025-06-15 16:37:38.310042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b9ca92152b0'
down_revision: Union[str, None] = '684625057560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('description', sa.String(), nullable=True))
    op.execute("UPDATE books SET description = 'No description' WHERE description IS NULL")
    op.alter_column('books', 'description', nullable=False)
    op.create_unique_constraint(None, 'librarians', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'librarians', type_='unique')
    op.drop_column('books', 'description')
    # ### end Alembic commands ###
