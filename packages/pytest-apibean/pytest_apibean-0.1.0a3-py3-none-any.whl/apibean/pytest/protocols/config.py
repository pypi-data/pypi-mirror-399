from typing import Protocol, runtime_checkable

@runtime_checkable
class ApibeanTestConfig(Protocol):
    DATABASE_URI: str
    DB_ECHO: bool

    ROOT_USER_EMAIL: str
    ROOT_USER_PASSWORD: str

    SYNC_USER_EMAIL: str
    SYNC_USER_PASSWORD: str
