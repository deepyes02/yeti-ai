from datetime import datetime
from langchain_core.tools import tool
import logging


@tool
def get_current_datetime():
    """Return the current date and time as a string when user asks for date or time."""
    logging.warning(f"Function get current date and time called")
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_datetime
