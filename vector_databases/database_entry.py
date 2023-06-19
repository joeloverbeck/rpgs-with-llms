from datetime import datetime
from typing import Dict


class DatabaseEntry:
    def __init__(self, index: int, data: Dict[str, any]):
        self._index = index
        self._data = data

    def get_index(self) -> int:
        return self._index

    def get_recency(self) -> float:
        return self._data.get("recency", 0.0)

    def get_importance(self) -> float:
        return self._data.get("importance", 0.0)

    def get_most_recent_access_timestamp(self) -> datetime:
        most_recent_access_timestamp = self._data.get(
            "most_recent_access_timestamp", datetime.now().isoformat()
        )
        if isinstance(most_recent_access_timestamp, datetime):
            return most_recent_access_timestamp

        return datetime.fromisoformat(most_recent_access_timestamp)

    def get_description(self) -> str:
        return self._data.get("description", "")
