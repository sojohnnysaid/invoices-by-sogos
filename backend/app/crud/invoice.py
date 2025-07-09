from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class CRUDInvoice(CRUDBase[Invoice, InvoiceCreate, InvoiceUpdate]):
    async def get_with_details(self, db: AsyncSession, id: str) -> Optional[Invoice]:
        """Get invoice with all related data (parties and line items)"""
        result = await db.execute(
            select(Invoice)
            .filter(Invoice.id == id)
            .options(
                selectinload(Invoice.parties),
                selectinload(Invoice.line_items)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_invoice_number(self, db: AsyncSession, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number"""
        result = await db.execute(
            select(Invoice).filter(Invoice.invoice_number == invoice_number)
        )
        return result.scalar_one_or_none()

    async def get_by_status(
        self, db: AsyncSession, status: InvoiceStatus, *, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """Get all invoices with a specific status"""
        result = await db.execute(
            select(Invoice)
            .filter(Invoice.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_overdue(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get all overdue invoices"""
        from datetime import datetime
        result = await db.execute(
            select(Invoice)
            .filter(
                and_(
                    Invoice.due_date < datetime.utcnow(),
                    Invoice.status.in_([InvoiceStatus.PENDING, InvoiceStatus.SENT])
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_with_details(
        self, db: AsyncSession, *, obj_in: InvoiceCreate
    ) -> Invoice:
        """Create invoice with parties and line items"""
        # Extract nested data
        parties_data = obj_in.parties if hasattr(obj_in, 'parties') else []
        line_items_data = obj_in.line_items if hasattr(obj_in, 'line_items') else []
        
        # Create invoice without nested data
        invoice_data = obj_in.model_dump(exclude={'parties', 'line_items'})
        db_invoice = Invoice(**invoice_data)
        db.add(db_invoice)
        await db.flush()  # Flush to get the ID without committing
        
        # Create related parties
        from app.models.invoice_party import InvoiceParty
        for party_data in parties_data:
            party_dict = party_data.model_dump() if hasattr(party_data, 'model_dump') else party_data
            db_party = InvoiceParty(invoice_id=db_invoice.id, **party_dict)
            db.add(db_party)
        
        # Create related line items
        from app.models.line_item import LineItem
        for idx, item_data in enumerate(line_items_data):
            item_dict = item_data.model_dump() if hasattr(item_data, 'model_dump') else item_data
            if 'position' not in item_dict:
                item_dict['position'] = idx
            db_item = LineItem(invoice_id=db_invoice.id, **item_dict)
            db.add(db_item)
        
        await db.commit()
        await db.refresh(db_invoice)
        
        # Load relationships
        result = await db.execute(
            select(Invoice)
            .filter(Invoice.id == db_invoice.id)
            .options(
                selectinload(Invoice.parties),
                selectinload(Invoice.line_items)
            )
        )
        return result.scalar_one()

    async def calculate_totals(self, db: AsyncSession, invoice_id: str) -> Invoice:
        """Recalculate invoice totals based on line items"""
        invoice = await self.get_with_details(db, invoice_id)
        if not invoice:
            return None
        
        # Calculate subtotal from line items
        subtotal = sum(item.amount for item in invoice.line_items)
        
        # Calculate tax
        tax_amount = subtotal * (invoice.tax_rate / 100) if invoice.tax_rate else 0
        
        # Calculate total
        total = subtotal + tax_amount + invoice.shipping_amount - invoice.discount_amount
        
        # Calculate balance due
        balance_due = total - invoice.amount_paid
        
        # Update invoice
        invoice.subtotal = subtotal
        invoice.tax_amount = tax_amount
        invoice.total = total
        invoice.balance_due = balance_due
        
        await db.commit()
        await db.refresh(invoice)
        return invoice


invoice = CRUDInvoice(Invoice)