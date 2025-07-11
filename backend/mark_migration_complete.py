#!/usr/bin/env python3
"""
Script to mark the initial migration as complete in Alembic.
This is useful when the database already has the schema but Alembic doesn't know about it.
"""
import asyncio
import os
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def mark_migration_complete():
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://invoice_user:invoice_pass@postgres:5432/invoice_db")
    
    # Create engine
    engine = create_async_engine(database_url)
    
    async with engine.begin() as conn:
        # Check if alembic_version table exists
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            # Create alembic_version table
            await conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                );
            """))
            print("Created alembic_version table")
        
        # Check if migration is already marked
        result = await conn.execute(text("SELECT version_num FROM alembic_version WHERE version_num = '001'"))
        if result.scalar():
            print("Migration 001 is already marked as complete")
        else:
            # Insert the migration record
            await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('001')"))
            print("Marked migration 001 as complete")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(mark_migration_complete())