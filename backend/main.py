"""
Main application entry point
This file demonstrates how to use the database setup
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import create_tables

# Create FastAPI instance with lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Uncomment to create tables on startup (for development)
    # await create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="Invoice Generator API",
    description="Backend API for invoice generation",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Invoice Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example of how to run migrations programmatically:
# Run in terminal: alembic revision --autogenerate -m "Initial migration"
# Run in terminal: alembic upgrade head

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)