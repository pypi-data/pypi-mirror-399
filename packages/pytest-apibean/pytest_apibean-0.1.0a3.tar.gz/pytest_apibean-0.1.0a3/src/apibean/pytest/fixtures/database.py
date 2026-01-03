import importlib
import pytest

from apibean.pytest.decorators import abstract_fixture
from apibean.pytest.decorators import concrete_fixture
from apibean.pytest.helpers import silence_alembic_migration_logs
from apibean.pytest.protocols.database import ApibeanTestDatabase
from apibean.pytest.settings import settings


@pytest.fixture(scope="session")
@concrete_fixture
def apibean_db(apibean_migrate_db, apibean_connect_db) -> ApibeanTestDatabase:
    """
    Provide the application Database instance for the entire test session.

    This fixture composes the full database lifecycle required by tests:

    1. Ensure database schema is up-to-date by running migrations
       via ``apibean_migrate_db`` (if available).
    2. Create and expose a shared ``Database`` object through
       ``apibean_connect_db``.

    The returned Database instance is intended to be:
    - Session-scoped and reused across all tests.
    - The single source of truth for database engine and session management
      during the test run.

    Lifecycle responsibilities:
    - Schema preparation is handled before yielding.
    - Resource cleanup (engine disposal, connection closing) is delegated
      to ``apibean_connect_db`` after the test session completes.

    Applications may override lower-level fixtures (such as
    ``apibean_connect_db`` or ``apibean_migrate_db``) to customize database
    behavior without redefining this fixture.

    Yields:
        ApibeanTestDatabase: The initialized Database instance for test usage.
    """
    yield apibean_connect_db


@pytest.fixture(scope="session")
@concrete_fixture
def apibean_migrate_db() -> None:
    """
    Run Alembic migrations (upgrade head) if Alembic is available.

    This fixture attempts to detect Alembic dynamically. If Alembic
    is not installed or not configured by the application, migrations
    are skipped gracefully.

    The application is responsible for providing a valid Alembic
    configuration (alembic.ini or programmatic config).
    """

    try:
        alembic_config = importlib.import_module("alembic.config")
    except ImportError:
        # Application does not use Alembic
        yield
        return

    if not hasattr(alembic_config, "main"):
        yield
        return

    try:
        with silence_alembic_migration_logs():
            alembic_config.main(argv=["upgrade", "head"])
    except SystemExit:
        # Prevent alembic CLI from killing pytest
        pytest.fail("Alembic migration aborted the test session")
    except Exception as e:
        pytest.fail(f"Alembic migration failed: {e}")

    yield


@pytest.fixture(scope="session")
@concrete_fixture
def apibean_connect_db(apibean_safe_config) -> ApibeanTestDatabase:
    """
    Provide a Database handler for test execution.

    The fixture attempts to load the application's database handler module
    from the configured ``dbhandler_module_path`` option.

    If the module cannot be imported, the entire test session is skipped,
    requiring the application to provide its own database implementation.

    The returned object is expected to manage:
    - database engine lifecycle
    - session / connection factory
    - proper resource cleanup
    """

    dbhandler_class_name = (
        settings.dbhandler_class_name
        if hasattr(settings, "dbhandler_class_name")
        else "Database"
    )

    dbhandler_module_path = (
        settings.dbhandler_module_path
        if hasattr(settings, "dbhandler_module_path")
        else "app.core.database"
    )

    try:
        module = importlib.import_module(dbhandler_module_path)
    except ImportError:
        pytest.skip(
            f"Database handler module '{dbhandler_module_path}' not found. "
            "Please configure [tool.apibean.pytest.options].dbhandler_module_path "
            "or provide an application-level database handler."
        )

    if not hasattr(module, dbhandler_class_name):
        pytest.skip(
            f"Module '{dbhandler_module_path}' does not export a `{dbhandler_class_name}` class."
        )

    # Create test database handler
    db = module.Database(db_url=apibean_safe_config.DATABASE_URI, echo=apibean_safe_config.DB_ECHO)

    if not isinstance(db, ApibeanTestDatabase):
        pytest.skip(
            f"Database handler '{dbhandler_class_name}' does not conform to "
            "ApibeanTestDatabase protocol "
            "(required: engine property, session() method)."
        )

    yield db

    # Ensure engine & connections are properly disposed
    db.engine.dispose()


@pytest.fixture(scope="function")
def apibean_reset_db(apibean_container):
    """
    Reset application database state before each test.

    This fixture is responsible for clearing application data
    while preserving the database schema. It is typically used
    to ensure test isolation between test cases.

    The application must provide an implementation of this fixture.
    """
    test_service = apibean_container.test_service()
    test_service.reset_db()
    yield
