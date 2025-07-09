from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.models.invoice import InvoiceStatus
from .invoice_party import InvoiceParty
from .line_item import LineItem


class InvoiceBase(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=50)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    date: datetime
    due_date: datetime
    payment_terms: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    shipping_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total: Decimal = Field(default=Decimal("0.00"), ge=0)
    amount_paid: Decimal = Field(default=Decimal("0.00"), ge=0)
    balance_due: Decimal = Field(default=Decimal("0.00"), ge=0)
    notes: Optional[str] = None
    terms: Optional[str] = None

    @validator('due_date')
    def due_date_must_be_after_date(cls, v, values):
        if 'date' in values and v < values['date']:
            raise ValueError('Due date must be after invoice date')
        return v

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class InvoiceCreate(InvoiceBase):
    parties: Optional[List['InvoicePartyCreate']] = []
    line_items: Optional[List['LineItemCreate']] = []


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[InvoiceStatus] = None
    date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_terms: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    subtotal: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    shipping_amount: Optional[Decimal] = Field(None, ge=0)
    total: Optional[Decimal] = Field(None, ge=0)
    amount_paid: Optional[Decimal] = Field(None, ge=0)
    balance_due: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    terms: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class Invoice(InvoiceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceWithDetails(Invoice):
    parties: List[InvoiceParty] = []
    line_items: List[LineItem] = []

    class Config:
        from_attributes = True


# Fix circular import
from .invoice_party import InvoicePartyCreate
from .line_item import LineItemCreate
InvoiceCreate.model_rebuild()