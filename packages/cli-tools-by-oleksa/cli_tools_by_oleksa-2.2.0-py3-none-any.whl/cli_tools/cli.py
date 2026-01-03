import re
import getpass
from typing import Callable, Any, Iterable
from contextlib import contextmanager
from shutil import get_terminal_size
from time import time

from .exceptions import ValidationError, ConversionError, APIError
from .patterns import INT, ANY
from .validators import is_in_list
from .utils import format_iterable, format_table, try_until_ok
from . import utils as u
from .terminal import clear_line, move_to_column, move_up


def get_input(prompt: str = "",
              pattern: str | re.Pattern = ANY,
              validator: Callable[[str], bool] = lambda x: True,
              converter: Callable[[str], Any] = str,
              default: Any | None = None,
              *,
              retry: bool = True,
              if_invalid: str = "invalid input!",
              on_keyboard_interrupt: Callable | None = None) -> Any:
    """
    Prompts the user for input and performs validation, with optional retry logic.

    This function is the core of validated input handling, combining single-pass
    validation (when retry=False) and repeated attempts (when retry=True).
    The validation sequence is strict: 1) RegEx Pattern Check, 2) Custom Validator Check,
    3) Conversion.

    :param prompt: The message displayed to the user before input.
    :param pattern: A regex pattern (str or re.Pattern) the input must fully match.
                    Defaults to ANY (r'.*').
    :param validator: A custom function (Callable[[str], bool]) for additional logical checks.
                      It receives the input string before conversion.
    :param converter: A function (Callable[[str], Any]) to convert the validated input string
                      to the desired type (e.g., int, float). Defaults to str.
    :param default: The value to return if the user presses Enter (provides empty input).
                    Can be any type (Any), as this value bypasses validation and conversion.
    :param retry: If False, the function acts as a single-pass validator:
                  it raises exceptions upon failure. If True (default), it loops, prompting
                  the user until valid input is provided.
    :param if_invalid: The error message displayed upon validation/conversion failure (used only if retry=True).
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)

    :returns: The converted input value (Any).

    :raises ValidationError: If the input does not match the 'pattern' or fails
                             the 'validator' check, and retry=False.
    :raises ConversionError: If the 'converter' function raises an exception
                             (e.g., ValueError, TypeError) during type conversion, and retry=False.
    """
    if retry:
        return try_until_ok(
            get_input,
            prompt=prompt,
            pattern=pattern,
            validator=validator,
            converter=converter,
            default=default,
            exceptions=ValidationError,
            retry=False,
            on_exception=if_invalid,
            on_keyboard_interrupt=on_keyboard_interrupt
        )

    input_text = input(prompt)

    if default is not None and input_text == '':
        return default

    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    if pattern.fullmatch(input_text) and validator(input_text):
        try:
            return converter(input_text)
        except Exception as e:
            raise ConversionError(f"conversion failed: {e}") from e
    else:
        raise ValidationError("invalid input format!")


def get_password(
    prompt: str = "Password: ",
    pattern: str | re.Pattern = ANY,
    validator: Callable[[str], bool] = lambda x: True,
    *,
    retry: bool = True,
    if_invalid: str = "Invalid password format!",
    on_keyboard_interrupt: Callable | None = None,
) -> str:
    """
    Prompts the user for sensitive input (password) without echoing characters
    to the console, and applies validation with optional retry logic.

    This function uses getpass.getpass() for secure input handling. It defaults
    to retry=True because password input often requires multiple attempts to
    satisfy complexity requirements.

    :param prompt: The message displayed to the user. Defaults to 'Password: '.
    :param pattern: A regex pattern (str or re.Pattern) the password must fully match.
                    Defaults to ANY (r'.*').
    :param validator: A custom function (Callable[[str], bool]) for additional logical checks.
                      It receives the input string before conversion.
    :param retry: If True (default), loops until a valid password is given, displaying
                  'if_invalid' message. If False, raises exceptions upon failure.
    :param if_invalid: The error message displayed upon validation failure (used only if retry=True).
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)

    :returns: The validated password string.

    :raises ValidationError: If retry=False and validation fails.
    """
    if retry:
        return try_until_ok(
            get_password,
            prompt=prompt,
            pattern=pattern,
            validator=validator,
            exceptions=ValidationError,
            retry=False,
            on_exception=if_invalid,
            on_keyboard_interrupt=on_keyboard_interrupt
        )

    password = getpass.getpass(prompt=prompt)

    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    if pattern.fullmatch(password) and validator(password):
        return password
    else:
        raise ValidationError("invalid password format!")


def get_choice(
        options: list[str],
        prompt: str = "Choose option: ",
        if_invalid: str = "Incorrect option!",
        case_sensitive: bool = False,
        show: bool = False,
        pattern: str = "- {}",
        join_by: str = "\n",
        start: str = "",
        end: str = "",
        on_keyboard_interrupt: Callable | None = None,
) -> str:
    """
    Prompts the user to input a string and validates that the input exactly
    matches one of the provided options from the list.

    The function uses 'get_input' with retry = True and 'is_in_list' validator.

    :param options: List of acceptable string choices.
    :param prompt: Text displayed to the user before input.
    :param if_invalid: Text displayed to the user if input is incorrect.
    :param case_sensitive: If True, validation is case-sensitive;
                           if False (default), case is ignored during comparison.
    :param show: If True, prints the list of 'options' using 'print_iterable'
                 before prompting the user. Defaults to False (e.g., for 'Y/n' prompts).
    :param pattern: Format string passed to 'print_iterable' for displaying each item
                    (e.g., '- {}'). Used only if 'show' is True.
    :param join_by: Separator placed between formatted elements. Used only if 'show' is True.
    :param start: Prefix string placed at the beginning of the output. Used only if 'show' is True.
    :param end: Suffix string placed at the end of the output. Used only if 'show' is True.
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)
    :raises APIError: If the 'options' list is empty.
    :return: The string that the user successfully entered from the 'options' list.
    """
    if not options:
        raise APIError("options list can't be empty.")

    if show:
        print_iterable(options, item_pattern=pattern, join_by=join_by, start=start, end=end)

    return get_input(prompt=prompt,
                     validator=is_in_list(options, case_sensitive),
                     retry=True,
                     if_invalid=if_invalid,
                     on_keyboard_interrupt=on_keyboard_interrupt)


def menu(
        options: dict[int, str],
        prompt: str = "Choose option: ",
        if_invalid: str = "Incorrect option!",
        pattern="{}. {}",
        join_by: str = "\n",
        start: str = "",
        end: str = "",
        show_options: bool = True,
        on_keyboard_interrupt: Callable | None = None,
) -> int:
    """
    Print a numbered menu and ask the user to pick an option by its number.

    The **keys** of the dictionary are the exact numbers the user must type.
    The order is preserved (Python 3.7+ dicts are ordered).

    Perfect for the ultra-clean pattern:
        match menu(options):
            case 1: ...
            case 0: break

    Parameters
    ----------
    options : dict[int, str]
        Menu items. Keys = numbers the user types, values = displayed text.
        Common pattern: 1, 2, 3, 0 for "Exit".
    prompt : str, default "Choose option: "
        Text shown before input.
    if_invalid : str, default "Incorrect option!"
        Message shown on invalid input.
    pattern : str, default "{}. {}"
        Row format string for ``print_table``. First placeholder = number, second = text.
    join_by, start, end : str
        Formatting options passed directly to ``print_table``.
    show_options : bool, default True
        If True, the function prints the numbered menu options to the console
        before asking for input. Set to **False** if you want to display the
        options using custom formatting logic.
    on_keyboard_interrupt : Callable | None, default None
                     - Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)

    Returns
    -------
    int
        The number (key) that user entered.

    Example
    -------
    >>> options = {1: "Play", 2: "Rating", 0: "Exit"}
    >>> while True:
    ...     match menu(options, pattern="{}. {}"):
    ...         case 1: play()
    ...         case 2: show_rating()
    ...         case 0: break
    """
    if show_options:
        print_table(options.items(), pattern, join_by=join_by, start=start, end=end)
    return get_input(
        prompt=prompt,
        pattern=INT,
        validator=is_in_list([str(key) for key in options.keys()], case_sensitive=False),
        converter=lambda t: int(t),
        retry=True,
        if_invalid=if_invalid,
        on_keyboard_interrupt=on_keyboard_interrupt
    )


