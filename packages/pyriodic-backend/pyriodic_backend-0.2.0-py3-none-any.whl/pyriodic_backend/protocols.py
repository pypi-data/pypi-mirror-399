from typing import Protocol

from .entities import RegisteredMethod


class BackendProtocol(Protocol):
    def record(self, method: RegisteredMethod):
        ...

    def get_minutes_since_last_run(self, method: RegisteredMethod) -> int | None:
        ...
