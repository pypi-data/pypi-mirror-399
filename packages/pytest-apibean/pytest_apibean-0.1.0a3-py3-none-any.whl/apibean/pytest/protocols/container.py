from typing import Protocol, runtime_checkable
from dependency_injector.providers import Provider


@runtime_checkable
class ApibeanTestContainer(Protocol):
    """
    Minimal contract pytest-apibean needs
    """
    db: Provider

    auth_service: Provider
    test_service: Provider

    def wire(self, modules=None) -> None: ...
    def unwire(self) -> None: ...
