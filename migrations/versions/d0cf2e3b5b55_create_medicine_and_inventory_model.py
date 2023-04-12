"""create medicine and inventory model

Revision ID: d0cf2e3b5b55
Revises: 
Create Date: 2023-04-12 14:16:42.380731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0cf2e3b5b55'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicine_detail',
    sa.Column('medicine_id', sa.Integer(), nullable=False),
    sa.Column('medicine_name_bg', sa.String(length=255), nullable=True),
    sa.Column('group', sa.String(length=255), nullable=True),
    sa.Column('manufacturer', sa.String(length=255), nullable=True),
    sa.Column('sales_measure', sa.String(length=255), nullable=True),
    sa.Column('medicine_name', sa.String(length=255), nullable=True),
    sa.Column('atc_code', sa.String(length=50), nullable=True),
    sa.Column('opiate', sa.String(length=255), nullable=True),
    sa.Column('nhif_code', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('medicine_id')
    )
    op.create_table('inventory',
    sa.Column('inventory_id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('expiry_date', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine_detail.medicine_id'], ),
    sa.PrimaryKeyConstraint('inventory_id')
    )
    op.create_table('medicine_barcode',
    sa.Column('barcode_id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=True),
    sa.Column('barcode_1', sa.String(length=255), nullable=True),
    sa.Column('barcode_2', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine_detail.medicine_id'], ),
    sa.PrimaryKeyConstraint('barcode_id')
    )
    op.create_table('purchase',
    sa.Column('purchase_id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('batch_number', sa.String(length=255), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('reported', sa.Boolean(), nullable=True),
    sa.Column('sespa_reporting', sa.Boolean(), nullable=True),
    sa.Column('supplier_code', sa.String(length=255), nullable=True),
    sa.Column('purchase_order', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine_detail.medicine_id'], ),
    sa.PrimaryKeyConstraint('purchase_id')
    )
    op.create_table('sale',
    sa.Column('sale_id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('batch_number', sa.String(length=255), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('reported', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine_detail.medicine_id'], ),
    sa.PrimaryKeyConstraint('sale_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sale')
    op.drop_table('purchase')
    op.drop_table('medicine_barcode')
    op.drop_table('inventory')
    op.drop_table('medicine_detail')
    # ### end Alembic commands ###