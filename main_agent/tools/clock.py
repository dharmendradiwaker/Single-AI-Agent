from langchain.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo


# Custom tool
@tool
def world_clock(timezone: str):
    """
    Get the current local time in a specific IANA timezone

    Use this whenever a user asks what time it is in a specific city or region.
    The timezone argument must be a valid IANA timezone name (e.g., 'America/New_York', 'Asia/Kolkata', 'Europe/London').
    """

    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)

        return now.strftime("Current time in %Z (%z): %Y-%m-%d %H:%M:%S")
    except Exception:
        return (
            f"Invalid timezone '{timezone}'. Please use a valid IANA timezone name."
        )