def yes_no(
        prompt: str = 'Confirm [y/n]: ',
        yes: list = None,
        no: list = None,
        if_invalid: str = 'Incorrect option!',
        on_keyboard_interrupt: Callable | None = None,
) -> bool:
    """
        Prompts the user for a yes/no confirmation with input validation.

        Parameters
        ----------
        prompt : str
            The prompt text displayed to the user.
            'Confirm [y/n]: ' by default.
        yes : list[str]
            A list of allowed strings for a 'Yes' response.
            ['y', 'yes'] by default.
        no : list[str]
            A list of allowed strings for a 'No' response.
            ['n', 'no'] by default.
        if_invalid : str
            The message displayed when invalid input is entered.
            ['Incorrect option!'] by default.
        on_keyboard_interrupt : Callable | None, default None
                     - Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)

        Returns
        -------
        bool
            True if the user entered an option from 'yes'; False if from 'no'.
        """
    if no is None:
        no = ['n', 'no']
    else:
        no = [string.lower() for string in no]
    if yes is None:
        yes = ['y', 'yes']
    else:
        yes = [string.lower() for string in yes]
    inp = get_input(
        prompt,
        validator=is_in_list(
            yes + no,
            case_sensitive=False
        ),
        retry=True,
        if_invalid=if_invalid,
        on_keyboard_interrupt=on_keyboard_interrupt,
    ).lower()

    return inp in yes


def print_iterable(
        iterable: Iterable[Any],
        item_pattern: str = "{}",
        join_by: str = "\n",
        start: str = "",
        end: str = ""
) -> None:
    """
    Conveniently prints all elements of a one-dimensional iterable, formatted
    using the logic of format_iterable().

    :param iterable: The iterable whose elements are to be formatted and printed.
    :param item_pattern: The format string used for each individual item (e.g., 'Item: {}').
    :param join_by: The separator placed between the formatted elements.
    :param start: A prefix string placed at the beginning of the output.
    :param end: A suffix string placed at the end of the output.
    :return: None. The result is printed directly to stdout.
    """
    print(format_iterable(iterable, item_pattern, join_by, start, end))


def print_table(iterable: Iterable[Iterable[Any]],
                row_pattern: str = "{}: {}",
                join_by: str = "\n",
                start: str = "",
                end: str = "",
                ) -> None:
    """
    Conveniently prints elements of an iterable containing unpackable items (e.g., pairs, tuples),
    formatted using the logic of format_table().

    This is useful for tables and items produced by enumerate(), zip(), dict.items(), etc.

    :param iterable: The iterable containing elements that can be unpacked (e.g., [(1, 'a'), (2, 'b')]).
                     Each inner element is unpacked using Python's *item syntax.
    :param row_pattern: The format string used for each inner unpackable element.
                         The number of elements in each inner item MUST match the number of placeholders
                         in 'item_pattern' (e.g., '{}: {}' requires two elements).
    :param join_by: The separator placed between the formatted elements.
    :param start: A prefix string placed at the beginning of the output.
    :param end: A suffix string placed at the end of the output.
    :return: None. The result is printed directly to stdout.
    """
    print(format_table(iterable, row_pattern, join_by, start, end))


def print_header(
        header: str,
        char: str = "~",
        *,
        width: int | None = None,
        space: int = 0
) -> None:
    """
    Prints a nice centered header with decorative lines.

    :param header: Text to display
    :param char: Symbol for the lines (default: '~')
    :param width: Force specific line width. If None — uses length of header.
    :param space: Number of spaces added on both sides of the header (default: 0)
    """
    header = " " * space + header + " " * space
    line = char * (width or len(header))
    print(f"{line}\n{header}\n{line}")


