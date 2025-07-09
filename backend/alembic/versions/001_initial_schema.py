"""Initial schema with invoice, party, and line item tables

Revision ID: 001
Revises: 
Create Date: 2025-01-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create invoices table
    op.create_table('invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('draft', 'sent', 'paid', 'overdue', name='invoicestatus'), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('payment_terms', sa.String(length=100), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('subtotal', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('tax_rate', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('tax_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('discount_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('shipping_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('amount_paid', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('balance_due', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('terms', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)

    # Create invoice_parties table
    op.create_table('invoice_parties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('party_type', sa.Enum('from', 'to', 'ship_to', name='partytype'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_parties_id'), 'invoice_parties', ['id'], unique=False)

    # Create line_items table
    op.create_table('line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_line_items_id'), 'line_items', ['id'], unique=False)

    # Keep the existing invoice_defaults table as is
    op.create_table('invoice_defaults',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('company_email', sa.String(), nullable=True),
        sa.Column('company_phone', sa.String(), nullable=True),
        sa.Column('company_address', sa.Text(), nullable=True),
        sa.Column('company_logo', sa.String(), nullable=True),
        sa.Column('default_payment_terms', sa.Integer(), nullable=True),
        sa.Column('default_tax_rate', sa.Float(), nullable=True),
        sa.Column('default_currency', sa.String(), nullable=True),
        sa.Column('invoice_prefix', sa.String(), nullable=True),
        sa.Column('next_invoice_number', sa.Integer(), nullable=True),
        sa.Column('payment_instructions', sa.Text(), nullable=True),
        sa.Column('footer_text', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_defaults_id'), 'invoice_defaults', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_invoice_defaults_id'), table_name='invoice_defaults')
    op.drop_table('invoice_defaults')
    op.drop_index(op.f('ix_line_items_id'), table_name='line_items')
    op.drop_table('line_items')
    op.drop_index(op.f('ix_invoice_parties_id'), table_name='invoice_parties')
    op.drop_table('invoice_parties')
    op.drop_index(op.f('ix_invoices_invoice_number'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_id'), table_name='invoices')
    op.drop_table('invoices')
    op.execute('DROP TYPE IF EXISTS invoicestatus')
    op.execute('DROP TYPE IF EXISTS partytype')