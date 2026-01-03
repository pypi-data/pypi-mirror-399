import sys
import ctypes
from typing import Callable

# --- Global State and Windows Initialization ---

# Assume ANSI is NOT supported only if on Windows. This flag will be updated
# after trying to enable ANSI processing or if WinAPI fails.
ANSI_SUPPORTED = not sys.platform.startswith('win')
ESC = '\033'

# --- Windows API Definitions (For WinAPI fallback) ---

H_STDOUT = None
Coord = None
ConsoleScreenBufferInfo = None
get_console_screen_buffer_info = None
fill_console_output_character = None
set_console_cursor_position = None

if sys.platform.startswith('win'):
    STD_OUTPUT_HANDLE = -11
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    class CoordStruct(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    Coord = CoordStruct

    class ConsoleScreenBufferInfoStruct(ctypes.Structure):
        _fields_ = [("dwSize", CoordStruct),
                    ("dwCursorPosition", CoordStruct),
                    ("wAttributes", ctypes.c_ushort),
                    ("srWindow", ctypes.c_short * 4),
                    ("dwMaximumWindowSize", CoordStruct)]

    ConsoleScreenBufferInfo = ConsoleScreenBufferInfoStruct

    kernel32 = ctypes.windll.kernel32

    GetStdHandle = kernel32.GetStdHandle
    SetConsoleMode = kernel32.SetConsoleMode
    GetConsoleMode = kernel32.GetConsoleMode
    set_console_cursor_position = kernel32.SetConsoleCursorPosition
    fill_console_output_character = kernel32.FillConsoleOutputCharacterW
    get_console_screen_buffer_info = kernel32.GetConsoleScreenBufferInfo

    # Try to get the handle immediately
    try:
        H_STDOUT = GetStdHandle(STD_OUTPUT_HANDLE)
    except Exception:
        H_STDOUT = None


def _init_support() -> None:
    """
    Attempts to enable Virtual Terminal Processing on Windows.
    Sets ANSI_SUPPORTED flag. This function runs automatically upon module import.
    """
    global ANSI_SUPPORTED
    ANSI_SUPPORTED = not sys.platform.startswith('win')
    if not sys.platform.startswith('win') or H_STDOUT is None:
        return

    try:
        # Try to enable ANSI processing
        mode = ctypes.c_ulong(0)
        kernel32.GetConsoleMode(H_STDOUT, ctypes.byref(mode))
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(H_STDOUT, new_mode)
        ANSI_SUPPORTED = True

    except Exception:
        # If ANSI fails, we rely on the WinAPI functions (H_STDOUT is still available)
        ANSI_SUPPORTED = False


def _write_ansi_or_winapi(ansi_code: str, winapi_func: Callable[[...], None] | None = None, *args) -> None:
    """
    Internal function to write ANSI code or use WinAPI fallback if ANSI is not supported
    and the platform is Windows.
    """
    if ANSI_SUPPORTED:
        sys.stdout.write(ansi_code)
        sys.stdout.flush()
        return

    # WinAPI Fallback (only on Windows, and only if H_STDOUT is available)
    if sys.platform.startswith('win') and H_STDOUT is not None and winapi_func:
        try:
            winapi_func(*args)
        except Exception:
            # Ignore WinAPI errors to keep the module quiet and non-intrusive
            pass


# --- Automatic Initialization ---
_init_support()
