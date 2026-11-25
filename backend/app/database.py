import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("studymate.database")

# Ensure backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import settings
import urllib.parse

# Engine configuration based on dialect
database_url = settings.DATABASE_URL
engine = None
fallback_used = False

# Auto-fix password escaping if password contains '@'
if database_url and ("postgresql://" in database_url or "postgresql+" in database_url):
    try:
        # Standardize dialect for psycopg 3
        if database_url.startswith("postgresql://"):
            database_url = "postgresql+psycopg://" + database_url[len("postgresql://"):]
        
        # If multiple '@' are in the URL, password contains '@' and must be URL encoded
        if database_url.count('@') > 1:
            proto, rest = database_url.split('://', 1)
            auth, host_part = rest.rsplit('@', 1)
            if ':' in auth:
                user, pwd = auth.split(':', 1)
                database_url = f"{proto}://{user}:{urllib.parse.quote(pwd)}@{host_part}"
    except Exception as e:
        logger.warning(f"DATABASE_URL parse notice: {e}")

if database_url.startswith("postgresql"):
    try:
        # Create Supabase PostgreSQL engine with connection pooling and resilient connection timeout
        pg_engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 20},
            echo=False
        )
        # Test connection
        with pg_engine.connect() as conn:
            pass
        engine = pg_engine
        print(f"[DATABASE] Connected to Supabase Cloud PostgreSQL: {database_url.split('@')[-1] if '@' in database_url else 'PostgreSQL'}")
    except Exception as e:
        print(f"\n" + "=" * 70)
        print("  [SUPABASE CLOUD POSTGRESQL NOTICE]")
        print(f"  Target: {database_url}")
        print("  Status: Supabase Cloud database connection pending or unreachable.")
        print("  Details:", str(e).split("\n")[0])
        print("  To connect your Supabase Cloud Database:")
        print("    1. Go to https://supabase.com -> Project Settings -> Database")
        print("    2. Copy the URI string (port 5432 or 6543 pooler)")
        print("    3. Set in your .env: DATABASE_URL=postgresql+psycopg://postgres:[PASSWORD]@[HOST]:[PORT]/postgres")
        print("    4. Run backend/database/supabase_schema.sql in the Supabase SQL Editor")
        print("  [STORAGE NOTE] Local file databases disabled. Using in-memory RAM session.")
        print("=" * 70 + "\n")
        fallback_used = True
        # In-memory RAM database - creates ZERO files on disk
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
else:
    # In-memory RAM database - creates ZERO files on disk
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Initializes tables on the current engine if needed."""
    from app.models import user, document, chat_history, flashcard, quiz_result, extra
    Base.metadata.create_all(bind=engine)


# If in-memory fallback was triggered, ensure tables and seed data are ready
if fallback_used:
    try:
        init_db()
        from seed_data import seed_database
        seed_database()
    except Exception as e:
        logger.warning(f"In-memory init notice: {e}")


def get_db():
    """FastAPI Dependency for database session management with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes tables in database if they do not exist."""
    import app.models  # Registers all models with Base.metadata
    Base.metadata.create_all(bind=engine)
