import json
from datetime import datetime, timezone
from pathlib import Path

from .entities import RegisteredMethod


class InMemoryJSONBackend:
    """only for use with testing"""

    def __init__(self):
        self.db: dict[str, datetime] = {}

    def record(self, method: RegisteredMethod):
        self.db[method.signature()] = datetime.now(timezone.utc)

    def get_last_run_time(self, method: RegisteredMethod) -> datetime | None:
        return self.db.get(method.signature())

    def get_minutes_since_last_run(self, method: RegisteredMethod) -> int | None:
        last_run_time = self.get_last_run_time(method)
        if last_run_time is None:
            return None
        return int((datetime.now(timezone.utc) - last_run_time).total_seconds())


class FileJSONBackend:
    def __init__(self, file_path: str | None = None):
        if not file_path:
            self.file_path = Path(__file__).parent / "db.json"
        else:
            self.file_path = Path(file_path)

    def record(self, method: RegisteredMethod):
        db = self._load_db()
        db[method.signature()] = datetime.now(timezone.utc).isoformat()
        self._write_db(db)

    def _get_last_run_time(self, method: RegisteredMethod) -> datetime | None:
        db = self._load_db()
        last_run_time = db.get(method.signature())
        return datetime.fromisoformat(last_run_time) if last_run_time else None

    def get_minutes_since_last_run(self, method: RegisteredMethod) -> int | None:
        last_run_time = self._get_last_run_time(method)
        if last_run_time is None:
            return None
        return int((datetime.now(timezone.utc) - last_run_time).total_seconds() // 60)

    def _load_db(self) -> dict:
        db_file = Path(self.file_path)
        if db_file.exists():
            with db_file.open("r") as f:
                return json.load(f)
        else:
            return {}

    def _write_db(self, db: dict):
        with open(self.file_path, "w") as f:
            json.dump(db, f)
