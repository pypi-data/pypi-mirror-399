from abc import ABC, abstractmethod


class BaseInspector(ABC):
    """
    Base class for all pytest-apibean inspectors.

    An inspector is responsible for:
    - inspecting application or pytest-apibean runtime state
    - collecting structured information
    - rendering human-readable output
    """

    name: str = "inspector"

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def inspect(self):
        """Perform inspection and collect data."""
        raise NotImplementedError


class BaseInspectionResult(ABC):
    @abstractmethod
    def render_lines(self) -> list[str]:
        """Render inspection result into displayable lines."""
        raise NotImplementedError
