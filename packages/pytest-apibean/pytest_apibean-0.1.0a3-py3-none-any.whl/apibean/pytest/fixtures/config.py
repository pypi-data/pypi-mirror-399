import pytest

from apibean.pytest.decorators import abstract_fixture
from apibean.pytest.decorators import concrete_fixture
from apibean.pytest.protocols.config import ApibeanTestConfig

@pytest.fixture(scope="session")
@abstract_fixture
def apibean_config() -> ApibeanTestConfig:
    """
    Provide apibean test configuration for the current test.

    This fixture returns an ApibeanTestConfig object that defines
    how the apibean testing lifecycle behaves, including database
    reset strategy, data seeding options, and optional test features.

    The concrete configuration must be supplied by the application
    or test environment.

    The application must provide an implementation of this fixture.
    """

@pytest.fixture(scope="session")
def apibean_safe_config(apibean_config) -> ApibeanTestConfig:
    if not isinstance(apibean_config, ApibeanTestConfig):
        pytest.skip(
            "apibean_config does not conform to ApibeanTestConfig protocol."
        )
    yield apibean_config
