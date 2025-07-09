from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"


class PartyType(str, enum.Enum):
    FROM = "from"
    TO = "to"
    SHIP_TO = "ship_to"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    payment_terms = Column(String(100))
    currency = Column(String(3), default="USD", nullable=False)
    
    # Financial fields
    subtotal = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    tax_rate = Column(DECIMAL(5, 2), default=0.00, nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    shipping_amount = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    total = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    amount_paid = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    balance_due = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    
    # Additional fields
    notes = Column(Text)
    terms = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    parties = relationship("InvoiceParty", back_populates="invoice", cascade="all, delete-orphan")
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceParty(Base):
    __tablename__ = "invoice_parties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    party_type = Column(Enum(PartyType), nullable=False)
    
    # Party details
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="parties")


class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    
    # Line item details
    description = Column(Text, nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Order
    position = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")