class ProgressBar:
    """
    Manages the state and rendering of a console progress bar.

    This class handles dynamic terminal resizing, update throttling to save resources,
    and smart formatting (switching to two-line display if the title is too long).
    """

    def __init__(
            self,
            steps: int,
            title: str,
            start: str = '[',
            end: str = ']',
            char: str = '=',
            length: int = 10,
            min_update_time: float = 0.15
    ):
        """
        Initialize the ProgressBar.

        :param steps: Total number of steps to complete (100%).
        :param title: Text string displayed alongside the bar.
        :param start: Character(s) marking the start of the bar (default: '[').
        :param end: Character(s) marking the end of the bar (default: ']').
        :param char: Character used to fill the progress (default: '=').
        :param length: Maximum visual length of the bar in characters (excluding title/percentage).
                       The bar will automatically shrink if the terminal width is too small.
        :param min_update_time: Minimum time interval (in seconds) between screen refreshes.
                                Used to prevent flickering and reduce CPU usage during fast loops.
        """
        self._steps = steps
        self._title = title
        self._start = start
        self._end = end
        self._char = char
        self._length = length
        self._step = 0
        self._min_update_time = min_update_time
        self._last_update_time = 0

    def start(self):
        """
        Draws the initial state of the progress bar (0%) and returns the instance.
        Useful for method chaining or usage within context managers.

        :return: self
        """
        self.draw()
        return self

    def draw(self):
        """
        Renders the current state of the progress bar to the console.

        This method calculates the percentage, checks the terminal width, and
        formats the output string accordingly. It includes logic to throttle
        updates based on `min_update_time` and handles multi-line rendering
        if the terminal is too narrow for a single line.
        """
        curr_time = time()
        # Throttling check: skip drawing if not enough time has passed,
        # unless it is the final step (which should always be drawn).
        if curr_time - self._last_update_time < self._min_update_time and self._step < self._steps:
            return

        self._last_update_time = curr_time
        perc = (self._step / self._steps) * 100
        columns = get_terminal_size().columns
        length = min(self._length, columns - len(self._start) - len(self._end))
        chars = int(perc * length / 100)
        bar = f'{self._start}{self._char * chars:<{length}}{self._end}'
        title = self._title
        perc = f'  {perc:.2f}%'

        # Check if the full line fits in the current terminal width
        if len(bar) + len(title) + len(perc) + 8 > columns:
            # Multi-line mode: Title on top, bar below
            line = f'{title}{perc:>{len(bar) - len(title)}}\n{bar}'
            clear_line()
            move_up(1)
        else:
            # Single-line mode
            free = min(columns - len(bar) - len(perc), 8 + len(title))
            line = f'{title:<{free}}{bar}{perc}'

        clear_line()
        move_to_column(1)
        print(line, end='', flush=True)

    def update(self, steps=1):
        """
        Advances the progress by the specified number of steps.

        :param steps: Number of steps to add to the current progress (default: 1).
        """
        self._step += steps
        if self._step > self._steps:
            self._step = self._steps

        self.draw()


@contextmanager
def progress_bar(
        steps: int,
        title: str,
        start: str = '[',
        end: str = ']',
        char: str = '=',
        length: int = 10,
        min_update_time: float = 0.15,
        on_keyboard_interrupt: Callable | None = None,
):
    """
    Context manager for displaying a progress bar during a loop.

    It handles initialization, safe execution, and clean termination (printing a newline)
    after the loop finishes. It also provides a mechanism to handle KeyboardInterrupt gracefully.

    :param steps: Total number of iterations.
    :param title: Title text displayed next to the bar.
    :param start: Starting character of the bar.
    :param end: Ending character of the bar.
    :param char: Progress fill character.
    :param length: Desired length of the bar.
    :param min_update_time: Throttling interval in seconds to prevent flickering.
    :param on_keyboard_interrupt: Optional callback function to execute if the user presses Ctrl+C.
                                  If None, uses default handler print() + exit(0).
                                  You can change default handler with utils.on_interrupt.
    :yields: An instance of `ProgressBar` with an `.update()` method.
    """
    try:
        bar = ProgressBar(steps, title, start, end, char, length, min_update_time)
        yield bar.start()
    except KeyboardInterrupt:
        if on_keyboard_interrupt:
            on_keyboard_interrupt()
        else:
            u._on_ki()

    print()
