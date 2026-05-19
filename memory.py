from collections import defaultdict
from typing import Dict, List


Message = Dict[str, str]


class MemoryStorage:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self._storage: Dict[int, List[Message]] = defaultdict(list)

    def add_message(self, user_id: int, role: str, content: str) -> None:
        self._storage[user_id].append({
            "role": role,
            "content": content
        })

        if len(self._storage[user_id]) > self.max_messages:
            self._storage[user_id] = self._storage[user_id][-self.max_messages:]

    def get_history(self, user_id: int) -> List[Message]:
        return self._storage[user_id]

    def clear_history(self, user_id: int) -> None:
        self._storage[user_id].clear()