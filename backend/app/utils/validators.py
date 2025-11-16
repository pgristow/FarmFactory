"""
Custom validation functions for API requests
"""
from typing import Optional
from decimal import Decimal
from datetime import date, datetime
import re


def validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> bool:
    """
    Validate geographic coordinates

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if coordinates are valid
    """
    if latitude is None and longitude is None:
        return True

    if latitude is None or longitude is None:
        return False

    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_npk_ratio(npk_ratio: str) -> bool:
    """
    Validate NPK ratio format (e.g., "10-10-10", "20-5-10")

    Args:
        npk_ratio: NPK ratio string

    Returns:
        True if format is valid
    """
    pattern = r'^\d+\-\d+\-\d+$'
    return bool(re.match(pattern, npk_ratio))


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that start date is before or equal to end date

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        True if date range is valid
    """
    return start_date <= end_date


def validate_positive_decimal(value: Decimal) -> bool:
    """
    Validate that a decimal value is positive

    Args:
        value: Decimal value to validate

    Returns:
        True if value is positive
    """
    return value >= 0


def validate_ph_level(ph: Decimal) -> bool:
    """
    Validate pH level (0-14)

    Args:
        ph: pH value

    Returns:
        True if pH is in valid range
    """
    return 0 <= ph <= 14


def validate_percentage(value: Decimal) -> bool:
    """
    Validate percentage value (0-100)

    Args:
        value: Percentage value

    Returns:
        True if value is valid percentage
    """
    return 0 <= value <= 100


def validate_timezone(timezone: str) -> bool:
    """
    Validate timezone string

    Args:
        timezone: Timezone string (e.g., "America/New_York")

    Returns:
        True if timezone is valid
    """
    try:
        import pytz
        return timezone in pytz.all_timezones
    except ImportError:
        # If pytz is not available, just check basic format
        pattern = r'^[A-Za-z_]+/[A-Za-z_]+$'
        return bool(re.match(pattern, timezone)) or timezone == "UTC"


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input by trimming whitespace

    Args:
        value: String to sanitize
        max_length: Optional maximum length

    Returns:
        Sanitized string
    """
    sanitized = value.strip()
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address

    Returns:
        True if email format is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension

    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.csv', '.xlsx'])

    Returns:
        True if file extension is allowed
    """
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)
