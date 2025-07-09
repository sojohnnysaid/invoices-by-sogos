from sqlalchemy.orm import Session
from app.models.defaults import InvoiceDefaults


def generate_invoice_number(db: Session) -> str:
    """Generate next invoice number based on user defaults."""
    # Get or create defaults
    defaults = db.query(InvoiceDefaults).first()
    if not defaults:
        # Create default settings if not exists
        defaults = InvoiceDefaults(
            invoice_prefix="INV",
            next_invoice_number=1
        )
        db.add(defaults)
        db.commit()
        db.refresh(defaults)
    
    # Generate invoice number
    invoice_number = f"{defaults.invoice_prefix}-{str(defaults.next_invoice_number).zfill(5)}"
    
    # Update next invoice number
    defaults.next_invoice_number += 1
    db.commit()
    
    return invoice_number