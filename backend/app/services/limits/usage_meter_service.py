from __future__ import annotations

from collections import defaultdict
from datetime import date


class UsageMeterService:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str, date], int] = defaultdict(int)

    def increment_usage(self, user_id: str, feature: str) -> int:
        key = (user_id, feature, date.today())
        self._usage[key] += 1
        return self._usage[key]

    def get_usage(self, user_id: str, feature: str) -> int:
        return self._usage[(user_id, feature, date.today())]
