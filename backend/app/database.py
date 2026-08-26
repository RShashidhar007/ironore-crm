from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import pyodbc

from .config import settings

# Configure pyodbc to use comma as decimal separator for MSSQL connections
# Note: This should be set BEFORE any database connections are made
if settings.DB_MODE == "mssql":
    try:
        # pyodbc.setDecimalSeparator() expects one argument
        # But we're using the default decimal handling, so we'll skip this for now
        # If needed in future, use: pyodbc.setDecimalSeparator(lambda s: s.replace(',', '.'))
        pass
    except Exception as e:
        # Silently fail if decimal separator configuration fails
        pass

connect_args = {"check_same_thread": False} if settings.DB_MODE == "sqlite" else {}

# Use NullPool for MSSQL to avoid connection pooling issues
# Connection pooling can cause timeout issues with the pyodbc driver
pool_class = NullPool if settings.DB_MODE == "mssql" else None

engine = create_engine(
    settings.sqlalchemy_database_uri,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
    poolclass=pool_class,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
