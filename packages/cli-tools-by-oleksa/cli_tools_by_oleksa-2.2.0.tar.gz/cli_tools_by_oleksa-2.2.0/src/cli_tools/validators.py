import re
from typing import Callable, TypeAlias
from .utils import safe_float, split

Number: TypeAlias = int | float


def all_of(*validators: Callable[[str], bool]) -> Callable[[str], bool]:
    """
        Returns a validator that passes only if ALL provided validators return True.

        This function uses short-circuit logic: it stops and returns False
        immediately upon finding the first failed validator.

        Args:
            *validators: Arbitrary number of functions that accept a string and return a boolean.

        Returns:
            A callable function that serves as the combined validator.
        """

    def validator(x: str) -> bool:
        return all(v(x) for v in validators)

    return validator


def any_of(*validators: Callable[[str], bool]) -> Callable[[str], bool]:
    """
    Returns a validator that passes if ANY of the provided validators return True.

    This function uses short-circuit logic: it stops and returns True
    immediately upon finding the first successful validator.

    Args:
        *validators: Arbitrary number of functions that accept a string and return a boolean.

    Returns:
        A callable function that serves as the combined validator.
    """
    def validator(x: str) -> bool:
        return any(v(x) for v in validators)

    return validator


def is_list_of(pattern: str | re.Pattern,
               split_by: None | str | re.Pattern = None
               ) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a string is a list of specific data.

    :param pattern: The regex pattern to apply using fullmatch() to every element of list after splitting.
    :param split_by: The delimiter used for splitting.
                     If None (default), uses str.split().
                     Can be a string or a compiled re.Pattern.
    :return: A validator function (Callable[[str], bool]).
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    def validator(x: str) -> bool:
        elements = split(x, split_by)
        if not elements:
            return False
        return all(pattern.fullmatch(el) for el in elements)

    return validator


def is_in_list(options: list[str],
               case_sensitive: bool = True
               ) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a string input is in list of options.

    :param options: list of valid strings.
    :param case_sensitive: If True, validation is case-sensitive;
                           if False, case is ignored during comparison.
    :return: A validator function Callable[[str], bool].
    """
    if case_sensitive:
        return lambda x: x in options
    else:
        return lambda x: x.lower() in [opt.lower() for opt in options]


def not_in_list(options: list[str],
                case_sensitive: bool = True
                ) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a string input is not in list of options.

    :param options: list of invalid strings.
    :param case_sensitive: If True, validation is case-sensitive;
                           if False, case is ignored during comparison.
    :return: A validator function Callable[[str], bool].
    """
    if case_sensitive:
        return lambda x: x not in options
    else:
        return lambda x: x.lower() not in [opt.lower() for opt in options]


def is_in_range(start: Number, end: Number) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a number (string input)
    is within the inclusive range [start, end].

    The generated validator safely attempts to convert the input string to a float
    before comparison.

    :param start: The lower bound (inclusive).
    :param end: The upper bound (inclusive).
    :return: A validator function (Callable[[str], bool]).
    """

    def validator(text: str) -> bool:
        number = safe_float(text)
        if number is None:
            return False
        return start <= number <= end

    return validator


def is_between(start: Number, end: Number) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a number (string input)
    is within the exclusive open interval (start, end).

    :param start: The lower bound (exclusive).
    :param end: The upper bound (exclusive).
    :return: A validator function (Callable[[str], bool]).
    """

    def validator(text: str) -> bool:
        number = safe_float(text)
        if number is None:
            return False
        return start < number < end

    return validator


def more(limit: Number) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a number (string input)
    is strictly greater than the limit (> limit).

    :param limit: The number to compare against (exclusive).
    :return: A validator function (Callable[[str], bool]).
    """

    def validator(text: str) -> bool:
        number = safe_float(text)
        if number is None:
            return False
        return number > limit

    return validator


def more_or_equal(limit: Number) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a number (string input)
    is greater than or equal to the limit (>= limit).

    :param limit: The number to compare against (inclusive).
    :return: A validator function (Callable[[str], bool]).
    """

    def validator(text: str) -> bool:
        number = safe_float(text)
        if number is None:
            return False
        return number >= limit

    return validator


def less(limit: Number) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a number (string input)
    is strictly less than the limit (< limit).

    :param limit: The number to compare against (exclusive).
    :return: A validator function (Callable[[str], bool]).
    """

    def validator(text: str) -> bool:
        number = safe_float(text)
        if number is None:
            return False
        return number < limit

    return validator


def less_or_equal(limit: Number) -> Callable[[str], bool]:
    """
    Generates a validator function that checks if a number (string input)
    is less than or equal to the limit (<= limit).

    :param limit: The number to compare against (inclusive).
    :return: A validator function (Callable[[str], bool]).
    """

    def validator(text: str) -> bool:
        number = safe_float(text)
        if number is None:
            return False
        return number <= limit

    return validator
