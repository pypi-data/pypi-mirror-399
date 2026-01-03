from contextlib import contextmanager

import logging
import logging.config

@contextmanager
def silence_alembic_migration_logs():
    """
    Context manager that temporarily silences Alembic migration logs.

    This utility suppresses verbose Alembic migration output by patching
    `logging.config.fileConfig` so that, after Alembic initializes its
    logging configuration, the log level of the
    ``alembic.runtime.migration`` logger is forced to ``WARNING``.

    The original ``logging.config.fileConfig`` function is restored when
    exiting the context, ensuring that logging behavior outside of the
    context remains unchanged.

    This is particularly useful in test environments or automated
    migrations where Alembic's INFO-level logs would otherwise clutter
    the output.

    Yields:
        None

    Example:
        with silence_alembic_migration_logs():
            command.upgrade(alembic_cfg, "head")

    Notes:
        - The patch only affects logging configuration performed inside
          the context block.
        - This context manager is intended for short-lived use and should
          not be applied globally.
    """
    original_fileconfig = logging.config.fileConfig

    def patched_fileconfig(*args, **kwargs):
        original_fileconfig(*args, **kwargs)
        logging.getLogger("alembic.runtime.migration").setLevel(logging.WARNING)

    logging.config.fileConfig = patched_fileconfig
    try:
        yield
    finally:
        logging.config.fileConfig = original_fileconfig


#------------------------------------------------------------------------------

import re

def snake_to_pascal(s: str) -> str:
    """Convert a snake_case string to PascalCase.

    Args:
        s: Input string in snake_case format.

    Returns:
        The converted string in PascalCase format.

    Examples:
        >>> snake_to_pascal("user_name")
        'UserName'
        >>> snake_to_pascal("api_key")
        'ApiKey'
    """
    return "".join(p.capitalize() for p in s.split("_"))


def pascal_to_snake(s: str) -> str:
    """Convert a PascalCase string to snake_case.

    The function also supports camelCase input and will insert underscores
    between word boundaries before converting the result to lowercase.

    Args:
        s: Input string in PascalCase or camelCase format.

    Returns:
        The converted string in snake_case format.

    Examples:
        >>> pascal_to_snake("UserName")
        'user_name'
        >>> pascal_to_snake("HTTPServerError")
        'http_server_error'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()
