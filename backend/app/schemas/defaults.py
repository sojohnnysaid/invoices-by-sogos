from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class InvoiceDefaultsBase(BaseModel):
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    company_logo: Optional[str] = None
    default_payment_terms: int = 30
    default_tax_rate: float = 0.0
    default_currency: str = "USD"
    invoice_prefix: str = "INV"
    next_invoice_number: int = 1
    payment_instructions: Optional[str] = None
    footer_text: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class InvoiceDefaultsCreate(InvoiceDefaultsBase):
    pass


class InvoiceDefaultsUpdate(InvoiceDefaultsBase):
    pass


class InvoiceDefaults(InvoiceDefaultsBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True