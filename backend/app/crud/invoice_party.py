from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.invoice import InvoiceParty, PartyType
from app.schemas.invoice_party import InvoicePartyCreate, InvoicePartyUpdate


class CRUDInvoiceParty(CRUDBase[InvoiceParty, InvoicePartyCreate, InvoicePartyUpdate]):
    def get_by_invoice(
        self, db: Session, invoice_id: str
    ) -> List[InvoiceParty]:
        """Get all parties for an invoice"""
        return db.query(InvoiceParty).filter(InvoiceParty.invoice_id == invoice_id).all()

    def get_by_invoice_and_type(
        self, db: Session, invoice_id: str, party_type: PartyType
    ) -> Optional[InvoiceParty]:
        """Get a specific party type for an invoice"""
        return db.query(InvoiceParty).filter(
            InvoiceParty.invoice_id == invoice_id,
            InvoiceParty.party_type == party_type
        ).first()

    def create_for_invoice(
        self, db: Session, invoice_id: str, *, obj_in: InvoicePartyCreate
    ) -> InvoiceParty:
        """Create a party for a specific invoice"""
        obj_in_data = obj_in.dict()
        db_obj = InvoiceParty(invoice_id=invoice_id, **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_or_create(
        self, db: Session, invoice_id: str, party_type: PartyType, *, obj_in: InvoicePartyCreate
    ) -> InvoiceParty:
        """Update existing party or create new one"""
        existing = self.get_by_invoice_and_type(db, invoice_id, party_type)
        
        if existing:
            # Update existing
            return self.update(db, db_obj=existing, obj_in=obj_in)
        else:
            # Create new
            return self.create_for_invoice(db, invoice_id, obj_in=obj_in)


invoice_party = CRUDInvoiceParty(InvoiceParty)