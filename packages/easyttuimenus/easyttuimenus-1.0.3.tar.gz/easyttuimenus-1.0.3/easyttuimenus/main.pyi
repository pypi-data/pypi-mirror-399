from typing import Any

BREAK_HARD: str
BREAK_SOFT: str
INPUT_INDICATOR: str
SELECTED_INDICATOR: str

def int_menu(prompt: str, min: int, max: int) -> int: ...
def list_menu(prompt: str, options: list[Any]) -> int: ...
def multiple_choice_menu(prompt: str, options: list[Any]) -> list[int]: ...
