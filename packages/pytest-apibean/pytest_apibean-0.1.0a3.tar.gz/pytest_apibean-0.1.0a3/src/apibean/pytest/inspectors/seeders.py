import importlib
import inspect
import pkgutil

from dataclasses import dataclass

from apibean.pytest.cli import render
from apibean.pytest.helpers import pascal_to_snake, snake_to_pascal
from apibean.pytest.inspectors.base import BaseInspector, BaseInspectionResult
from apibean.pytest.settings import settings


@dataclass
class SeederInfo:
    seed_name: str
    module: str
    class_name: str
    doc: str | None


class SeederInspectionResult(BaseInspectionResult):
    def __init__(self, module_path: str | None = None, seeders: list[SeederInfo] = []):
        self.module_path = module_path
        self.seeders = seeders

    def render_lines(self) -> list[str]:
        if not self.seeders:
            return [
                "⚠ No seeders found",
                f"  Seed module path: {self.module_path}",
            ]

        lines: list[str] = []
        for seeder in self.seeders:
            lines.append(f"✔ {seeder.seed_name}")
            lines.append(f"    Module : {seeder.module}")
            lines.append(f"    Class  : {seeder.class_name}")
            if seeder.doc:
                lines.append("    Doc    :")
                for line in seeder.doc.splitlines():
                    lines.append(f"      {line}")
            lines.append("")
        return lines


class SeederInspector(BaseInspector):
    """
    Inspect seeders discoverable by pytest-apibean.

    Seeders are discovered using the following conventions:
    - base module path provided by ``apibean_seed_modules`` fixture
    - module name: ``<prefix>_seeder``
    - class name: ``<Prefix>Seeder``
    """

    name = "seeders"

    def __init__(self, config):
        super().__init__(config)


    def inspect(self):
        module_path = settings.seed_modules
        return SeederInspectionResult(
            module_path = module_path,
            seeders = self._discover_seeders(module_path)
        )


    def _discover_seeders(self, base_module_path: str) -> list[SeederInfo]:
        try:
            base_module = importlib.import_module(base_module_path)
        except ImportError:
            return []

        if not hasattr(base_module, "__path__"):
            return []

        results: list[SeederInfo] = []
        loaded_seeders = []
        for modinfo in pkgutil.iter_modules(base_module.__path__):
            if not modinfo.name.endswith("_seeder"):
                continue

            module_name = f"{base_module_path}.{modinfo.name}"

            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue

            prefix = modinfo.name.removesuffix("_seeder")

            for obj in module.__dict__.values():
                if not inspect.isclass(obj):
                    continue
                if not obj.__name__.endswith("Seeder"):
                    continue
                if obj.__name__ not in loaded_seeders:
                    loaded_seeders.append(obj.__name__)
                else:
                    continue

                seed_name = self._extract_seed_name(prefix, class_name=obj.__name__)

                results.append(
                    SeederInfo(
                        seed_name=seed_name,
                        module=module_name,
                        class_name=obj.__name__,
                        doc=inspect.getdoc(obj),
                    )
                )

        return sorted(results, key=lambda s: s.seed_name)


    def _extract_seed_name(self, prefix, class_name: str | None = None):
        prefix_in_pascal = snake_to_pascal(prefix)
        variant_with_seeder = class_name.removeprefix(prefix_in_pascal)
        variant_in_pascal = variant_with_seeder.removesuffix("Seeder")
        variant_in_snake = pascal_to_snake(variant_in_pascal)
        if variant_in_snake:
            return f"{prefix}.{variant_in_snake}"
        return f"{prefix}.*"


def show_seeders(config, mode: str | None = None):
    inspector = SeederInspector(config)
    render(
        title = f"Apibean {inspector.name}",
        lines = inspector.inspect().render_lines(),
    )
