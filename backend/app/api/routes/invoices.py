from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db
from app.models.invoice import Invoice as InvoiceModel
from app.models.defaults import InvoiceDefaults as DefaultsModel
from app.schemas.invoice import Invoice, InvoiceCreate, InvoiceUpdate, InvoiceList

router = APIRouter()


def calculate_invoice_totals(items: list, tax_rate: float) -> dict:
    """Calculate subtotal, tax amount, and total for invoice."""
    subtotal = sum(item.get("quantity", 1) * item.get("rate", 0) for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount
    
    # Also update item amounts
    for item in items:
        item["amount"] = item.get("quantity", 1) * item.get("rate", 0)
    
    return {
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
        "items": items
    }


def generate_invoice_number(db: Session) -> str:
    """Generate next invoice number based on defaults."""
    defaults = db.query(DefaultsModel).first()
    if not defaults:
        # Create default settings if not exists
        defaults = DefaultsModel()
        db.add(defaults)
        db.commit()
        db.refresh(defaults)
    
    invoice_number = f"{defaults.invoice_prefix}-{str(defaults.next_invoice_number).zfill(5)}"
    
    # Update next invoice number
    defaults.next_invoice_number += 1
    db.commit()
    
    return invoice_number


@router.get("/", response_model=InvoiceList)
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of invoices with pagination.
    """
    query = db.query(InvoiceModel)
    
    if status:
        query = query.filter(InvoiceModel.status == status)
    
    total = query.count()
    invoices = query.order_by(desc(InvoiceModel.created_at)).offset(skip).limit(limit).all()
    
    return InvoiceList(total=total, items=invoices)


@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Get a specific invoice by ID.
    """
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/", response_model=Invoice)
async def create_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    """
    Create a new invoice.
    """
    # Generate invoice number
    invoice_number = generate_invoice_number(db)
    
    # Calculate totals
    items_data = [item.dict() for item in invoice_in.items] if invoice_in.items else []
    totals = calculate_invoice_totals(items_data, invoice_in.tax_rate)
    
    # Create invoice
    db_invoice = InvoiceModel(
        invoice_number=invoice_number,
        client_name=invoice_in.client_name,
        client_email=invoice_in.client_email,
        client_address=invoice_in.client_address,
        issue_date=invoice_in.issue_date or datetime.now(),
        due_date=invoice_in.due_date,
        items=totals["items"],
        subtotal=totals["subtotal"],
        tax_rate=invoice_in.tax_rate,
        tax_amount=totals["tax_amount"],
        total=totals["total"],
        notes=invoice_in.notes,
        status=invoice_in.status
    )
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice


@router.put("/{invoice_id}", response_model=Invoice)
async def update_invoice(
    invoice_id: int,
    invoice_in: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing invoice.
    """
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update fields
    update_data = invoice_in.dict(exclude_unset=True)
    
    # If items or tax_rate changed, recalculate totals
    if "items" in update_data or "tax_rate" in update_data:
        items_data = [item.dict() for item in invoice_in.items] if invoice_in.items else invoice.items
        tax_rate = invoice_in.tax_rate if invoice_in.tax_rate is not None else invoice.tax_rate
        totals = calculate_invoice_totals(items_data, tax_rate)
        
        update_data.update({
            "items": totals["items"],
            "subtotal": totals["subtotal"],
            "tax_amount": totals["tax_amount"],
            "total": totals["total"]
        })
    
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Delete an invoice.
    """
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    db.delete(invoice)
    db.commit()
    
    return {"message": "Invoice deleted successfully"}


@router.post("/{invoice_id}/duplicate", response_model=Invoice)
async def duplicate_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Duplicate an existing invoice.
    """
    # Get original invoice
    original = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Generate new invoice number
    invoice_number = generate_invoice_number(db)
    
    # Create duplicate
    duplicate = InvoiceModel(
        invoice_number=invoice_number,
        client_name=original.client_name,
        client_email=original.client_email,
        client_address=original.client_address,
        issue_date=datetime.now(),
        due_date=original.due_date,
        items=original.items,
        subtotal=original.subtotal,
        tax_rate=original.tax_rate,
        tax_amount=original.tax_amount,
        total=original.total,
        notes=original.notes,
        status="draft"  # New duplicates start as draft
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate