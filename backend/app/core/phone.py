import re
from typing import Tuple, Optional

def normalize_and_validate_phone(phone: str, country_code: str = "+91") -> Tuple[str, str]:
    """
    Validates and normalizes phone numbers.
    - Supports India (+91) with standard 10-digit mobile starting with 6, 7, 8, or 9.
    - Extensible to international phone numbers following the E.164 standard (+ followed by 7-15 digits).
    - Returns a tuple of (normalized_e164_phone, country_code).
    - Raises ValueError with clear user-facing explanation if invalid.
    """
    if not phone or not isinstance(phone, str):
        raise ValueError("Phone number is required.")

    # Remove formatting characters (spaces, hyphens, parentheses, periods)
    raw = re.sub(r"[\s\-\(\)\.]+", "", phone.strip())
    if not raw:
        raise ValueError("Phone number cannot be empty.")

    # Determine default country code
    def_code = (country_code or "+91").strip()
    if not def_code.startswith("+"):
        def_code = f"+{def_code}"

    # If the input explicitly begins with '+', validate as full international E.164
    if raw.startswith("+"):
        if not re.match(r"^\+[1-9]\d{7,14}$", raw):
            raise ValueError("Invalid international phone number format. Must follow standard format (e.g. +919876543210).")

        # Specific validation for India (+91)
        if raw.startswith("+91"):
            national_part = raw[3:]
            if len(national_part) != 10 or national_part[0] not in "6789" or not national_part.isdigit():
                raise ValueError("Invalid Indian mobile number. Please enter a valid 10-digit number starting with 6, 7, 8, or 9.")
            return raw, "+91"

        # General valid international number
        # Try to infer country code from raw
        match = re.match(r"^(\+[1-9]\d{0,3})(\d{6,14})$", raw)
        inferred_code = match.group(1) if match else def_code
        return raw, inferred_code

    # Input without leading '+'. Handle based on country_code
    # Strip any leading zeros
    digits = raw.lstrip("0")

    if def_code == "+91":
        # Check if user entered "91" prefix without '+'
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]

        if len(digits) != 10 or digits[0] not in "6789" or not digits.isdigit():
            raise ValueError("Invalid Indian mobile number. Please enter a valid 10-digit number starting with 6, 7, 8, or 9.")

        return f"+91{digits}", "+91"
    else:
        # International country code specified
        full_e164 = f"{def_code}{digits}"
        if not re.match(r"^\+[1-9]\d{7,14}$", full_e164):
            raise ValueError(f"Invalid phone number for country code {def_code}.")
        return full_e164, def_code

def mask_phone_number(phone: Optional[str]) -> str:
    """
    Masks a phone number for privacy display (e.g. +91 98****3210).
    """
    if not phone:
        return "Not configured"
    phone_clean = phone.strip()
    if len(phone_clean) <= 6:
        return "****"
    prefix = phone_clean[:5]
    suffix = phone_clean[-3:]
    return f"{prefix}****{suffix}"
