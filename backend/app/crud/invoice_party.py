from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.invoice_party import InvoiceParty, PartyType
from app.schemas.invoice_party import InvoicePartyCreate, InvoicePartyUpdate


class CRUDInvoiceParty(CRUDBase[InvoiceParty, InvoicePartyCreate, InvoicePartyUpdate]):
    async def get_by_invoice(
        self, db: AsyncSession, invoice_id: str
    ) -> List[InvoiceParty]:
        """Get all parties for an invoice"""
        result = await db.execute(
            select(InvoiceParty).filter(InvoiceParty.invoice_id == invoice_id)
        )
        return result.scalars().all()

    async def get_by_invoice_and_type(
        self, db: AsyncSession, invoice_id: str, party_type: PartyType
    ) -> Optional[InvoiceParty]:
        """Get a specific party type for an invoice"""
        result = await db.execute(
            select(InvoiceParty).filter(
                InvoiceParty.invoice_id == invoice_id,
                InvoiceParty.party_type == party_type
            )
        )
        return result.scalar_one_or_none()

    async def create_for_invoice(
        self, db: AsyncSession, invoice_id: str, *, obj_in: InvoicePartyCreate
    ) -> InvoiceParty:
        """Create a party for a specific invoice"""
        obj_in_data = obj_in.model_dump()
        db_obj = InvoiceParty(invoice_id=invoice_id, **obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_or_create(
        self, db: AsyncSession, invoice_id: str, party_type: PartyType, *, obj_in: InvoicePartyCreate
    ) -> InvoiceParty:
        """Update existing party or create new one"""
        existing = await self.get_by_invoice_and_type(db, invoice_id, party_type)
        
        if existing:
            # Update existing
            return await self.update(db, db_obj=existing, obj_in=obj_in)
        else:
            # Create new
            return await self.create_for_invoice(db, invoice_id, obj_in=obj_in)


invoice_party = CRUDInvoiceParty(InvoiceParty)