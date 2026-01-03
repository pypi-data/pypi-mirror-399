import pathlib
from typing import Optional, Union

from .messages import print_verbose


def sql_quotename(
    name: Optional[str] = None,
    brackets: bool = True,
    ticks: bool = False,
    verbose: bool = False,
) -> str:
    """
    Quote a SQL Server name string with brackets or ticks.

    Args:
        name: The name to quote. Must be a non-empty string.
        brackets: If True, wraps the name in square brackets [name].
        ticks: If True, wraps the name in single quotes 'name'.
            Takes precedence over brackets if both are True.
        verbose: If True, prints error messages.

    Returns:
        The quoted name string.

    Raises:
        ValueError: If name is None or empty after stripping.
        TypeError: If name is not a string.

    Examples:
        >>> sql_quotename('table_name')
        '[table_name]'
        >>> sql_quotename('table_name', brackets=False, ticks=True)
        "'table_name'"
    """
    if name is None:
        print_verbose("No name provided; exiting sql_quotename.", verbose)
        raise ValueError("name must be provided")
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must be a non-empty string")

    return_value = cleaned.replace("[", "").replace("]", "")
    if brackets:
        return_value = f"[{return_value}]"
    if ticks or not brackets:
        return_value = f"'{return_value}'"
    return return_value


def pathing(
    input: Optional[Union[str, pathlib.Path]], verbose: bool = False
) -> pathlib.Path:
    """
    Standardize and validate a path string or Path object.

    Args:
        input: The path to standardize (string or pathlib.Path). Must not be None.
        verbose: If True, prints error messages.

    Returns:
        A pathlib.Path object if the path exists.

    Raises:
        ValueError: If input is None or the path does not exist.
        TypeError: If input is not a string or pathlib.Path.
    """
    if input is None:
        print_verbose("No path provided; exiting pathing.", verbose)
        raise ValueError("path input must be provided")

    if isinstance(input, str):
        normalized = input.replace("\\", "/")
        path_obj = pathlib.Path(normalized)
    elif isinstance(input, pathlib.Path):
        path_obj = input
    else:
        raise TypeError("input must be a string or pathlib.Path")

    if path_obj.exists():
        return path_obj

    print_verbose(f"Path {path_obj} does not exist; exiting pathing.", verbose)
    raise ValueError(f"Path does not exist: {path_obj}")
