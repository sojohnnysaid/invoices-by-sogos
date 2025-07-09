from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.defaults import InvoiceDefaults as DefaultsModel
from app.schemas.defaults import InvoiceDefaults, InvoiceDefaultsUpdate

router = APIRouter()


@router.get("/", response_model=InvoiceDefaults)
async def get_defaults(db: Session = Depends(get_db)):
    """
    Get invoice default settings.
    """
    defaults = db.query(DefaultsModel).first()
    
    if not defaults:
        # Create default settings if not exists
        defaults = DefaultsModel()
        db.add(defaults)
        db.commit()
        db.refresh(defaults)
    
    return defaults


@router.put("/", response_model=InvoiceDefaults)
async def update_defaults(
    defaults_in: InvoiceDefaultsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update invoice default settings.
    """
    defaults = db.query(DefaultsModel).first()
    
    if not defaults:
        # Create if not exists
        defaults = DefaultsModel(**defaults_in.dict(exclude_unset=True))
        db.add(defaults)
    else:
        # Update existing
        update_data = defaults_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(defaults, field, value)
    
    db.commit()
    db.refresh(defaults)
    
    return defaults