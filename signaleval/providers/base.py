from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def predict(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Given a dataset row, return a prediction dict."""
        ...

    def close(self):
        pass
