# Maximum value for SQLite INTEGER
MAX_INT = 9223372036854775807


def dollars_to_cents(dollars):
    return int(float(dollars) * 100)


def cents_to_dollars(cents):
    return int(cents) / 100.0


def validate_int(value):
    try:
        value = int(value)
        if abs(value) > MAX_INT:
            raise ValueError(
                f"Value exceeds maximum limit {MAX_INT} for SQLite INTEGER."
            )
        return value
    except ValueError as e:
        raise ValueError(f"Invalid integer value: {e}") from e
    except TypeError as e:
        raise TypeError(f"Invalid integer type: {e}") from e


def validate_float(value):
    try:
        value = float(value)
        value_in_cents = dollars_to_cents(value)
        if abs(value_in_cents) > MAX_INT:
            raise ValueError(
                f"Value exceeds maximum limit {MAX_INT} for SQLite INTEGER."
            )
        return value
    except ValueError as e:
        raise ValueError(f"Invalid float value: {e}") from e
    except TypeError as e:
        raise TypeError(f"Invalid float type: {e}") from e
