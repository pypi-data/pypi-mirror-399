import re
from typing import Optional


def mask_phone_number(phone_number: Optional[str]) -> str:
    """Mask a Chinese phone number.

    keeping only the first 3 and the last 4 digits visible.

    Args:
        phone_number (str): The phone number to mask.

    Returns:
        str: A masked string like '138****5678'. Returns an empty string if
        input is not a string. Returns the original trimmed string if
        it doesn't match standard patterns.
    """
    if not isinstance(phone_number, str):
        return ""
    phone_number = phone_number.strip()

    if len(phone_number) == 11 and phone_number.isdigit():
        return re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", phone_number)

    if (
        phone_number.startswith("+86")
        and len(phone_number) == 14
        and phone_number[3:].isdigit()
    ):
        return re.sub(r"(\+86)(\d{3})\d{4}(\d{4})", r"\1\2****\3", phone_number)

    return phone_number
