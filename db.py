from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    url="postgresql+psycopg2://postgres:postgres@localhost:5432/dev-meet-blog"
)

Session = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    """Context manager to ensure the session is closed after use."""
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise


DbSession = Annotated[Session, Depends(get_db)]
