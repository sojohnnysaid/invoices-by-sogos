from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.invoice import PartyType


class InvoicePartyBase(BaseModel):
    party_type: PartyType
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)


class InvoicePartyCreate(InvoicePartyBase):
    pass


class InvoicePartyUpdate(BaseModel):
    party_type: Optional[PartyType] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)


class InvoiceParty(InvoicePartyBase):
    id: UUID
    invoice_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True