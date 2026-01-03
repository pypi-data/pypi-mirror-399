from os import system, name
from typing import Callable, List, Any

BREAK_HARD = "=============================="
BREAK_SOFT = "------------------------------"
INPUT_INDICATOR = ":: "
SELECTED_INDICATOR = "* "
TYPE_ERROR_MESSEGE: Callable[[List[Any]], str] = lambda options: f"All options must support string representation. Options passed: {options}"

def _display(prompt: str, body_text: str) -> int | ValueError:
    system("cls") if name == "nt" else system("clear")
    print(f"{BREAK_HARD}\n{prompt}\n{BREAK_SOFT}\n{body_text}\n{BREAK_HARD}")
    try:
        return int(input(INPUT_INDICATOR))
    except ValueError as e:
        return e

def _menu(prompt: str, body_text: str, validate: Callable[[int], tuple[bool, str]]) -> int:
    while True:
        response = _display(prompt, body_text)
        if type(response) is int:
            is_valid, err_mseg = validate(response)
            if is_valid:
                return response
            prompt = f"{prompt}\n{err_mseg}"
        if type(response) is ValueError: 
            prompt = f"{prompt}\nPlease only enter whole numbers"

def int_menu(prompt: str, min: int, max: int) -> int:
    validate: Callable[[int], tuple[bool, str]] = lambda x: (
        min <= x <= max,
        f"Response is out of range. Please try again."
    )
    body_text = f"Please enter a number between {min} and {max}."
    return _menu(prompt, body_text, validate)

def list_menu(prompt: str, options: List[Any]) -> int:
    validate: Callable[[int], tuple[bool, str]] = lambda x: (
        0 <= x < len(options),
        f"Response is not in the available options. Please try another."
    )
    body_text = "\n".join([f"{i}: {options[i]}" for i in range(len(options))])
    return _menu(prompt, body_text, validate)

def multiple_choice_menu(prompt: str, options: List[Any]) -> list[int]:
    """A wrapper for `list_menu()` that adds multiple-choice support."""
    options = [str(o) for o in options]
    options.insert(0, "Done")
    selected: list[int] = []
    while True:
        choice = list_menu(prompt, options)
        if choice == 0:
            return selected
        if options[choice].startswith(SELECTED_INDICATOR):
            options[choice] = options[choice][2:]
            selected.remove(choice)
        else:
            options[choice] = f"{SELECTED_INDICATOR}{options[choice]}"
            selected.append(choice)
