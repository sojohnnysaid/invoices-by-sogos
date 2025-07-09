from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.invoice import LineItem
from app.schemas.line_item import LineItemCreate, LineItemUpdate


class CRUDLineItem(CRUDBase[LineItem, LineItemCreate, LineItemUpdate]):
    def get_by_invoice(
        self, db: Session, invoice_id: str
    ) -> List[LineItem]:
        """Get all line items for an invoice, ordered by position"""
        return db.query(LineItem)\
            .filter(LineItem.invoice_id == invoice_id)\
            .order_by(LineItem.position)\
            .all()

    def create_for_invoice(
        self, db: Session, invoice_id: str, *, obj_in: LineItemCreate
    ) -> LineItem:
        """Create a line item for a specific invoice"""
        # If position not specified, add to end
        if not hasattr(obj_in, 'position') or obj_in.position is None:
            max_position = db.query(func.max(LineItem.position))\
                .filter(LineItem.invoice_id == invoice_id)\
                .scalar()
            position = (max_position or -1) + 1
            obj_in_data = obj_in.dict()
            obj_in_data['position'] = position
        else:
            obj_in_data = obj_in.dict()
        
        db_obj = LineItem(invoice_id=invoice_id, **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

    def update(
        self, db: Session, *, db_obj: LineItem, obj_in: LineItemUpdate
    ) -> LineItem:
        """Update a line item"""
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> LineItem:
        """Remove a line item"""
        item = self.get(db, id)
        if not item:
            return None
        
        return super().remove(db, id=id)

    def reorder(
        self, db: Session, invoice_id: str, item_id: str, new_position: int
    ) -> List[LineItem]:
        """Reorder line items by changing position"""
        items = self.get_by_invoice(db, invoice_id)
        
        # Find the item to move
        item_to_move = None
        for item in items:
            if str(item.id) == item_id:
                item_to_move = item
                break
        
        if not item_to_move:
            return items
        
        old_position = item_to_move.position
        
        # Update positions
        if new_position < old_position:
            # Moving up: increment positions between new and old
            for item in items:
                if new_position <= item.position < old_position:
                    item.position += 1
        else:
            # Moving down: decrement positions between old and new
            for item in items:
                if old_position < item.position <= new_position:
                    item.position -= 1
        
        # Set new position
        item_to_move.position = new_position
        
        # Save all changes
        db.commit()
        
        # Return reordered list
        return self.get_by_invoice(db, invoice_id)


line_item = CRUDLineItem(LineItem)