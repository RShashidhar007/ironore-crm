from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from .config import settings
from .database import Base, engine
from .routers import auth, customer, product, chat, complaint, notification, quotation
from .solution_generator_scheduler import start_solution_generator, stop_solution_generator

app = FastAPI(
    title="Iron Ore / Iron Pellet CRM Bot API",
    description="Backend for the CRM chatbot. Ollama and the frontend both talk to this API only.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(product.router)
app.include_router(chat.router)
app.include_router(complaint.router)
app.include_router(notification.router)
app.include_router(quotation.router)


@app.on_event("startup")
async def on_startup():
    # In SQLite mode, make sure tables exist. Against a real
    # SQL Server (DB_MODE=mssql) the six tables are assumed to already
    # exist and this call is a harmless no-op for existing tables.
    Base.metadata.create_all(bind=engine)
    
    # Start the solution generator scheduler
    try:
        await start_solution_generator()
    except Exception as e:
        print(f"Warning: Could not start solution generator scheduler: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    # Stop the solution generator scheduler
    try:
        await stop_solution_generator()
    except Exception:
        pass


@app.get("/api/health")
def health():
    return {"status": "ok"}
