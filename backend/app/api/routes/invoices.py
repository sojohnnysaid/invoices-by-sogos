from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.invoice import invoice as invoice_crud
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceWithDetails
from app.services.pdf_generator import InvoicePDFGenerator

router = APIRouter()


@router.get("/", response_model=List[InvoiceWithDetails])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of invoices with pagination."""
    return invoice_crud.get_multi_with_details(
        db, skip=skip, limit=limit, status=status
    )


@router.get("/{invoice_id}", response_model=InvoiceWithDetails)
async def get_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    """Get a specific invoice by ID."""
    invoice = invoice_crud.get_with_details(db, id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/", response_model=InvoiceWithDetails)
async def create_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    """Create a new invoice."""
    try:
        return invoice_crud.create_with_details(db, obj_in=invoice_in)
    except Exception as e:
        import traceback
        print(f"Error creating invoice: {str(e)}")
        print(f"Invoice data: {invoice_in.dict()}")
        print(f"Traceback: {traceback.format_exc()}")
        raise


@router.put("/{invoice_id}", response_model=InvoiceWithDetails)
async def update_invoice(
    invoice_id: UUID,
    invoice_in: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing invoice."""
    print(f"Updating invoice {invoice_id}")
    print(f"Update data: {invoice_in.dict()}")
    
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    result = invoice_crud.update_with_details(db, db_obj=invoice, obj_in=invoice_in)
    print(f"Update result: Invoice {result.invoice_number}, items: {len(result.line_items)}")
    return result


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    """Delete an invoice."""
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice_crud.remove(db, id=invoice_id)
    return {"message": "Invoice deleted successfully"}


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: UUID, db: Session = Depends(get_db)):
    """Generate and return PDF for an invoice."""
    # Get invoice with all details
    invoice = invoice_crud.get_with_details(db, id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Generate PDF
    pdf_generator = InvoicePDFGenerator()
    pdf_bytes = pdf_generator.generate_pdf(
        invoice=invoice,
        parties=invoice.parties,
        line_items=invoice.line_items
    )
    
    # Return PDF response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
        }
    )


@router.post("/{invoice_id}/duplicate", response_model=InvoiceWithDetails)
async def duplicate_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    """Duplicate an existing invoice."""
    # Get original invoice
    original = invoice_crud.get_with_details(db, id=invoice_id)
    if not original:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Create duplicate
    return invoice_crud.duplicate(db, original=original)