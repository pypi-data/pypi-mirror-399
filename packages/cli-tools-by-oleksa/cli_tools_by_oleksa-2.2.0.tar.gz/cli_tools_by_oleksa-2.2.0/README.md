# cli_tools_by_oleksa

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/cli-tools-by-oleksa?color=green&label=version)](https://pypi.org/project/cli-tools-by-oleksa/)

A zero-dependency Python library for robust console input (validation, menus, type conversion) and cross-platform terminal control and styling.

***

### Purpose

This toolkit is designed to eliminate the notorious boilerplate required for reliable interactive console applications. It allows developers to completely bypass the need for writing repetitive input validation loops (`while True: try/except`) and managing fragile ANSI escape sequences for styling and cursor control.

### Target Audience

**`cli_tools`** is the perfect choice for projects where simplicity and minimal dependencies are paramount:

* **Students and Educators:** Write clean, readable code instantly without complex, low-level validation logic.
* **Utility & Script Developers:** Build robust, highly interactive command-line tools and prototypes quickly, without adopting heavy frameworks like Click, Typer, or Rich.
* **Clean Code Enthusiasts:** Achieve production-level reliability and polished user interaction while maintaining a zero-dependency footprint.

### Source Code

https://github.com/01eksa/cli_tools_by_oleksa

---

## Core Features

### Input & Validation

* **`get_input`** — The central function for user input. Features a robust pipeline (RegEx → Validator → Converter) and an  **automatic retry loop** (`retry=True` by default).
* **`get_password`** — Securely prompts the user for a password (text is not echoed). It supports the full validation pipeline (RegEx → Validator) and **automatic retry logic**.
* **Specialized `get_*` Wrappers** — Dynamically generated functions (e.g., `get_int`, `get_email`, `get_date_dmy`) that pre-package specific RegEx patterns and converters for immediate use.
* **Validator Factories** — Reusable functions that **generate** validators (`is_in_range`, `is_list_of`, etc.), allowing users to easily compose complex input validation logic.
* **Validator Composition** — Combine multiple rules using `all_of` and `any_of` factories for complex, multi-stage data validation.
* **Predefined Patterns** — A set of included **RegEx constants** (`INT`, `FLOAT`, `EMAIL`, `DATE_DMY`) available for immediate use in input validation.


---

### Parsing, Splitting, and Converting

* **`extract_match`** — Extracts regex groups from a string and **converts** them to target types in a single step.
* **`split`** — Splits strings by delimiter or regex with optional automatic type conversion of elements.
* **`safe_int` / `safe_float`** — Fault-tolerant converters that return `None` on failure instead of raising exceptions.

---

### Menus & Selection

* **`menu`** — Generates a numbered console menu from a dictionary and returns the selected **key** (int).
* **`get_choice`** — Selects a string from a list of options. It is **case-insensitive by default** and includes auto-retry logic.
* **`yes_no`** — A standard confirmation prompt returning a `bool` (`True` for yes, `False` for no).

---

### Terminal Control & Dynamic Display

* **Cursor Control** — A comprehensive suite of functions (`move_to`, `move_to_column`, `move_up/down`, etc.) for building dynamic interfaces like spinners or progress bars.
* **Cross-Platform Reliability** — Includes a built-in **WinAPI fallback** mechanism, ensuring cursor movements and screen clearing work correctly on Windows even if ANSI is not natively supported.
* **`set_title`** — Sets the console window title.

---

### Styling & Formatting

* **`stylize`** — Apply one or few styles to text.
* **`rgb`** - Convert RGB (tuple or hex) into ANSI code for this color
* **Style Helpers** — Ready-made, semantic functions (`error`, `success`, `warning`, `info`) for applying standard color schemes instantly.
* **Style Constants** — Ready-to-use constants for foregrounds (`RED`), backgrounds (`BG_BLUE`), and attributes (`BOLD`, `UNDERLINE`).
* **Pretty Printing** — `print_table` and `print_iterable` for formatting lists and tabular data with custom patterns.
* **`print_header`** — Displays a centered title with decorative separators.
* **`progress_bar`** — Adaptive context manager with automatic title wrapping and screen refresh rate limit.

---

### Utilities & Error Safety

* **`safe_run`** — A context manager that handles exceptions gracefully and ensures a clean exit on `KeyboardInterrupt` (Ctrl+C).
* **`try_until_ok`** — A universal wrapper to repeatedly execute unstable functions (e.g., network calls) until success.
* **`on_interrupt`** — Global interrupt control: use it to define a consistent behavior for Ctrl+C across your entire application.

#### Requires Python 3.10+ and has zero external dependencies.

---

## Installation
```bash
pip install --upgrade cli_tools_by_oleksa
```

---

## What's new in 2.2.0?
* Added `on_interrupt` function to set default `KeyboardInterrupt` handling for all functions with `on_keyboard_interrupt` parameter.
* Added simple progress bar context manager (look for example 3)
* The source code is available on GitHub

---

### What's new in 2.1.1?
* Added `on_keyboard_interrupt` parameter to customize `KeyboardInterrupt` handling to `get_input`, `try_until_ok`, `safe_run`. Also, by default, a newline character is now printed before calling `sys.exit(0)`.
* Fixed an issue with style support on Linux

---

### What's new in 2.1?
* Functions for combining multiple validators: `any_of` and `all_of` and `not_in_list` validator
* `get_input` and all child functions now have `retry=True` by default

---

## Examples

### 1. Basic Functions

```Python
from cli_tools import print_header, get_input, get_int, get_number
from cli_tools.validators import is_in_range


print_header('Basic CLI Functions')

name = get_input(
    'What is your name? ',
    # DEMO: converter can modify input before return.
    # NOTE: For simple string ops like this, get_input().strip().capitalize() is cleaner.
    converter=lambda s: s.strip().capitalize(),
    # returns 'Anonim' if the user presses Enter.
    default='Anonim'
)


# get_int ensures integer format.
age = get_int(
    'How old are you? ',
    # validator checks if the number is within the range [10, 100].
    validator=is_in_range(10, 100),
    # message to show if input is incorrect
    if_invalid='Age must be an integer between 10 and 100.',
)

# get_number passes int and float numbers (returns always float).
num = get_number(
    'What is your favourite number? ',
    if_invalid='Please, enter a number.'
)


print(f"Nice to meet you, {name}! You are {age} years old and your favorite number is {num}. I like it!")


```

---

### 2. Menu, Choices and Format Output

```python
from cli_tools import print_header, get_choice, menu, yes_no, print_iterable, print_table


# Defines the main menu options for the menu() function.
# Keys (int) are the expected user input; values (str) are the displayed option text.
main_menu = {
    1: 'New game',
    2: 'Best players',
    3: 'Show results',
    0: 'Quit',
}

# Simple list of players for print_iterable demonstration.
players = [
    'You',
    'Not you',
    'Who?'
]

# Dictionary of results for print_table demonstration.
# The items (key-value pairs) will be unpacked into table rows.
results = {
    'Easy': 2308,
    'Medium': 1841,
    'Hard': 1550,
}


def play():
    """Starts the game flow, handling difficulty selection."""

    modes = ['Easy', 'Medium', 'Hard']

    # get_choice() validates user input against a list of options (modes).
    # show=True displays the options automatically before prompting.
    mode = get_choice(
        options = modes,
        prompt = 'Choose difficulty: ',
        if_invalid = 'Please, enter a valid mode name.',
        show = True
    ).lower()

    print(f'Some game logic for {mode} mode...')


def main():
    """Main loop for the CLI application, controlling flow via the menu."""

    # print_header() adds visual separation and a centered title to the console.
    print_header('Choices And Format Demo', char='=', space=3)

    while True:
        # menu() handles display, validates input against the dictionary keys, and returns the selected key (int).
        match menu(main_menu, 'What would you like to do? '):
            case 1:
                play()
            case 2:
                # print_iterable() outputs a one-dimensional list with custom formatting.
                print_iterable(
                    players,
                    start='\nBest players:\n',
                    item_pattern='- {}'
                )
            case 3:
                # print_table() iterates over results.items() and unpacks each pair into the row_pattern.
                print_table(
                    results.items(),
                    # Pattern uses format specifiers for alignment:
                    # {:<6} for left-aligned string, {:>8} for right-aligned integer
                    row_pattern = '{:<6}{:>8}',
                    start = '\nMode\tResults\n'
                )
            case 0:
                # yes_no() prompts for confirmation and returns a boolean (True for 'yes', False for 'no').
                if yes_no('Exit? [y/N]: '):
                    break

    print('Bye!')


if __name__ == '__main__':
    main()


```

---

### 3. Progress Bar

```python
from time import sleep
from cli_tools import progress_bar


with progress_bar(1000, 'Processing...', length=20) as bar:
    for i in range(1000):
        sleep(0.01)
        bar.update(steps=3)

print('Done')

```

---

### 4. Project Example: Simple Calculator

```Python
import re
from cli_tools import (print_header, get_input,
                           extract_match) # extract list of all matches, optionally convert every match
from cli_tools.patterns import NUMBER     # Ready-made pattern: accepts both int and float

# Pattern <number> <operator> <number>, spaces ignored
simple_expr_pattern = re.compile(fr' *({NUMBER.pattern}) *([+\-*/^]) *({NUMBER.pattern}) *')
# Accepts either numbers or operators. Converts numbers to float
converter = lambda x: float(x) if x not in '+-*/^' else x

print_header('| Simple calculator |', '—')
print('Supports simple expressions in format <number> <operator> <number>. Press Ctrl+C to exit.')

while True:
    # Guaranteed to pass only input that matches the pattern
    expr = get_input('> ', pattern=simple_expr_pattern, if_invalid='Wrong format!')
    # Unpack the input, immediately converting the numbers
    left, operator, right = extract_match(expr, simple_expr_pattern, converter=converter)

    match operator:
        case '+':
            print(left+right)
        case '-':
            print(left-right)
        case '*':
            print(left*right)
        case '/':
            if right == 0:
                print('Division by zero is not allowed!')
                continue
            print(left/right)
        case '^':
            print(left**right)
        case _:
            print('Wrong operator!')

```

---

### 5. Styles

```python
import cli_tools.styles as s
from cli_tools.styles import (
    rgb,       # Converts full-range RGB (HEX or tuple) into an ANSI color code.
    stylize    # Applies one or more style codes (color, background, format) to text.
)


# These functions apply a default foreground color and return the styled string.
error_msg = s.error('Error message')
warning_msg = s.warning('Warning message')
success_msg = s.success('Success message')
info_msg = s.info('Info message')

print(error_msg)
print(warning_msg)
print(success_msg)
print(info_msg)

# Define custom color using an RGB tuple (24-bit color).
tuple_yellow = (240, 240, 100)

# Apply the tuple color as foreground (text).
print(
    stylize('Yellow text', rgb(tuple_yellow))
)

# Apply the tuple color as background (using is_bg=True) and combine with BLACK foreground (text).
print(
    stylize('Yellow background', rgb(tuple_yellow, is_bg=True), s.BLACK)
)

# Define custom colors using the rgb function with HEX codes.
# The first color is foreground (text), the second specifies the background (bg#).
gray = rgb('#dddddd')
darkblue_bg = rgb('bg#0a0a88')

# wrap() applies multiple styles (foreground, background, and formatting constants).
print(
    stylize('Styled message', gray, darkblue_bg, s.ITALIC, s.UNDERLINE)
)


```

---

### 6. Terminal

```python
from time import sleep
from cli_tools import terminal as t


t.clear_screen()
t.home_cursor()
t.set_title('Title')

print('Hello!')

print('This text will disappear in a second.')
sleep(1)
t.move_up(1)
t.clear_line()

print('Simple progress bar example: ')
pattern = '[{:<10}]'

for i in range(1, 11):
    t.clear_line()
    t.move_to_column(1)
    print(pattern.format('='*i), end='', flush=True)
    sleep(0.2)
print()

print('Simple spinner example: ', end='')
for i in range(4):
    for status in ['|', '/', '—', '\\']:
        print(status, end='', flush=True)
        sleep(0.1)
        t.move_backward(1)

print('Done')


```

---

### 7. Error Handling

```python
import random, time

from cli_tools.exceptions import (CLIError,         # Base class for all raised errors
                                  APIError,         # Error that raised when you pass invalid data to a function.
                                  ValidationError,  # Data not validated
                                  ConversionError)  # The transferred converter caused an error
from cli_tools import safe_run, try_until_ok, print_header

print_header('Safe Execution Demo')

with safe_run(debug=False, exit_on_error=False):
    print("Press Ctrl+C to test graceful exit, or wait for the error...")

    for i in range(3, 0, -1):
        print(f"Crashing in {i}...")
        time.sleep(1)

    raise CLIError("Something went wrong inside the app!")

print("App still working.")

###

print_header('Retry Logic Demo')


def unstable_network_request():
    """Simulates a connection that fails 70% of the time."""
    if random.random() < 0.7:
        raise ConnectionError("Connection timed out")
    return "200 OK"


print("Attempting to connect to server...")

status = try_until_ok(
    unstable_network_request,
    exceptions=ConnectionError,
    on_exception="Connection failed. Retrying..."
)

print(f"Success! Server response: {status}")

```

---

## Roadmap

**Next Steps (Technical & Infrastructure):**
- Detailed documentation
- Tests
- Repository

**Next Steps (Feature Development):**
- Progress bar and Spinners (High-level API)
- Enhanced Validator Functionality:
    - Expanding Built-in Validators: Adding new useful validators to the library.
  