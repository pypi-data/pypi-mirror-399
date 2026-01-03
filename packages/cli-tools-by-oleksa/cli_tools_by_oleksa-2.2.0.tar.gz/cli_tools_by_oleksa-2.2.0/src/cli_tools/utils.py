import re
import traceback
from sys import exit, maxsize
from typing import Type, Callable, Iterable, Any
from contextlib import contextmanager


def _on_ki():
    """
    Default internal handler for KeyboardInterrupt (SIGINT).

    Ensures that the cursor moves to a new line (preventing broken terminal lines)
    and exits the process gracefully with status code 0. Used as a fallback
    across all CLI input functions.
    """
    print()  # Guarantees line wrapping
    exit(0)


def on_interrupt(func: Callable) -> None:
    """
    Overrides the default global interrupt handler with a custom callable.

    This allows the user to define a project-wide behavior for Ctrl+C events.
    The registered function will be triggered by `get_input`, `progress_bar`,
    and all specialized input functions (e.g., `get_int`, `get_email`)
    whenever a local `on_keyboard_interrupt` handler is not provided.

    :param func: A callable to be executed when a KeyboardInterrupt occurs.
    """
    global _on_ki
    _on_ki = func


@contextmanager
def safe_run(
        debug: bool = False,
        exit_on_error: bool = True,
        on_keyboard_interrupt: Callable | None = None,
):
    """
    Context manager for safe code execution, catching exceptions and managing program termination.

    It specifically intercepts `KeyboardInterrupt` to exit with status 0, ensuring graceful shutdown
    when the user interrupts the script (e.g., Ctrl+C). Catches common exceptions and manages termination.

    :param debug: If True, prints the full traceback upon error. If False, prints a brief error message.
                  Defaults to False.
    :param exit_on_error: If True, the program exits with a status code of 1 upon catching an exception.
                          If False, the program continues execution after the 'with' block.
                          Defaults to True.
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)
    :return: Context manager yields execution control.
    """
    try:
        yield
    except KeyboardInterrupt:
        if on_keyboard_interrupt is None:
            _on_ki()
        else:
            on_keyboard_interrupt()
    except Exception as e:
        if debug:
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        if exit_on_error:
            exit(1)


def try_until_ok(
        func: Callable[..., Any],
        *args: Any,
        exceptions: tuple[Type[BaseException], ...] | Type[BaseException] = Exception,
        on_exception: str | Callable[[BaseException], Any] | None = None,
        on_keyboard_interrupt: Callable | None = None,
        **kwargs,
) -> Any:
    """
    Attempts to execute the function repeatedly in a loop until it completes without errors,
    catching specified exceptions and providing feedback.

    :param func: Function to execute repeatedly.
    :param args: Positional arguments to pass to the function.
    :param exceptions: A single exception type or a tuple of exception types to catch and retry.
                       Defaults to catching all generic exceptions (Exception).
                       Note: `KeyboardInterrupt` is always handled separately and terminates the program.
    :param on_exception: Action to take when a caught error occurs:
                     - str: The string message to print.
                     - Callable: A function (Callable[[BaseException], Any]) to call with the exception object.
                     - None (default): Prints the generic error message (f'Error: {e}').
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)
    :param kwargs: Keyword arguments to pass to the function.
    :return: The result returned by the successfully executed function.
    """
    while True:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            if on_keyboard_interrupt is None:
                _on_ki()
            else:
                on_keyboard_interrupt()
        except exceptions as e:
            if isinstance(on_exception, str):
                print(on_exception)
            elif callable(on_exception):
                on_exception(e)
            else:
                print(f"Error: {e}")


def safe_int(string: str) -> int | None:
    """
    Safe way to convert a string to an int.

    :param string: string to convert.
    :return: int if text converted to int, else None.
    """
    try:
        return int(string)
    except ValueError:
        return None


