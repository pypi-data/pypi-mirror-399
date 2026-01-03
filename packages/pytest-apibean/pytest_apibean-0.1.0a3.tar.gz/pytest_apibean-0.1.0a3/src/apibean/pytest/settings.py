from __future__ import annotations
from typing import List, Optional

import os
import tomllib
from pathlib import Path
from dataclasses import dataclass, asdict

TOOL_APIBEAN_PYTEST_OPTIONS = "tool.apibean.pytest.options"


@dataclass(slots=True)
class ApibeanOptions:
    base_url: str = "http://localhost:8000"
    login_path: str = "/auth/login"
    username: str = "admin"
    password: str = "admin"
    timeout: float = 10.0
    auto_login: bool = True

    dbhandler_class_name: str = "Database"
    dbhandler_module_path: str = "app.core.database"

    container_class_name: str = "Container"
    container_module_path: str = "app.core.container"

    seed_modules: str = "tests.seeders"
    seed_marker: str = "seed"   # @pytest.mark.seed(...)
    seed_mode: str = "auto"     # auto | explicit | off

    log_cli: Optional[bool] = True
    log_cli_level: Optional[str] = "DEBUG"
    filterwarnings: List[str] | None = (
        "ignore::Warning",
        "ignore::DeprecationWarning",
    )

    def as_dict(self) -> dict:
        return asdict(self)


_DEFAULTS = ApibeanOptions()


def _load_pyproject_options() -> dict:
    """
    Load [tool.apibean.pytest.options] từ pyproject.toml
    """
    for path in (Path.cwd(), *Path.cwd().parents):
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            return (
                data
                .get("tool", {})
                .get("apibean", {})
                .get("pytest", {})
                .get("options", {})
            )
    return {}


def load_settings() -> ApibeanOptions:
    defaults = _DEFAULTS
    opts = _load_pyproject_options()

    return ApibeanOptions(
        base_url=opts.get(
            "base_url",
            os.getenv("APIBEAN_BASE_URL", defaults.base_url),
        ),
        login_path=opts.get(
            "login_path",
            os.getenv("APIBEAN_LOGIN_PATH", defaults.login_path),
        ),
        username=opts.get(
            "username",
            os.getenv("APIBEAN_USERNAME", defaults.username),
        ),
        password=opts.get(
            "password",
            os.getenv("APIBEAN_PASSWORD", defaults.password),
        ),
        timeout=float(
            opts.get(
                "timeout",
                os.getenv("APIBEAN_TIMEOUT", str(defaults.timeout)),
            )
        ),
        auto_login=bool(opts.get("auto_login", defaults.auto_login)),

        container_class_name=opts.get(
            "container_class_name",
            os.getenv("APIBEAN_CONTAINER_CLASS_NAME", defaults.container_class_name),
        ),
        container_module_path=opts.get(
            "container_module_path",
            os.getenv("APIBEAN_CONTAINER_MODULE_PATH", defaults.container_module_path),
        ),

        dbhandler_class_name=opts.get(
            "dbhandler_class_name",
            os.getenv("APIBEAN_DBHANDLER_CLASS_NAME", defaults.dbhandler_class_name),
        ),
        dbhandler_module_path=opts.get(
            "dbhandler_module_path",
            os.getenv("APIBEAN_DBHANDLER_MODULE_PATH", defaults.dbhandler_module_path),
        ),

        seed_modules=opts.get(
            "seed_modules",
            os.getenv("APIBEAN_SEED_MODULES", defaults.seed_modules),
        ),
        seed_marker=opts.get(
            "seed_marker",
            os.getenv("APIBEAN_SEED_MARKER", defaults.seed_marker),
        ),

        log_cli=opts.get("log_cli", defaults.log_cli),
        log_cli_level=opts.get("log_cli_level", defaults.log_cli_level),
        filterwarnings=opts.get("filterwarnings", defaults.filterwarnings),
    )


settings = load_settings()
