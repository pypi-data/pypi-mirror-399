"""Input validation helpers for TeamFlow Console App."""

from enum import Enum
from typing import TypeVar

from rich.console import Console

T = TypeVar("T", bound=Enum)


def validate_numbered_input(
    input_str: str,
    min_value: int,
    max_value: int,
    allow_empty: bool = False,
    default: int | None = None,
) -> int | None:
    """Validate a numbered menu selection.

    Args:
        input_str: The user input string
        min_value: Minimum valid value
        max_value: Maximum valid value
        allow_empty: Whether empty input is allowed
        default: Default value if empty input allowed

    Returns:
        The validated integer, or None if empty and allowed

    Raises:
        ValueError: If input is invalid
    """
    if not input_str.strip():
        if allow_empty and default is not None:
            return default
        raise ValueError("Input is required")

    try:
        value = int(input_str.strip())
    except ValueError:
        raise ValueError("Please enter a number")

    if value < min_value or value > max_value:
        raise ValueError(f"Please enter a number between {min_value} and {max_value}")

    return value


def validate_required_text(input_str: str, min_length: int = 1,
                          max_length: int = 200) -> str:
    """Validate required text input.

    Args:
        input_str: The user input string
        min_length: Minimum length (default: 1)
        max_length: Maximum length (default: 200)

    Returns:
        The validated and stripped text

    Raises:
        ValueError: If input is invalid
    """
    if not input_str.strip():
        raise ValueError("This field is required")

    stripped = input_str.strip()

    if len(stripped) < min_length:
        raise ValueError(f"Minimum length is {min_length} characters")

    if len(stripped) > max_length:
        raise ValueError(f"Maximum length is {max_length} characters")

    return stripped


def validate_optional_text(input_str: str, max_length: int = 1000) -> str | None:
    """Validate optional text input.

    Args:
        input_str: The user input string
        max_length: Maximum length (default: 1000)

    Returns:
        The validated and stripped text, or None if empty
    """
    if not input_str.strip():
        return None

    stripped = input_str.strip()

    if len(stripped) > max_length:
        raise ValueError(f"Maximum length is {max_length} characters")

    return stripped


def validate_enum_selection(
    input_str: str,
    enum_class: type[T],
    allow_empty: bool = False,
    default: T | None = None,
) -> T:
    """Validate an enum selection by number.

    Args:
        input_str: The user input string (number as string)
        enum_class: The Enum class to select from
        allow_empty: Whether empty input is allowed
        default: Default value if empty input allowed

    Returns:
        The selected enum value

    Raises:
        ValueError: If input is invalid
    """
    if not input_str.strip():
        if allow_empty and default is not None:
            return default
        raise ValueError("Selection is required")

    try:
        selection = int(input_str.strip())
    except ValueError:
        raise ValueError("Please enter a number")

    enum_values = list(enum_class)
    if selection < 1 or selection > len(enum_values):
        raise ValueError(f"Please enter a number between 1 and {len(enum_values)}")

    return enum_values[selection - 1]


def confirm_action(prompt: str, default: bool = True) -> bool:
    """Prompt for yes/no confirmation.

    Args:
        prompt: The confirmation prompt
        default: Default value if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    default_str = "Y" if default else "y"
    option_str = "Y/n" if default else "y/N"

    full_prompt = f"{prompt} [{option_str}]: "

    # In the actual CLI, this would use input()
    # For now, return the default
    return default


def get_enum_options(enum_class: type[Enum]) -> list[str]:
    """Get a list of enum options for display.

    Args:
        enum_class: The Enum class

    Returns:
        List of formatted option strings
    """
    return [f"[{i}] {value.value}" for i, value in enumerate(enum_class, start=1)]
