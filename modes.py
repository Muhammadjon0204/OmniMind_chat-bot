from collections import defaultdict


class UserModes:
    def __init__(self):
        self._modes = defaultdict(lambda: "normal")
        self._persona = defaultdict(str)
        self._waiting_persona = defaultdict(lambda: False)

    def set_mode(self, user_id: int, mode: str):
        self._modes[user_id] = mode

    def get_mode(self, user_id: int) -> str:
        return self._modes[user_id]

    def start_persona_setup(self, user_id: int):
        self._waiting_persona[user_id] = True

    def is_waiting_persona(self, user_id: int) -> bool:
        return self._waiting_persona[user_id]

    def set_persona(self, user_id: int, persona: str):
        self._persona[user_id] = persona
        self._waiting_persona[user_id] = False
        self._modes[user_id] = "custom"

    def get_persona(self, user_id: int) -> str:
        return self._persona[user_id]

    def clear_persona(self, user_id: int):
        self._persona[user_id] = ""
        self._waiting_persona[user_id] = False
        self._modes[user_id] = "normal"