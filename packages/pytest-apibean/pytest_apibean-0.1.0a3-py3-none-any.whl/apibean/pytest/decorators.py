from functools import wraps

import pytest

def abstract_fixture(func):
    """
    Mark a pytest fixture as an abstract (contract) fixture.

    This decorator designates a fixture as a required contract that must be
    implemented by the application under test. It is intended for core
    infrastructure fixtures that pytest-apibean depends on but cannot
    implement itself.

    When an abstract fixture is not overridden by the application, accessing
    it will immediately skip the test session with a clear and explicit
    message indicating that the fixture is missing.

    The decorator also attaches metadata to the wrapped function via the
    ``__apibean_abstract_fixture__`` attribute, allowing pytest-apibean to
    programmatically discover and list abstract fixtures (for example, via
    a custom command-line option).

    Typical use cases include fixtures such as:

    - ``apibean_config`` – application test configuration
    - ``apibean_container`` – dependency injection container
    - ``apibean_db`` – application database backend

    This decorator should only be applied to fixtures that are expected to be
    provided by the application and must not have a default implementation.
    """

    func.__apibean_abstract_fixture__ = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        pytest.skip(f"{func.__name__} fixture not provided by application")
        return func(*args, **kwargs)
    return wrapper


def concrete_fixture(func):
    """
    Decorator that marks a pytest fixture as a concrete apibean fixture.

    This decorator attaches the marker attribute
    ``__apibean_concrete_fixture__ = True`` to the decorated function.
    The attribute is used by apibean tooling (e.g. fixture inspection,
    listing, or documentation commands) to distinguish concrete fixtures
    from abstract, helper, or internal fixtures.

    The decorator does not alter the behavior or signature of the
    decorated function; it only adds metadata for introspection.

    Args:
        func (Callable):
            The fixture function to be marked as a concrete fixture.

    Returns:
        Callable:
            The same function with the ``__apibean_concrete_fixture__``
            attribute attached.

    Example:
        @pytest.fixture
        @concrete_fixture
        def login(apibean_container):
            ...

    Notes:
        - This decorator is intended for use with pytest fixtures.
        - Consumers should check for the presence of the
          ``__apibean_concrete_fixture__`` attribute rather than relying
          on naming conventions.
    """
    func.__apibean_concrete_fixture__ = True
    return func
