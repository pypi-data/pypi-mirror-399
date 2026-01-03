from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models import LogEvent


class Transport(ABC):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def is_running(self) -> bool: ...

    @abstractmethod
    def request(self, method: str, params: dict[str, Any] | None = None, *, timeout_s: float = 30) -> Any: ...

    @abstractmethod
    def notify(self, method: str, params: dict[str, Any] | None = None) -> None: ...

    @abstractmethod
    def stderr_tail(self, n: int = 200) -> list[str]: ...

    @abstractmethod
    def events_tail(self, n: int = 200) -> list[LogEvent]: ...

    @abstractmethod
    def server_info(self) -> dict[str, Any] | None: ...

