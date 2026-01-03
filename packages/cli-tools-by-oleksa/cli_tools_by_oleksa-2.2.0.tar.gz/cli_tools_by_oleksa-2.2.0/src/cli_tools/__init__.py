__version__ = "2.2.0"

from .utils import (
    safe_int,
    safe_float,
    split,
    extract_match,
    safe_run,
    try_until_ok,
    format_iterable,
    format_table,
)
from .cli import (
    get_input,
    get_choice,
    print_iterable,
    print_table,
    print_header,
    menu,
    yes_no,
    progress_bar,
)
from .utils import on_interrupt
from ._api_builder import _build_input_api


_generated_funcs = _build_input_api()
for name, func in _build_input_api().items():
    globals()[name] = func


__all__ = [
    'safe_run',
    'try_until_ok',
    'safe_int',
    'safe_float',
    'split',
    'extract_match',
    'format_iterable',
    'format_table',
    'get_input',
    'get_choice',
    'print_iterable',
    'print_table',
    'print_header',
    'menu',
    'yes_no',
    'progress_bar',
    *_generated_funcs.keys(),
]
