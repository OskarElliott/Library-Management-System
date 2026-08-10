def to_text(value): # null from the database arrives as none, which no widget can display
    if value is None:
        return ""
    return str(value)