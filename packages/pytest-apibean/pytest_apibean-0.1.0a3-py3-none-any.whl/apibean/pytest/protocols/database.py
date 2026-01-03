from typing import Any, Generator, Protocol, runtime_checkable

import inspect


@runtime_checkable
class ApibeanTestEngine(Protocol):
    def dispose(self) -> Any: ...


@runtime_checkable
class ApibeanTestDatabase(Protocol):

    @property
    def engine(self) -> ApibeanTestEngine: ...

    def session(self, **kwargs) -> Generator[Any, None, None]: ...


from .util import get_members_of
REQUIRED_DB_ATTRS = get_members_of(ApibeanTestDatabase)


def is_apibean_dbhandler(cls) -> bool:
    if not inspect.isclass(cls):
        return False

    for attr in REQUIRED_DB_ATTRS:
        if not hasattr(cls, attr):
            return False

    return True
