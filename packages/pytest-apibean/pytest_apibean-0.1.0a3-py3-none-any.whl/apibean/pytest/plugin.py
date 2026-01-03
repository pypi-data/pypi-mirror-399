import pytest

from .cli import render, render_kv

from .fixtures.auth import *
from .fixtures.config import *
from .fixtures.container import *
from .fixtures.database import *
from .fixtures.seeds import *
from .hooks.seed_only import *
from .settings import settings

from .markers import APIBEAN_MARKERS

def pytest_load_initial_conftests(early_config, parser, args):
    # early_config._inicache
    #{
    #    'addopts': [],
    #    'python_files': ['test_*.py', '*_test.py'],
    #    'pythonpath': [],
    #    'required_plugins': [],
    #    'filterwarnings': []
    #}

    # Logging: write into inicache
    if settings.log_cli is not None:
        early_config._inicache["log_cli"] = settings.log_cli

    if settings.log_cli_level:
        early_config._inicache["log_cli_level"] = settings.log_cli_level


def pytest_configure(config):
    """
    Register pytest-apibean markers.
    """

    for desc in APIBEAN_MARKERS.values():
        if desc not in config.getini("markers"):
            config.addinivalue_line("markers", desc)

    # --- Warnings filter ---
    if settings.filterwarnings:
        # pytest stores ini values in _inicache
        existing = config._inicache.get("filterwarnings", [])
        config._inicache["filterwarnings"] = [
            *existing,
            *settings.filterwarnings,
        ]


def pytest_addoption(parser):
    group = parser.getgroup("apibean", "apibean testing options")

    group.addoption(
        "--apibean-show-config",
        action="store_true",
        help="Show apibean pytest configuration.",
    )

    group.addoption(
        "--apibean-show-container",
        action="store_true",
        help="Show apibean DI container information",
    )

    group.addoption(
        "--apibean-show-dbhandler",
        action="store_true",
        help="Show apibean database handler information",
    )

    group.addoption(
        "--apibean-list-fixtures",
        action="store",
        dest="apibean_list_fixtures",
        nargs="?",
        const="full",
        help=(
            "List fixtures provided by pytest-apibean.\n"
            "Usage:\n"
            "  --apibean-list-fixtures (full)\n"
            "  --apibean-list-fixtures=brief\n"
            "  --apibean-list-fixtures=short\n"
        ),
    )

    group.addoption(
        "--apibean-list-seeders",
        action="store_true",
        dest="apibean_list_seeders",
        help="List seeders discovered by pytest-apibean",
    )

    group.addoption(
        "--apibean-list-markers",
        action="store_true",
        default=False,
        help="List all pytest markers provided by pytest-apibean.",
    )

    group.addoption(
        "--apibean-seed-only",
        action="store_true",
        dest="apibean_seed_only",
        help=(
            "Run all apibean seed fixtures and markers, "
            "then stop without executing test functions."
        ),
    )


def pytest_cmdline_main(config):
    if config.getoption("--apibean-show-config"):
        render_kv(
            title="pytest-apibean configuration",
            items=settings.as_dict(),
            footer="Configuration loaded from pyproject.toml",
        )
        return pytest.ExitCode.OK

    if config.getoption("--apibean-show-container"):
        from .inspectors.container import show_container
        show_container(config)
        return pytest.ExitCode.OK

    if config.getoption("--apibean-show-dbhandler"):
        from .inspectors.dbhandler import show_dbhandler
        show_dbhandler(config)
        return pytest.ExitCode.OK

    if config.getoption("--apibean-list-fixtures"):
        mode = config.option.apibean_list_fixtures
        if mode not in ("short", "brief", "full"):
            raise pytest.UsageError(
                "--apibean-list-fixtures only supports: short | brief | full"
            )
        from .inspectors.fixtures import show_fixtures
        show_fixtures(config, mode=mode)
        return pytest.ExitCode.OK
    
    if config.getoption("--apibean-list-seeders"):
        mode = config.option.apibean_list_seeders
        from .inspectors.seeders import show_seeders
        show_seeders(config, mode=mode)
        return pytest.ExitCode.OK

    if config.getoption("--apibean-list-markers"):
        lines = [
            f"@pytest.mark.{desc}"
            for desc in sorted(APIBEAN_MARKERS.values())
        ]

        render(
            title="pytest-apibean markers",
            lines=lines,
            footer=f"{len(lines)} apibean marker(s) registered.",
        )

        return pytest.ExitCode.OK
