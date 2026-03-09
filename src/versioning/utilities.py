"""Utility functions for safe nested dict/list access."""


def pull_from_config(x, *keys, fail_if_none=True):
    """Safely retrieve a nested value from a dict or list by sequential keys.

    Parameters
    ----------
    x : dict or list
        The top-level container to index into.
    *keys : str or int
        Sequence of keys or indices to apply in order. Use str for dict
        keys and int for list indices.
    fail_if_none : bool, default True
        If True, raise ValueError when the retrieved value is None.

    Returns
    -------
    The value at the specified path in x. If no keys are provided,
    returns x unchanged.

    Raises
    ------
    TypeError
        If a key is not str or int.
    KeyError
        If a str key is absent from its dict.
    IndexError
        If an int index is out of range for its list.
    ValueError
        If the value is None and fail_if_none is True.
    """
    working = x
    for i, key in enumerate(keys):
        prefix = f"Issue with key #{i + 1}:"
        if not isinstance(key, (str, int)):
            raise TypeError(
                f"{prefix} keys must be str or int, got {type(key).__name__}"
            )
        if isinstance(key, str):
            if not isinstance(working, dict) or key not in working:
                if not fail_if_none:
                    return None
                raise KeyError(f"{prefix} '{key}' not found in the sub-dict.")
            working = working[key]
        else:
            if not isinstance(working, (list, tuple)) or key >= len(working):
                if not fail_if_none:
                    return None
                length = len(working) if isinstance(working, (list, tuple)) else "N/A"
                raise IndexError(
                    f"{prefix} numeric index {key} is out of range (length {length})."
                )
            working = working[key]
        if fail_if_none and working is None:
            raise ValueError(f"{prefix} value is None.")
    return working
