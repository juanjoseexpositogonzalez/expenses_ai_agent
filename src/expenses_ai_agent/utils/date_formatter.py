from datetime import datetime

from zoneinfo import ZoneInfo


def format_datetime(dt: str, output_tz: str = "Europe/Madrid") -> str:
    """Format a datetime string to DD/MM/YYYY HH:MM format.

    Args:
        dt (str): Datetime in ISO 8601 format. If no timezone offset is provided,
                 output_tz will be assumed.
        output_tz (str): IANA timezone name for the output. Defaults to "Europe/Madrid".

    Returns:
        str: The formatted date string in DD/MM/YYYY HH:MM format.
    """
    # Parse the datetime string using fromisoformat (Python 3.7+)
    try:
        parsed_dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        # If parsing fails, try without timezone info
        parsed_dt = datetime.fromisoformat(dt)
        # If no timezone info, assume the output timezone
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=ZoneInfo(output_tz))

    # Convert to the desired output timezone
    if parsed_dt.tzinfo is not None:
        output_timezone = ZoneInfo(output_tz)
        parsed_dt = parsed_dt.astimezone(output_timezone)

    return parsed_dt.strftime("%d/%m/%Y %H:%M")
