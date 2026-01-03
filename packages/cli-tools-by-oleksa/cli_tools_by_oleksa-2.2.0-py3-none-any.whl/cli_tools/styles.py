import re
from .exceptions import APIError
from .patterns import HEX_RGB
from ._ansi_support import ANSI_SUPPORTED


HEX = re.compile(r"(?:bg)?" + HEX_RGB.pattern)


# --- Foreground Colors (Text) ---
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# --- Bright Foreground Colors (High Intensity Text) ---
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# --- Background Colors ---
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

# --- Bright Background Colors (High Intensity Background) ---
BG_BRIGHT_BLACK = "\033[100m"
BG_BRIGHT_RED = "\033[101m"
BG_BRIGHT_GREEN = "\033[102m"
BG_BRIGHT_YELLOW = "\033[103m"
BG_BRIGHT_BLUE = "\033[104m"
BG_BRIGHT_MAGENTA = "\033[105m"
BG_BRIGHT_CYAN = "\033[106m"
BG_BRIGHT_WHITE = "\033[107m"

# --- Styles and Utility Codes ---
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
INVERSE = "\033[7m"
STRIKETHROUGH = "\033[9m"


class rgb:
    """
        Represents and converts full-range (24-bit) RGB color data into an
        ANSI escape sequence (True Color).

        The object is designed to be passed to the 'stylize' function.

        It accepts color definitions in two formats:
        1. A tuple of (R, G, B) integers (0-255).
        2. A string in HEX format ('#RRGGBB').

        The background color can be specified either by:
        - Passing the 'is_bg=True' argument.
        - Using a special HEX string prefix (e.g., 'bg#RRGGBB').

        Raises:
            APIError: If the color format is incorrect or RGB components are out of range (0-255).
        """
    def __init__(self, color: tuple[int, int, int] | str, is_bg=False):
        if isinstance(color, tuple):
            self.r = color[0]
            self.g = color[1]
            self.b = color[2]
        elif isinstance(color, str):
            if HEX.fullmatch(color):
                if color.startswith("bg"):
                    is_bg = True
                    color = color[3:]
                else:
                    color = color[1:]
                self.r = int(color[0:2], 16)
                self.g = int(color[2:4], 16)
                self.b = int(color[4:6], 16)
            else:
                raise APIError("incorrect HEX format.")
        else:
            raise APIError("incorrect color format.")

        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255):
            raise APIError("RGB components must be between 0 and 255.")

        self.code_type = 48 if is_bg else 38

    def __repr__(self):
        return "rgb({}, {}, {}, {})".format(
            self.r, self.g, self.b, self.code_type == 48
        )

    def __str__(self):
        return f"\033[{self.code_type};2;{self.r};{self.g};{self.b}m"


def stylize(text: str, *codes: str | rgb) -> str:
    """
    Wraps the given text with one or more ANSI codes and ensures a reset at the end.

    This function is the core style applicator, allowing easy combination of colors and styles.

    :param text: Text to style.
    :param codes: One or more ANSI codes (e.g., RED, BOLD, or the result of rgb_color()).
    :return: The styled and reset string.
    """
    if ANSI_SUPPORTED:
        combined_code = "".join(str(code) for code in codes)
        return f"{combined_code}{text}{RESET}"
    return text


def error(text: str) -> str:
    """Style helper: Returns text in RED."""
    return stylize(text, RED)


def success(text: str) -> str:
    """Style helper: Returns text in GREEN."""
    return stylize(text, GREEN)


def warning(text: str) -> str:
    """Style helper: Returns text in YELLOW."""
    return stylize(text, YELLOW)


def info(text: str) -> str:
    """Style helper: Returns text in CYAN."""
    return stylize(text, CYAN)


def bold(text: str) -> str:
    """Style helper: Returns text in BOLD."""
    return stylize(text, BOLD)
