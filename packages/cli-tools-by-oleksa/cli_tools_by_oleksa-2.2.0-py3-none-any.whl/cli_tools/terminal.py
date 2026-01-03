import ctypes

from ._ansi_support import (
    ESC, H_STDOUT, Coord, ConsoleScreenBufferInfo,
    get_console_screen_buffer_info, fill_console_output_character, set_console_cursor_position,
    _write_ansi_or_winapi
)


def clear_screen() -> None:
    """
    Clears the entire screen. Uses ANSI if supported, otherwise uses WinAPI on Windows.
    """

    def winapi_clear_screen():
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        cells_in_screen = csbi.dwSize.X * csbi.dwSize.Y

        cursor_to_start = Coord(0, 0)
        chars_written = ctypes.c_ulong(0)

        fill_console_output_character(
            H_STDOUT,
            ctypes.c_wchar(' '),
            cells_in_screen,
            cursor_to_start,
            ctypes.byref(chars_written)
        )
        set_console_cursor_position(H_STDOUT, cursor_to_start)

    _write_ansi_or_winapi(f"{ESC}[2J{ESC}[H", winapi_clear_screen)


def clear_line() -> None:
    """
    Writes the ANSI sequence to clear the entire current line.
    """
    def winapi_clear_line():
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        y = csbi.dwCursorPosition.Y

        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        cells_in_line = csbi.dwSize.X

        cursor_to_start = Coord(0, y)
        chars_written = ctypes.c_ulong(0)

        fill_console_output_character(
            H_STDOUT,
            ctypes.c_wchar(' '),
            cells_in_line,
            cursor_to_start,
            ctypes.byref(chars_written)
        )
        set_console_cursor_position(H_STDOUT, cursor_to_start)
    _write_ansi_or_winapi(f"{ESC}[2K", winapi_clear_line)


def home_cursor() -> None:
    """
    Writes the sequence to move the cursor to the home position (1;1). Uses WinAPI on fallback.
    """

    def winapi_home_cursor():
        set_console_cursor_position(H_STDOUT, Coord(0, 0))

    _write_ansi_or_winapi(f"{ESC}[H", winapi_home_cursor)


def set_title(title: str) -> None:
    """
    Sets the title of the console window using an Operating System Command (OSC) sequence.
    """
    _write_ansi_or_winapi(f"{ESC}]0;{title}{ESC}\\")


def move_to(y: int, x: int) -> None:
    """
    Moves the cursor to an absolute position (row and column, 1-based). Uses WinAPI on fallback.
    """

    def winapi_move_to():
        set_console_cursor_position(H_STDOUT, Coord(max(0, x - 1), max(0, y - 1)))

    _write_ansi_or_winapi(f"{ESC}[{y};{x}H", winapi_move_to)


def move_to_column(x: int) -> None:
    """
    Moves the cursor to the specified column (x, 1-based index) of the current line.

    This is essential for non-blinking updates like progress bars and spinners,
    as it does not change the cursor's row position. Uses WinAPI on fallback.
    """

    def winapi_move_to_column():
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        new_x = max(0, x - 1)
        new_y = csbi.dwCursorPosition.Y
        set_console_cursor_position(H_STDOUT, Coord(new_x, new_y))

    _write_ansi_or_winapi(f"{ESC}[{x}G", winapi_move_to_column)


def move_up(n: int) -> None:
    """Moves the cursor n lines up. Uses WinAPI on fallback."""

    def winapi_move_up():
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        new_y = max(0, csbi.dwCursorPosition.Y - n)
        new_x = csbi.dwCursorPosition.X

        set_console_cursor_position(H_STDOUT, Coord(new_x, new_y))

    _write_ansi_or_winapi(f"{ESC}[{n}A", winapi_move_up)


def move_down(n: int) -> None:
    """Moves the cursor n lines down. Uses WinAPI on fallback."""

    def winapi_move_down():
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        new_y = csbi.dwCursorPosition.Y + n
        new_x = csbi.dwCursorPosition.X

        set_console_cursor_position(H_STDOUT, Coord(new_x, new_y))

    _write_ansi_or_winapi(f"{ESC}[{n}B", winapi_move_down)


def move_forward(n: int) -> None:
    """Moves the cursor n characters forward (right). Uses WinAPI on fallback."""

    def winapi_move_forward():
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        new_x = csbi.dwCursorPosition.X + n
        new_y = csbi.dwCursorPosition.Y

        set_console_cursor_position(H_STDOUT, Coord(new_x, new_y))

    _write_ansi_or_winapi(f"{ESC}[{n}C", winapi_move_forward)


def move_backward(n: int) -> None:
    """Moves the cursor n characters backward (left). Uses WinAPI on fallback."""

    def winapi_move_backward() -> None:
        csbi = ConsoleScreenBufferInfo()
        get_console_screen_buffer_info(H_STDOUT, ctypes.byref(csbi))

        new_x = max(0, csbi.dwCursorPosition.X - n)
        new_y = csbi.dwCursorPosition.Y

        set_console_cursor_position(H_STDOUT, Coord(new_x, new_y))

    _write_ansi_or_winapi(f"{ESC}[{n}D", winapi_move_backward)
