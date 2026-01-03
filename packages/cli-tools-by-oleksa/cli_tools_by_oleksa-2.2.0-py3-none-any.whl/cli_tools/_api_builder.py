import re
from datetime import datetime
from typing import Callable, Any, TypedDict

from .cli import get_input
from .patterns import (
    INT,
    FLOAT,
    NUMBER,
    USERNAME,
    EMAIL,
    HEX_RGB,
    DATE_DMY,
    DATE_YMD,
    TIME_24H,
)


class GeneratorParams(TypedDict):
    pattern: re.Pattern[Any]
    converter: Callable[[str], Any]


INPUT_GENERATORS: dict[str, GeneratorParams] = {
    "get_int": {"pattern": INT, "converter": int},
    "get_float": {"pattern": FLOAT, "converter": float},
    "get_number": {"pattern": NUMBER, "converter": float},
    "get_username": {"pattern": USERNAME, "converter": str},
    "get_email": {"pattern": EMAIL, "converter": str},
    "get_hex_rgb": {"pattern": HEX_RGB, "converter": str},
    "get_date_dmy": {
        "pattern": DATE_DMY,
        "converter": lambda x: datetime.strptime(x, "%d.%m.%Y").date(),
    },
    "get_date_ymd": {
        "pattern": DATE_YMD,
        "converter": lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
    },
    "get_time": {
        "pattern": TIME_24H,
        "converter": lambda x: datetime.strptime(x, "%H:%M").time(),
    },
}


def _generate_input_wrapper(
        name: str,
        pattern: re.Pattern,
        converter: Callable[[str], Any]
) -> Callable[..., Any]:
    """
    Generates a specialized input function based on pre-defined validation rules.

    This function creates a clean wrapper around the core 'get_input' function,
    injecting specific 'pattern' and 'converter' arguments to enforce a strict
    data type (e.g., integer, email, date).

    :param name: The desired name for the generated function (e.g., 'get_int').
    :param pattern: The compiled regex pattern to enforce for the specific data type.
    :param converter: The function used to convert the validated input string
                      into the target type.
    :returns: A new specialized input function (Callable[..., Any]).
    """

    def specialized_input_func(prompt: str = "",
                               validator: Callable[[str], bool] = lambda x: True,
                               default: Any = None,
                               *,
                               retry: bool = True,
                               if_invalid: str = f'Invalid {name.replace("get_", "").upper()} format!',
                               on_keyboard_interrupt: Callable | None = None) -> Any:
        return get_input(prompt=prompt,
                         pattern=pattern,
                         validator=validator,
                         converter=converter,
                         default=default,
                         retry=retry,
                         if_invalid=if_invalid,
                         on_keyboard_interrupt=on_keyboard_interrupt)

    specialized_input_func.__name__ = name
    converter_name = converter.__name__ if hasattr(converter, "__name__") else "lambda"
    specialized_input_func.__doc__ = (
        f"Gets user input and validates it as {name.replace('get_', '').upper()} data type. "
        f"Wrapper around get_input with pattern='{pattern.pattern}' and converter='{converter_name}'."
    )

    return specialized_input_func


def _build_input_api() -> dict[str, Callable]:
    """
    Dynamically generates all specialized input functions (get_int, get_email, etc.)
    defined in INPUT_GENERATORS.

    This is the entry point for generating input extensions for the module.

    :returns: A dictionary mapping function names (str) to the generated function objects (Callable).
    """
    generated = {}
    for name, params in INPUT_GENERATORS.items():
        func = _generate_input_wrapper(name, params["pattern"], params["converter"])
        generated[name] = func
    return generated
