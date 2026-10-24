from typing import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import db_config


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=db_config.user,
    password=db_config.password,
    host=db_config.host,
    port=db_config.port,
    database=db_config.dbname,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "options": "-c timezone=UTC",
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_database() -> None:
    engine.dispose()