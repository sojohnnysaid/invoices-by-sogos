from typing import List, Optional, Union, Dict, Any
from decimal import Decimal
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.invoice import Invoice, InvoiceStatus, InvoiceParty, LineItem, PartyType
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceWithDetails


class CRUDInvoice(CRUDBase[Invoice, InvoiceCreate, InvoiceUpdate]):
    def get_with_details(self, db: Session, id: UUID) -> Optional[Invoice]:
        """Get invoice with all related data (parties and line items)"""
        return db.query(Invoice)\
            .options(
                joinedload(Invoice.parties),
                joinedload(Invoice.line_items)
            )\
            .filter(Invoice.id == id)\
            .first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> List[Invoice]:
        """Get multiple invoices with all related data"""
        query = db.query(Invoice)\
            .options(
                joinedload(Invoice.parties),
                joinedload(Invoice.line_items)
            )
        
        if status:
            query = query.filter(Invoice.status == status)
        
        return query.order_by(Invoice.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_invoice_number(self, db: Session, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number"""
        return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

    def get_by_status(
        self, db: Session, status: InvoiceStatus, *, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """Get all invoices with a specific status"""
        return db.query(Invoice)\
            .filter(Invoice.status == status)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_overdue(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get all overdue invoices"""
        return db.query(Invoice)\
            .filter(
                and_(
                    Invoice.due_date < datetime.utcnow(),
                    Invoice.status.in_([InvoiceStatus.SENT])
                )
            )\
            .offset(skip)\
            .limit(limit)\
            .all()

    def _calculate_totals(self, invoice_data: Dict[str, Any], line_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate invoice totals based on line items and other amounts"""
        # Calculate subtotal from line items
        subtotal = Decimal('0')
        for item in line_items:
            quantity = Decimal(str(item.get('quantity', 0)))
            unit_price = Decimal(str(item.get('unit_price', 0)))
            amount = quantity * unit_price
            item['amount'] = float(amount)
            subtotal += amount
        
        # Get other amounts
        tax_rate = Decimal(str(invoice_data.get('tax_rate', 0)))
        discount_amount = Decimal(str(invoice_data.get('discount_amount', 0)))
        shipping_amount = Decimal(str(invoice_data.get('shipping_amount', 0)))
        amount_paid = Decimal(str(invoice_data.get('amount_paid', 0)))
        
        # Calculate tax
        tax_amount = subtotal * (tax_rate / 100)
        
        # Calculate total
        total = subtotal + tax_amount + shipping_amount - discount_amount
        
        # Calculate balance due
        balance_due = total - amount_paid
        
        # Update invoice data
        invoice_data['subtotal'] = float(subtotal)
        invoice_data['tax_amount'] = float(tax_amount)
        invoice_data['total'] = float(total)
        invoice_data['balance_due'] = float(balance_due)
        
        return invoice_data

    def create_with_details(self, db: Session, *, obj_in: InvoiceCreate) -> Invoice:
        """Create invoice with parties and line items"""
        # Extract nested data
        parties_data = obj_in.parties if hasattr(obj_in, 'parties') and obj_in.parties else []
        line_items_data = obj_in.line_items if hasattr(obj_in, 'line_items') and obj_in.line_items else []
        
        # Convert line items to dict for calculation
        line_items_dict = [item.dict() if hasattr(item, 'dict') else item for item in line_items_data]
        
        # Create invoice data and calculate totals
        invoice_data = obj_in.dict(exclude={'parties', 'line_items'})
        invoice_data = self._calculate_totals(invoice_data, line_items_dict)
        
        # Create invoice
        db_invoice = Invoice(**invoice_data)
        db.add(db_invoice)
        db.flush()  # Flush to get the ID without committing
        
        # Create related parties
        for party_data in parties_data:
            party_dict = party_data.dict() if hasattr(party_data, 'dict') else party_data
            db_party = InvoiceParty(invoice_id=db_invoice.id, **party_dict)
            db.add(db_party)
        
        # Create related line items with calculated amounts
        for idx, (item_data, item_dict) in enumerate(zip(line_items_data, line_items_dict)):
            if 'position' not in item_dict:
                item_dict['position'] = idx
            db_item = LineItem(invoice_id=db_invoice.id, **item_dict)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_invoice)
        
        # Load relationships
        return self.get_with_details(db, db_invoice.id)

    def update_with_details(
        self, db: Session, *, db_obj: Invoice, obj_in: Union[InvoiceUpdate, Dict[str, Any]]
    ) -> Invoice:
        """Update invoice with parties and line items"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle parties update if provided
        if 'parties' in update_data:
            # Remove existing parties
            db.query(InvoiceParty).filter(InvoiceParty.invoice_id == db_obj.id).delete()
            
            # Add new parties
            for party_data in update_data['parties']:
                party_dict = party_data.dict() if hasattr(party_data, 'dict') else party_data
                db_party = InvoiceParty(invoice_id=db_obj.id, **party_dict)
                db.add(db_party)
            
            del update_data['parties']
        
        # Handle line items update if provided
        if 'line_items' in update_data:
            # Remove existing line items
            db.query(LineItem).filter(LineItem.invoice_id == db_obj.id).delete()
            
            # Convert line items for calculation
            line_items_dict = [item.dict() if hasattr(item, 'dict') else item for item in update_data['line_items']]
            
            # Recalculate totals
            update_data = self._calculate_totals(update_data, line_items_dict)
            
            # Add new line items
            for idx, item_dict in enumerate(line_items_dict):
                if 'position' not in item_dict:
                    item_dict['position'] = idx
                db_item = LineItem(invoice_id=db_obj.id, **item_dict)
                db.add(db_item)
            
            del update_data['line_items']
        elif any(key in update_data for key in ['tax_rate', 'discount_amount', 'shipping_amount', 'amount_paid']):
            # If any amount field is updated, recalculate totals
            line_items = db.query(LineItem).filter(LineItem.invoice_id == db_obj.id).all()
            line_items_dict = [
                {
                    'quantity': float(item.quantity),
                    'unit_price': float(item.unit_price),
                    'amount': float(item.amount)
                }
                for item in line_items
            ]
            update_data = self._calculate_totals(update_data, line_items_dict)
        
        # Update invoice
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def duplicate(self, db: Session, *, original: Invoice) -> Invoice:
        """Duplicate an existing invoice"""
        # Generate new invoice number (this should be handled by a service)
        from app.services.invoice_service import generate_invoice_number
        new_invoice_number = generate_invoice_number(db)
        
        # Create new invoice data
        invoice_data = {
            'invoice_number': new_invoice_number,
            'status': InvoiceStatus.DRAFT,
            'date': datetime.utcnow(),
            'due_date': original.due_date,
            'payment_terms': original.payment_terms,
            'currency': original.currency,
            'subtotal': original.subtotal,
            'tax_rate': original.tax_rate,
            'tax_amount': original.tax_amount,
            'discount_amount': original.discount_amount,
            'shipping_amount': original.shipping_amount,
            'total': original.total,
            'amount_paid': Decimal('0'),  # Reset amount paid
            'balance_due': original.total,  # Reset balance due to total
            'notes': original.notes,
            'terms': original.terms,
        }
        
        # Create new invoice
        db_invoice = Invoice(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        # Duplicate parties
        for party in original.parties:
            party_data = {
                'invoice_id': db_invoice.id,
                'party_type': party.party_type,
                'name': party.name,
                'address': party.address,
                'city': party.city,
                'state': party.state,
                'zip_code': party.zip_code,
                'country': party.country,
                'email': party.email,
                'phone': party.phone,
            }
            db_party = InvoiceParty(**party_data)
            db.add(db_party)
        
        # Duplicate line items
        for item in original.line_items:
            item_data = {
                'invoice_id': db_invoice.id,
                'description': item.description,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'amount': item.amount,
                'position': item.position,
            }
            db_item = LineItem(**item_data)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_invoice)
        
        return self.get_with_details(db, db_invoice.id)


invoice = CRUDInvoice(Invoice)