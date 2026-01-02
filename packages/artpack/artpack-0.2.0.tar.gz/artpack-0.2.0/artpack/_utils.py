"""Internal utility functions for artpack."""

import re
from typing import Any
from matplotlib import colors as mcolors


###############################################################################
# Type validation
###############################################################################
def _check_type(
    param_name: str, param: Any, expected_type: type | tuple[type, ...]
) -> bool:
    """
    Internal type checker for dev. Raises if invalid.

    Parameters
    ----------
    param_name : str, required
        Name of the parameter to be checked in the parent function.
    param : Any, required
        Object to check the type of
    expected_type : type or tuple of types, required
        The expected type(s) to check `param` against.

    Raises
    ------
    TypeError
        If type of `param` does not match the `expected_type` value.

    Returns
    -------
    bool
        Returns True if `param` matches the `expected_type`.
    """
    if not isinstance(param, expected_type):
        expected_type_name = (
            "`" + expected_type.__name__ + "`"
            if isinstance(expected_type, type)
            else " or ".join("`" + t.__name__ + "`" for t in expected_type)
        )

        actual_type_name = type(param).__name__

        raise TypeError(
            f"`{param_name}` should be of type {expected_type_name}.\n"
            f"You've supplied a `{actual_type_name}` object"
        )


###############################################################################
# Color validation
###############################################################################
def _is_valid_color(param_name: str, color: str):
    """
    Internal check to validate color string (hex or matplotlib named). Raises if invalid.

    Parameters
    ----------
    param_name : str
        Name of the color parameter to be checked in the parent function

    color : str
        Color string to validate

    Raises
    ------
    ValueError
        If color is not a valid hexadecimal webcolor or a named matplotlib color.

    """
    # Give a helpful type error message
    if not isinstance(color, str):
        _check_type(param_name, color, str)

    # Check if it's a valid hex color (6 or 3 digits)
    hex_color = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
    invalid_hex_color = not re.match(hex_color, color)

    # Check if it's a named matplotlib color
    invalid_matplotlib_color = color.lower() not in mcolors.CSS4_COLORS

    if invalid_hex_color and invalid_matplotlib_color:
        raise ValueError(
            f"`{param_name}` must be a valid hex color (#RRGGBB or #RGB) "
            f"or a named matplotlib color.\nYou've supplied: '{color}'"
        )


###############################################################################
# Positive Numeric Values
###############################################################################
"""
Internal validator for positive int/float values. Raises on invalid.

Parameters
----------
param_name: str
    Name of the number parameter to be checked in the parent function.
number : float, int
    Number to check

Raises
------
ValueError
    If number is not a positive float or integer.

Returns
-------
bool
    True if valid positive int or float
"""


def _is_positive_number(param_name: str, number: float | int) -> bool:
    if not isinstance(number, (int, float)) or number <= 0:
        raise ValueError(
            f"`{param_name}` must be a positive integer or float (number with decimals).\nYou've supplied: `{number}`"
        )


###############################################################################
# Minimum numeric values
###############################################################################
"""
Internal validator for minimum n_points in *_data functions. Raises on invalid.

Parameters
----------
number : int
    Number to check

min_points : int
    Minimum allowed value for the number of points used to approximate a shape.

shape : str
    Name of the shape being validated (used for error messages or context). Must be a non-empty string.

Raises
------
ValueError
    If `number` is not greater than or equal to `min_points`.

Returns
-------
bool
    True if `number` is greater than or equal to `min_points`.
"""


def _check_min_points(number: int, min_points: int, shape: str) -> bool:
    if shape is None or not isinstance(shape, str) or not shape:
        raise TypeError(
            "`shape` must be a non-empty string identifying the shape (e.g., 'circle')."
        )
    if not isinstance(number, int) or number < min_points:
        raise ValueError(
            f"`n_points` must be >= {min_points} for a reasonable approximation of a {shape}.\nYou've supplied: `{number}`"
        )
    return True
