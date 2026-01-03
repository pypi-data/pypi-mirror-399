import anyio
import importlib
import pytest

from apibean.pytest.decorators import concrete_fixture
from apibean.pytest.settings import settings

@pytest.fixture(scope="function")
@concrete_fixture
def apibean_seed_modules() -> str:
    """
    Return the module path(s) where apibean seeders are defined.

    This fixture provides the import path used to discover and load
    seeder classes or functions responsible for initializing test data.

    Developers may override this fixture in their application or test
    suite to customize where seeder modules are located.

    If not explicitly configured, it defaults to "tests.seeders".
    """
    return settings.seed_modules or "tests.seeders"

@pytest.fixture(scope="function")
@concrete_fixture
def apibean_seed_data(request, apibean_container, apibean_seed_modules):
    """
    Seed test data based on ``@pytest.mark.seed`` markers.

    This fixture inspects the current test node for one or more
    ``@pytest.mark.seed(...)`` markers and executes the corresponding
    seeders before the test body is run.

    Each seed marker defines a seed name in the form ``"module.variant"``,
    where:

    - ``module`` determines the seeder module to load
      (``<seed_modules>.<module>_seeder``)
    - ``variant`` identifies the specific seed scenario handled by the seeder

    Additional keyword arguments provided to the marker are forwarded to
    the seeder constructor.

    Seeders are resolved dynamically using the following conventions:

    - Seeder module: ``<apibean_seed_modules>.<prefix>_seeder``
    - Seeder class: ``<Prefix>Seeder``

    Seeders receive the application test container via ``apibean_container``
    and are responsible for creating the required test data.

    When multiple ``@pytest.mark.seed`` markers are present, they are
    executed in reverse declaration order, allowing later markers to
    override or extend earlier seeded data.

    This fixture is designed to be driven entirely by test markers.
    Applications may customize seeding behavior by:

    - Providing custom seeder modules
    - Overriding ``apibean_seed_modules`` to change discovery paths
    - Extending or replacing seeder implementations

    If no ``@pytest.mark.seed`` marker is present, this fixture performs
    no action.
    """

    markers = reversed(list(request.node.iter_markers("seed")))
    if not markers:
        yield
        return

    for marker in markers:
        # args[0] là seed name, kwargs chứa tham số bổ sung
        seed_name = marker.args[0] if marker.args else marker.kwargs.get("name")
        kwargs = marker.kwargs or {}

        if not seed_name:
            raise ValueError("Missing seed name in pytest.mark.seed()")

        try:
            prefix, variant = seed_name.split(".", 1)
        except ValueError as e:
            raise ValueError(f"Invalid seed name: '{seed_name}' (must be in format 'module.variant')") from e

        seeder_module_name = f"{apibean_seed_modules}.{prefix}_seeder"
        seeder_class_name = "".join(part.capitalize() for part in prefix.split("_")) + "Seeder"
        seeder_variant_class_name = (
            "".join(part.capitalize() for part in prefix.split("_"))
                + variant.capitalize()
                + "Seeder"
        )

        try:
            module = importlib.import_module(seeder_module_name)
            seeder_cls = getattr(module, seeder_class_name)
            if not callable(seeder_cls):
                seeder_cls = getattr(module, seeder_variant_class_name)
            seeder = seeder_cls(seed=seed_name, session=None, container=apibean_container, **kwargs)
            if hasattr(seeder, "run_in_anyio_worker") and getattr(seeder, "run_in_anyio_worker"):
                anyio.run(anyio.to_thread.run_sync, seeder.run)
            else:
                seeder.run()
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Couldn't load the class [{seeder_class_name}] for '{seed_name}': {e}") from e

    yield

@pytest.fixture(scope="function")
@concrete_fixture
def apibean_init_context(apibean_container):
    """
    Optional pre-reset hook executed before database reset.

    This fixture acts as an extension point that is executed immediately
    before ``apibean_reset_db`` in the Apibean test case lifecycle.

    By default, this fixture performs no action and simply yields control.
    Applications may override this fixture to implement custom logic such as:

    - Flushing external caches
    - Stopping background workers
    - Preparing external services
    - Collecting state or diagnostics before reset

    This fixture is intentionally non-autouse to allow applications to
    explicitly enable or customize it as needed.
    """
    test_service = apibean_container.test_service()
    test_service.force_rand_hash("Te$tPassw0rd")
    yield

@pytest.fixture(autouse=True)
def apibean_testcase_loop(request):
    """
    Orchestrate the Apibean test case lifecycle.

    This fixture is automatically executed for every test case to ensure
    a clean, predictable, and repeatable test environment. It enforces
    the following execution order:

    1. ``apibean_init_context`` – optional pre-reset hook
    2. ``apibean_reset_db`` – reset the persistent state (e.g. database)
    3. ``apibean_seed_data`` – seed the required test data

    The purpose of this fixture is to provide a standardized "test case loop"
    across the Apibean ecosystem, ensuring test isolation and eliminating
    order-dependent behavior.

    Applications may override any of the component fixtures above to customize
    reset or seeding behavior without modifying this orchestration fixture.
    """
    # 🔑 GUARD: execute only if @pytest.mark.seed is applied
    if request.node.get_closest_marker("seed") is None:
        yield
        return

    request.getfixturevalue("apibean_init_context")
    request.getfixturevalue("apibean_reset_db")
    request.getfixturevalue("apibean_seed_data")
    yield
