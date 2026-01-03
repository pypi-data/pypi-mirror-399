from typing import Optional

from .dialects import Dialect


def quote_identifier(name: Optional[str], dialect: Dialect = Dialect.SQLSERVER) -> str:
    """
    Quote an identifier for the given SQL dialect.

    Args:
        name: Identifier to quote; must be non-empty string.
        dialect: Target SQL dialect.

    Returns:
        Quoted identifier string.

    Raises:
        ValueError: If name is missing/empty.
        TypeError: If name is not a string.
        NotImplementedError: If dialect is unsupported.
    """
    if name is None:
        raise ValueError("name must be provided")
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must be a non-empty string")

    if dialect == Dialect.SQLSERVER:
        return f"[{cleaned.replace('[', '').replace(']', '')}]"
    if dialect == Dialect.POSTGRES:
        escaped = cleaned.replace('"', '""')
        return f'"{escaped}"'
    if dialect == Dialect.MYSQL:
        escaped = cleaned.replace("`", "``")
        return f"`{escaped}`"
    if dialect == Dialect.DUCKDB:
        escaped = cleaned.replace('"', '""')
        return f'"{escaped}"'

    raise NotImplementedError(f"Dialect not supported: {dialect}")
