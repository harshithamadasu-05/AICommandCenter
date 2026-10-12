from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def ensure_schema(bind=engine):
    Base.metadata.create_all(bind=bind)

    emergency_columns = {
        column["name"] for column in inspect(bind).get_columns("emergencies")
    }
    if "accident_severity" not in emergency_columns:
        with bind.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE emergencies "
                    "ADD COLUMN accident_severity VARCHAR DEFAULT 'Critical'"
                )
            )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
