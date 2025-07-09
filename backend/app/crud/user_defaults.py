from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.user_defaults import UserDefaults
from app.schemas.user_defaults import UserDefaultsCreate, UserDefaultsUpdate


class CRUDUserDefaults(CRUDBase[UserDefaults, UserDefaultsCreate, UserDefaultsUpdate]):
    async def get_by_user(
        self, db: AsyncSession, user_identifier: str
    ) -> Optional[UserDefaults]:
        """Get user defaults by user identifier"""
        result = await db.execute(
            select(UserDefaults).filter(UserDefaults.user_identifier == user_identifier)
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, db: AsyncSession, user_identifier: str, *, obj_in: UserDefaultsCreate
    ) -> UserDefaults:
        """Create new user defaults or update existing ones"""
        existing = await self.get_by_user(db, user_identifier)
        
        if existing:
            # Update existing
            return await self.update(db, db_obj=existing, obj_in=obj_in)
        else:
            # Create new
            return await self.create(db, obj_in=obj_in)

    async def increment_invoice_number(
        self, db: AsyncSession, user_identifier: str
    ) -> int:
        """Increment and return the next invoice number for a user"""
        user_defaults = await self.get_by_user(db, user_identifier)
        
        if not user_defaults:
            # Create default settings if not exist
            user_defaults = await self.create(
                db,
                obj_in=UserDefaultsCreate(user_identifier=user_identifier)
            )
        
        # Get current number
        next_number = user_defaults.next_invoice_number
        
        # Increment for next time
        user_defaults.next_invoice_number = next_number + 1
        await db.commit()
        
        return next_number

    async def get_next_invoice_number(
        self, db: AsyncSession, user_identifier: str
    ) -> str:
        """Get the next invoice number with prefix"""
        user_defaults = await self.get_by_user(db, user_identifier)
        
        if not user_defaults:
            # Return default if no settings
            return "INV-1"
        
        return f"{user_defaults.invoice_number_prefix}{user_defaults.next_invoice_number}"


user_defaults = CRUDUserDefaults(UserDefaults)