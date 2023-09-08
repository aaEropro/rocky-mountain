
def bool(value:str) -> bool:    # takes a string and verifies if is a boolean
    return value.lower() in ("yes", "true", "t", "1")