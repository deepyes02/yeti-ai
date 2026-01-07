from datetime import datetime
from langchain_core.tools import tool
import logging


@tool
def get_current_datetime():
    """Return the current date and time. Use ONLY when the user explicitly asks for the current date or time. Do NOT use this for greetings or general conversation."""
    logger = logging.getLogger(__name__)
    logger.info("🕐 Getting current date and time")
    
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info(f"✅ Current datetime: {current_datetime}")
    return current_datetime
