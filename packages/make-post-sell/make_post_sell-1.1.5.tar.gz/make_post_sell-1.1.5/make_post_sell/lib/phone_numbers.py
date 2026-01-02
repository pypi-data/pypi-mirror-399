def is_phone_number_valid(phone_number):
    """Test if user phone_number meets our criteria for validity."""
    # Choices here are subject to change.
    # allow dashes.
    phone_number = phone_number.replace("-", "")
    # allow period.
    phone_number = phone_number.replace(".", "")
    # allow spaces.
    phone_number = phone_number.replace(" ", "")
    # allow left parethesis.
    phone_number = phone_number.replace("(", "")
    # allow right parethesis.
    phone_number = phone_number.replace(")", "")

    # must be left with only digits.
    if not phone_number.isdigit():
        return False

    # must be at least 10 digits.
    if len(phone_number) < 10:
        return False

    return True
