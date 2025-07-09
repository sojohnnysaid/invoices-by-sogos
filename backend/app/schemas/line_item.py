from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class LineItemBase(BaseModel):
    description: str = Field(..., min_length=1)
    quantity: Decimal = Field(..., gt=0)
    rate: Decimal = Field(..., ge=0)
    amount: Decimal = Field(..., ge=0)
    position: int = Field(default=0, ge=0)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class LineItemCreate(LineItemBase):
    pass


class LineItemUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    quantity: Optional[Decimal] = Field(None, gt=0)
    rate: Optional[Decimal] = Field(None, ge=0)
    amount: Optional[Decimal] = Field(None, ge=0)
    position: Optional[int] = Field(None, ge=0)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class LineItem(LineItemBase):
    id: UUID
    invoice_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True