from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class InvoiceDefaults(Base):
    __tablename__ = "invoice_defaults"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    company_email = Column(String)
    company_phone = Column(String)
    company_address = Column(Text)
    company_logo = Column(String)  # URL or base64
    default_payment_terms = Column(Integer, default=30)  # Days
    default_tax_rate = Column(Float, default=0.0)
    default_currency = Column(String, default="USD")
    invoice_prefix = Column(String, default="INV")
    next_invoice_number = Column(Integer, default=1)
    payment_instructions = Column(Text)
    footer_text = Column(Text)
    custom_fields = Column(JSON)  # Additional custom fields
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())