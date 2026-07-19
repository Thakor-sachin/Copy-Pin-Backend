from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = None

# Attempt to connect to PostgreSQL with a brief timeout
if DATABASE_URL.startswith("postgresql"):
    try:
        # Create a temporary engine just to test the connection quickly
        temp_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 2})
        with temp_engine.connect() as conn:
            pass
        # Connection succeeded
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        print("Database: PostgreSQL connection active.")
    except Exception as e:
        print(f"Database: PostgreSQL connection failed ({str(e)}). Falling back to local SQLite database.")
        DATABASE_URL = "sqlite:///./copypin.db"

# Setup engine (configuring SQLite correctly for FastAPI threads if necessary)
if engine is None:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class
Base = declarative_base()

# Dependency provider
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
