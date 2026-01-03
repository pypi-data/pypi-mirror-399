import importlib
from dataclasses import dataclass
from typing import List, Optional

from apibean.pytest.cli import render
from apibean.pytest.inspectors.base import BaseInspector
from apibean.pytest.inspectors.base import BaseInspectionResult
from apibean.pytest.settings import settings


@dataclass
class ContainerInspectionResult(BaseInspectionResult):
    found: bool
    module_path: str
    class_name: Optional[str] = None
    container_type: Optional[str] = None
    providers: Optional[List[str]] = None
    error: Optional[str] = None

    def render_lines(self):
        if not self.found:
            return [
                f"container module : {self.module_path}",
                "status           : NOT FOUND",
                "",
                f"reason           : {self.error}",
                "",
                "hint:",
                "  - configure [tool.apibean.pytest.options].container_module_path",
                "  - or provide an application Container",
            ],

        lines = [
            f"container module : {self.module_path}",
            f"container class  : {self.class_name}",
            f"container type   : {self.container_type}",
            "",
            "providers:",
        ]

        for name in self.providers:
            lines.append(f"  - {name}")

        return lines


class ContainerInspector(BaseInspector):
    name = "Container"

    def __init__(self, container_module_path: str,
        container_class_name: str = "Container"
    ):
        self._module_path = container_module_path
        self._class_name = container_class_name

    def inspect(self) -> ContainerInspectionResult:
        try:
            module = importlib.import_module(self._module_path)
        except ModuleNotFoundError as e:
            return ContainerInspectionResult(
                found=False,
                module_path=self._module_path,
                error=str(e),
            )

        # find Container class
        container_cls = getattr(module, self._class_name, None)
        if container_cls is None:
            return ContainerInspectionResult(
                found=False,
                module_path=self._module_path,
                error=f"Module does not export `{self._class_name}`",
            )

        providers = []
        if hasattr(container_cls, "providers"):
            providers = sorted(container_cls.providers.keys())

        return ContainerInspectionResult(
            found=True,
            module_path=self._module_path,
            class_name=container_cls.__name__,
            container_type=container_cls.__class__.__name__,
            providers=providers,
        )


def show_container(config):
    inspector = ContainerInspector(
        settings.container_module_path,
        container_class_name=settings.container_class_name
    )

    render(
        title = f"Apibean :: {inspector.name}",
        lines = inspector.inspect().render_lines()
    )
