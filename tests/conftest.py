import asyncio
import logging

import pytest
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import InternalError, ProgrammingError
from sqlalchemy.orm import sessionmaker

from db_triggers.router import discover_replaceable_entities
from models import AbstractBase
from tests.conftest_utils.db_helper import SqlDbTestConnector

LOGGER = logging.getLogger(__file__)
TRIGGER_ENTITIES = discover_replaceable_entities()


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_connector():
    with SqlDbTestConnector() as connector:
        yield connector


@pytest.fixture(scope="session")
def setup_test_engine(db_connector):
    engine = create_engine(db_connector.get_sync_db_url(), echo=True)
    LOGGER.info("Creating tables...")
    AbstractBase.metadata.create_all(engine)
    LOGGER.info(db_connector.get_sync_db_url())

    yield engine


@pytest.fixture(scope="session", autouse=True)
def install_db_functions(setup_test_engine):
    # First install all PGFunctions
    #  Drop triggers first using raw SQL for guaranteed execution
    for obj in TRIGGER_ENTITIES:
        if isinstance(obj, PGTrigger):
            with setup_test_engine.begin() as conn:
                try:
                    drop_trigger_sql = (
                        f'DROP TRIGGER IF EXISTS "{obj.signature}" ON {obj.on_entity};'
                    )
                    conn.execute(text(drop_trigger_sql))
                except Exception as e:
                    print(f"[WARN] Could not drop trigger {obj.signature}: {e}")

    # Drop functions after all triggers are gone
    for obj in TRIGGER_ENTITIES:
        if isinstance(obj, PGFunction):
            with setup_test_engine.begin() as conn:
                try:
                    drop_sql = f"DROP FUNCTION {obj.signature} CASCADE;"
                    conn.execute(text(drop_sql))

                except ProgrammingError:
                    pass
                except Exception as e:
                    print(f"[WARN] Could not drop function {obj.signature}: {e}")

    for obj in TRIGGER_ENTITIES:
        if isinstance(obj, PGFunction):
            with setup_test_engine.begin() as conn:
                try:
                    drop_sql = obj.to_sql_statement_drop()
                    conn.execute(drop_sql)
                except ProgrammingError:
                    pass
            with setup_test_engine.begin() as conn:
                create_sql = obj.to_sql_statement_create()
                conn.execute(create_sql)


@pytest.fixture(scope="session", autouse=True)
def install_db_triggers(install_db_functions, setup_test_engine):
    for obj in TRIGGER_ENTITIES:

        if isinstance(obj, PGTrigger):
            with setup_test_engine.begin() as conn:
                try:
                    drop_trigger_sql = (
                        f'DROP TRIGGER IF EXISTS "{obj.signature}" ON {obj.on_entity};'
                    )
                    conn.execute(text(drop_trigger_sql))
                except InternalError:
                    pass
            with setup_test_engine.begin() as conn:

                create_sql = obj.to_sql_statement_create()
                conn.execute(create_sql)  # no text() wrapping


@pytest.fixture(scope="function")
def session(setup_test_engine):
    Session = sessionmaker(bind=setup_test_engine, expire_on_commit=False)
    with Session() as session:

        # with patch(
        #     "accountant.database.handlers.user_handler.async_session"
        # ) as mock_session:
        #     mock_session.return_value = session

        yield session
