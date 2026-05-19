def is_non_empty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
