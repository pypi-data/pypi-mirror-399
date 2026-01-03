from typing import Any, List


def flatten(nest: List[Any]) -> List[Any]:
    """
    Flatten a nested list recursively to a single-level list.

    Args:
        nest: A potentially nested list structure.

    Returns:
        A flat list containing all elements from the nested structure.

    Examples:
        >>> flatten([1, [2, 3], [[4], 5]])
        [1, 2, 3, 4, 5]
        >>> flatten([1, 2, 3])
        [1, 2, 3]
    """
    if not isinstance(nest, list):
        raise TypeError("nest must be a list")

    result = []
    for item in nest:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
