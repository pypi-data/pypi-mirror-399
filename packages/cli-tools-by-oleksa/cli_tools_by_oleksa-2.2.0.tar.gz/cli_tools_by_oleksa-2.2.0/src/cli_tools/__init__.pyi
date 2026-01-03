import re
from typing import Callable, Any, Iterable, Type
from datetime import date, time
from contextlib import AbstractContextManager
from .cli import ProgressBar


class ValidationError(Exception): ...
class ConversionError(Exception): ...
class APIError(Exception): ...


def safe_run(debug: bool = False, exit_on_error: bool = True) -> AbstractContextManager[]: ...
def try_until_ok(
    func: Callable[..., Any],
    *args: Any,
    exceptions: tuple[Type[BaseException], ...] | Type[BaseException] = Exception,
    on_exception: str | Callable[[BaseException], Any] | None = None,
    on_keyboard_interrupt: Callable | None = None,
    **kwargs: Any,
) -> Any: ...

def format_iterable(
    iterable: Iterable[Any],
    item_pattern: str = "{}",
    join_by: str = "\n",
    start: str = "",
    end: str = "",
) -> str: ...

def format_table(
    iterable: Iterable[Iterable[Any]],
    row_pattern: str = "{}: {}",
    join_by: str = "\n",
    start: str = "",
    end: str = "",
) -> str: ...

def safe_int(string: str) -> int | None: ...
def safe_float(string: str) -> float | None: ...
def split(
    string: str,
    split_by: None | str | re.Pattern = None,
    converter: Callable[[str], Any] | None = None,
) -> list[Any]: ...
def extract_match(
    string: str,
    pattern: re.Pattern,
    pos: int = 0,
    endpos: int = ...,
    converter: Callable[[str], Any] | None = None,
) -> list[Any]: ...


# --- ПУБЛІЧНІ ФУНКЦІЇ CLI ---

# Константні дефолтні значення (ANY, INT) замінено на '...'
# Лямбда-функції та is_in_list також замінено на '...'

def get_input(prompt: str = "",
              pattern: str | re.Pattern = ..., # Замість ANY
              validator: Callable[[str], bool] = ...,
              converter: Callable[[str], Any] = str,
              default: Any | None = None,
              *,
              retry: bool = True,
              if_invalid: str = "invalid input!",
              on_keyboard_interrupt: Callable | None = None,) -> Any: ...

def get_password(
    prompt: str = "Password: ",
    pattern: str | re.Pattern = ..., # Замість ANY
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = True,
    if_invalid: str = "Invalid password format!",
    on_keyboard_interrupt: Callable | None = None,
) -> str: ...


def get_choice(options: list[str],
               prompt: str = "Choose option: ",
               if_invalid: str = "Incorrect option!",
               case_sensitive: bool = False,
               show: bool = False,
               pattern: str = "- {}",
               join_by: str = "\n",
               start: str = "",
               end: str = "",
               ) -> str: ...

def menu(options: dict[int, str],
         prompt: str = "Choose option: ",
         if_invalid: str = "Incorrect option!",
         pattern: str = "{}. {}",
         join_by: str = "\n",
         start: str = "",
         end: str = "",
         show_options: bool = True) -> int: ...

def yes_no(prompt: str = 'Confirm [y/n]: ',
           yes: list = None,
           no: list = None,
           if_invalid: str = 'Incorrect option!',
           ) -> bool: ...

def progress_bar(
    steps: int,
    title: str,
    start: str = '[',
    end: str = ']',
    char: str = '=',
    length: int = 10,
    min_update_time: float = 0.15,
    on_keyboard_interrupt: Callable | None = None,
) -> AbstractContextManager[ProgressBar]: ...

def print_iterable(
    iterable: Iterable[Any],
    item_pattern: str = "{}",
    join_by: str = "\n",
    start: str = "",
    end: str = "",
) -> None: ...

def print_table(iterable: Iterable[Iterable[Any]],
                row_pattern: str = "{}: {}",
                join_by: str = "\n",
                start: str = "",
                end: str = "",
                ) -> None: ...

def print_header(header: str,
                 char: str = "~",
                 *,
                 width: int | None = None,
                 space: int = 0
                 ) -> None: ...


def get_int(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> int: ...
def get_float(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> float: ...
def get_number(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> float: ...
def get_username(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> str: ...
def get_email(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> str: ...
def get_hex_rgb(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> str: ...
def get_date_dmy(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> date: ...
def get_date_ymd(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> date: ...
def get_time(
    prompt: str = ...,
    validator: Callable[[str], bool] = ...,
    *,
    retry: bool = ...,
    if_invalid: str = ...,
    on_keyboard_interrupt: Callable | None = None,
) -> time: ...
def on_interrupt(
        func: Callable
) -> None: ...