def safe_float(string: str) -> float | None:
    """
    Safe way to convert a string to a float.

    :param string: string to convert.
    :return: float if text converted to float, else None.
    """
    try:
        return float(string)
    except ValueError:
        return None


def split(
        string: str,
        split_by: None | str | re.Pattern = None,
        converter: Callable[[str], Any] | None = None,
) -> list:
    """
    Splits text string and returns a list of elements.

    :param string: The input string to be split.
    :param split_by: The delimiter used for splitting.
                     If None (default), uses str.split().
                     Can be a string or a compiled re.Pattern.
    :param converter: Callable[[str], Any] to be applied to each element after splitting
                      (e.g., int, float, str.strip). If None, elements remain as strings.
    :raises TypeError: If 'split_by' is of an unsupported type.
    :return: List of parsed and optionally converted elements.
    """

    if split_by is None or isinstance(split_by, str):
        res = string.split(split_by)
    elif isinstance(split_by, re.Pattern):
        res = re.split(split_by, string)
    else:
        raise TypeError("split_by must be None, str or re.Pattern.")

    if converter:
        return [converter(el) for el in res]
    return res


def extract_match(
        string: str,
        pattern: re.Pattern,
        pos: int = 0,
        endpos: int = maxsize,
        converter: Callable[[str], Any] | None = None,
) -> list:
    """
    Performs a RegEx search and returns a list of captured groups.

    It uses the `re.search()` method and extracts all groups captured
    by the provided pattern.

    Can convert all elements with a converter function.

    :param string: The input text to search within.
    :param pattern: The compiled RegEx pattern (re.Pattern) containing capture groups.
    :param pos: Optional. The starting index for the search (default 0).
    :param endpos: Optional. The ending index for the search (default sys.maxsize).
    :param converter: Optional. A callable function (e.g., int, float, str.strip)
                      to be applied to EACH captured group string (default None).
    :return: List of parsed and optionally converted elements. [] if no matches found.
    """
    match = pattern.search(string, pos=pos, endpos=endpos)
    if not match:
        return []
    res = match.groups()
    if converter:
        return [converter(el) for el in res]
    return list(res)


def format_iterable(
        iterable: Iterable[Any],
        item_pattern: str = "{}",
        join_by: str = "\n",
        start: str = "",
        end: str = "",
) -> str:
    """
    Formats all elements of a one-dimensional iterable into a single string.

    Each item is formatted using 'item_pattern' and then joined by 'join_by'.

    :param iterable: The iterable (e.g., list, tuple, set) whose elements are to be formatted.
    :param item_pattern: The format string used for each individual item (e.g., 'Item: {}').
    :param join_by: The separator placed between the formatted elements.
    :param start: A prefix string placed at the beginning of the resulting string.
    :param end: A suffix string placed at the end of the resulting string.
    :return: The fully formatted string containing all elements.
    """
    formated_items = [item_pattern.format(item) for item in iterable]
    return start + join_by.join(formated_items) + end


def format_table(
        iterable: Iterable[Iterable[Any]],
        row_pattern: str = "{}: {}",
        join_by: str = "\n",
        start: str = "",
        end: str = "",
) -> str:
    """
    Formats elements of an iterable containing unpackable items (e.g., pairs, tuples).

    This is useful for tables and items produced by enumerate(), zip(), dict.items(), etc.

    :param iterable: The iterable containing elements that can be unpacked (e.g., [(1, 'a'), (2, 'b')]).
                     Each inner element is unpacked using Python's *item syntax.
    :param row_pattern: The format string used for each inner unpackable element.
                         The number of elements in each inner item MUST match the number of placeholders
                         in 'item_pattern' (e.g., '{}: {}' requires two elements).
    :param join_by: The separator placed between the formatted elements.
    :param start: A prefix string placed at the beginning of the output.
    :param end: A suffix string placed at the end of the output.
    """
    formated_items = [row_pattern.format(*item) for item in iterable]
    return start + join_by.join(formated_items) + end
