from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.line_item import LineItem
from app.schemas.line_item import LineItemCreate, LineItemUpdate


class CRUDLineItem(CRUDBase[LineItem, LineItemCreate, LineItemUpdate]):
    async def get_by_invoice(
        self, db: AsyncSession, invoice_id: str
    ) -> List[LineItem]:
        """Get all line items for an invoice, ordered by position"""
        result = await db.execute(
            select(LineItem)
            .filter(LineItem.invoice_id == invoice_id)
            .order_by(LineItem.position)
        )
        return result.scalars().all()

    async def create_for_invoice(
        self, db: AsyncSession, invoice_id: str, *, obj_in: LineItemCreate
    ) -> LineItem:
        """Create a line item for a specific invoice"""
        # If position not specified, add to end
        if not hasattr(obj_in, 'position') or obj_in.position is None:
            result = await db.execute(
                select(func.max(LineItem.position))
                .filter(LineItem.invoice_id == invoice_id)
            )
            max_position = result.scalar()
            position = (max_position or -1) + 1
            obj_in_data = obj_in.model_dump()
            obj_in_data['position'] = position
        else:
            obj_in_data = obj_in.model_dump()
        
        db_obj = LineItem(invoice_id=invoice_id, **obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update invoice totals
        from app.crud.invoice import invoice as crud_invoice
        await crud_invoice.calculate_totals(db, invoice_id)
        
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: LineItem, obj_in: LineItemUpdate
    ) -> LineItem:
        """Update a line item and recalculate invoice totals"""
        updated_item = await super().update(db, db_obj=db_obj, obj_in=obj_in)
        
        # Update invoice totals
        from app.crud.invoice import invoice as crud_invoice
        await crud_invoice.calculate_totals(db, updated_item.invoice_id)
        
        return updated_item

    async def remove(self, db: AsyncSession, *, id: str) -> LineItem:
        """Remove a line item and recalculate invoice totals"""
        item = await self.get(db, id)
        if not item:
            return None
        
        invoice_id = item.invoice_id
        removed_item = await super().remove(db, id=id)
        
        # Update invoice totals
        from app.crud.invoice import invoice as crud_invoice
        await crud_invoice.calculate_totals(db, invoice_id)
        
        return removed_item

    async def reorder(
        self, db: AsyncSession, invoice_id: str, item_id: str, new_position: int
    ) -> List[LineItem]:
        """Reorder line items by changing position"""
        items = await self.get_by_invoice(db, invoice_id)
        
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
        await db.commit()
        
        # Return reordered list
        return await self.get_by_invoice(db, invoice_id)


line_item = CRUDLineItem(LineItem)