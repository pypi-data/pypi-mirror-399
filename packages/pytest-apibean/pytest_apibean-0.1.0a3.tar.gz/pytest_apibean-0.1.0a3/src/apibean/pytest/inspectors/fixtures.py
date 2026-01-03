import pkgutil
import importlib

from dataclasses import dataclass

from apibean.pytest.cli import render, row
from apibean.pytest.inspectors.base import BaseInspector
from apibean.pytest.inspectors.base import BaseInspectionResult
from apibean.pytest.renderers import render_docstring


@dataclass
class FixturesInspectionResult:
    def __init__(self, functions: list, mode: str | None = None):
        self._functions = functions
        self._mode = mode or "full"

    def render_lines(self):
        lines: list[str] = []

        for func in self._functions:
            fx = getattr(func, "_fixture_function_marker", None)

            scope = fx.scope if fx else "unknown"
            autouse = "yes" if fx and fx.autouse else "no"
            is_abstract = hasattr(func, "__apibean_abstract_fixture__")

            icon = "⚠" if is_abstract else "✔"
            kind = "abstract" if is_abstract else "concrete"

            if self._mode == "short":
                lines.append(f"{icon} [{scope:>8}] {func.__name__}")
                continue

            if self._mode == "brief" or self._mode == "full":
                lines.append(f"{icon} {func.__name__}")
                lines.append(row(" ", "scope", scope))
                lines.append(row(" ", "autouse", autouse))
                lines.append(row(" ", "type", kind))

            if self._mode == "brief":
                if func.__doc__:
                    doc = func.__doc__.strip().splitlines()[0]
                    lines.append(row(" ", "doc", doc))
                lines.append("")

            if self._mode == "full":
                if func.__doc__:
                    lines.append(row(" ", "doc", ""))  # header line
                    doc_lines = render_docstring(func.__doc__)
                    lines.extend(doc_lines)
                lines.append("")

        return lines


class FixturesInspector(BaseInspector):
    name = "Fixtures"

    def __init__(self, mode: str):
        self._mode = mode

    def inspect(self) -> FixturesInspectionResult:
        return FixturesInspectionResult(
            functions = self._classify_apibean_fixture_functions(),
            mode = self._mode,
        )

    def _iter_apibean_fixture_functions(self):
        import apibean.pytest.fixtures as fixtures_pkg

        for _, modname, _ in pkgutil.iter_modules(fixtures_pkg.__path__):
            module = importlib.import_module(f"{fixtures_pkg.__name__}.{modname}")
            for name, obj in vars(module).items():
                if hasattr(obj, "__apibean_abstract_fixture__"):
                    yield obj, "abstract"
                if hasattr(obj, "__apibean_concrete_fixture__"):
                    yield obj, "concrete"


    def _classify_apibean_fixture_functions(self):
        fixtures = {"abstract": [], "concrete": []}
        for func, func_type in self._iter_apibean_fixture_functions():
            fixtures[func_type].append(func)
        return fixtures["abstract"] + sorted(fixtures["concrete"], key=lambda f: f.__name__)


def show_fixtures(config, mode: str | None = None):
    inspector = FixturesInspector(mode=mode)
    render(
        title = f"Apibean {inspector.name}",
        lines = inspector.inspect().render_lines(),
    )
