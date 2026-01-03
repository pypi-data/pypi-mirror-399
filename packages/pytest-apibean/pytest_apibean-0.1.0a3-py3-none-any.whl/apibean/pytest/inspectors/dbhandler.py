from typing import Optional
from dataclasses import dataclass

from apibean.pytest.cli import render
from apibean.pytest.inspectors.base import BaseInspector
from apibean.pytest.inspectors.base import BaseInspectionResult
from apibean.pytest.protocols.database import ApibeanTestDatabase
from apibean.pytest.protocols.database import is_apibean_dbhandler
from apibean.pytest.settings import settings


@dataclass
class DBHandlerInspectionResult:
    found: bool
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    attributes: Optional[list[str]] = None
    protocol: Optional[str] = None
    conformed_class_name: Optional[str] = None
    error: Optional[str] = None

    def render_lines(self):
        lines: list[str] = []

        if self.found:
            lines.extend([
                "✔ Status            OK",
                f"✔ Module            {self.module_path}",
                f"✔ Protocol          {self.protocol}",
                f"✔ Class             {self.class_name}",
            ])
            if self.attributes:
                lines.append("✔ Attributes:")
            for attr in self.attributes:
                lines.append(f"  - { attr }")
        else:
            lines.extend([
                 "✖ Status            NOT FOUND",
                f"✖ Module            {self.module_path}",
                f"✖ Declared class    {self.class_name}",
                f"✖ Detected class    {self.conformed_class_name}",
                f"✖ Reason            {self.error}",
                 "✖ Hint              Please configure dbhandler_module_path and dbhandler_class_name correctly",
            ])

        return lines


class DBHandlerInspector(BaseInspector):
    name = "DB-Handler"

    def __init__(self, dbhandler_module_path: str,
        dbhandler_class_name: str = "Database"
    ):
        self._module_path = dbhandler_module_path
        self._class_name = dbhandler_class_name

    def inspect(self) -> DBHandlerInspectionResult:
        try:
            module = __import__(self._module_path, fromlist=["*"])
        except ModuleNotFoundError as e:
            return DBHandlerInspectionResult(
                found=False,
                module_path=self._module_path,
                error=str(e),
            )

        db_cls = getattr(module, self._class_name, None)

        if db_cls is None:
            conformed_db_cls = next(
                obj
                for obj in module.__dict__.values()
                if is_apibean_dbhandler(obj)
            )
            conformed_class_name = conformed_db_cls.__name__ if conformed_db_cls is not None else None
            return DBHandlerInspectionResult(
                found=False,
                module_path=self._module_path,
                class_name=self._class_name,
                conformed_class_name=conformed_class_name,
                error=f"Module `{self._module_path}` does not provide class `{self._class_name}`",
            )

        attributes = [
            name
            for name in dir(db_cls)
            if not name.startswith("_")
        ]

        return DBHandlerInspectionResult(
            found=True,
            module_path=self._module_path,
            class_name=db_cls.__name__,
            attributes=attributes,
            protocol=ApibeanTestDatabase.__name__,
        )


def show_dbhandler(config):
    inspector = DBHandlerInspector(
        dbhandler_module_path=settings.dbhandler_module_path,
        dbhandler_class_name=settings.dbhandler_class_name
    )

    render(
        title = f"Apibean {inspector.name}",
        lines = inspector.inspect().render_lines(),
    )
