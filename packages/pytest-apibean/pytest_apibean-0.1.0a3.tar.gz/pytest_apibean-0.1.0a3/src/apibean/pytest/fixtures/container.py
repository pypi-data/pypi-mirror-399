import importlib
import pytest
from dependency_injector import providers

from apibean.pytest.decorators import concrete_fixture
from apibean.pytest.protocols.container import ApibeanTestContainer
from apibean.pytest.settings import settings

@pytest.fixture(scope="session")
@concrete_fixture
def apibean_container(apibean_db):
    """
    Provide the application test container.

    This fixture attempts to automatically load the application's dependency
    container using the ``container_module_path`` option defined under
    ``[tool.apibean.pytest.options]`` in ``pyproject.toml``.

    By convention, the default container module path is
    ``"app.core.container"``. The module is expected to expose a ``Container``
    object compatible with ``dependency-injector``.

    If the container module cannot be imported or does not define a valid
    ``Container``, the test session will be skipped with a clear message
    instructing the application to either fix the configuration or provide
    its own ``apibean_container`` fixture.
    """

    container_class_name = (
        settings.container_class_name
        if hasattr(settings, "container_class_name")
        else "Container"
    )

    container_module_path = (
        settings.container_module_path
        if hasattr(settings, "container_module_path")
        else "app.core.container"
    )

    try:
        module = importlib.import_module(container_module_path)
    except ImportError as e:
        pytest.skip(
            f"Cannot import container module '{container_module_path}': {e}. "
            "Configure [tool.apibean.pytest.options].container_module_path "
            "or provide an explicit apibean_container fixture."
        )

    Container = getattr(module, container_class_name, None)
    if Container is None:
        pytest.skip(
            f"Module '{container_module_path}' does not define '{container_class_name}'. "
            "Configure [tool.apibean.pytest.options].container_module_path "
            "and [tool.apibean.pytest.options].container_class_name "
            "or provide an explicit apibean_container fixture."
        )

    from ..wrappers.container import ServiceWrappingMeta

    class MetaTestContainer(
        Container,
        metaclass=ServiceWrappingMeta,
        injected_func_name="_inject_api_invoker",
    ):
        """
        Test-specific container that wraps service providers to inject
        test-time collaborators such as an API invoker.
        """

        api_invoker = providers.Object(None)

        @staticmethod
        def _inject_api_invoker(service, api_invoker):
            service.api_invoker = api_invoker
            return service

    container = MetaTestContainer()

    if not isinstance(container, ApibeanTestContainer):
        pytest.skip(
            f"Container '{container_class_name}' does not conform to "
            "ApibeanTestContainer protocol "
            "(required: db property, auth_service property, wire() and unwire() methods)."
        )

    # Override database provider with test database
    if apibean_db is not None:
        container.db.override(apibean_db)

    yield container

    container.unwire()
