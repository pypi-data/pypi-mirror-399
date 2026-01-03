import re


ANY = re.compile(r".*")


# Math patterns
INT = re.compile(r"[+-]?\d+")
"""Matches any integer number, optionally prefixed with '+' or '-'."""

FLOAT = re.compile(r"[+-]?\d+\.\d+")
"""Matches any floating-point number (must contain a decimal point), optionally prefixed with '+' or '-'."""

NUMBER = re.compile(r"[+-]?\d+(?:\.\d+)?")
"""Matches any number (integer or float), optionally prefixed with '+' or '-'."""

HEX_RGB = re.compile(r"#([a-fA-F0-9]{6})")


# Text patterns
USERNAME = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
"""Matches a variable name or identifier: starts with a letter or underscore,
followed by letters, numbers, or underscores."""

EMAIL = re.compile(r"[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
"""Matches a basic email format (user@domain.tld)."""


# Datetime patterns
DATE_DMY = re.compile(r"\d{2}\.\d{2}\.\d{4}")
"""Matches a date in DD.MM.YYYY format."""

DATE_YMD = re.compile(r"\d{4}-\d{2}-\d{2}")
"""Matches a date in YYYY-MM-DD format."""

TIME_24H = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")
"""Matches a time in HH:MM format (24-hour clock)."""


def in_line(pattern: re.Pattern):
    """
    Wraps the pattern by adding ^ at the beginning and $ at the end

    :param pattern: Pattern to wrap.
    :return: Wrapped pattern.
    """
    return re.compile(r"^" + pattern.pattern + r"$")


def in_group(pattern: re.Pattern) -> re.Pattern:
    """
    Creates a new compiled RegEx pattern by wrapping the original pattern
    in a capture group.

    USE WITH CAUTION: This creates nested capture groups if the input pattern
    already contains them.

    :param pattern: The original compiled RegEx pattern.
    :return: A new compiled RegEx pattern with an outer capture group.
    """
    return re.compile(r"(" + pattern.pattern + r")")
