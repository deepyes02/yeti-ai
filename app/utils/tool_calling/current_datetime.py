from datetime import datetime
from langchain_core.tools import Tool


def make_datetime_tool():
    def _get_current_datetime(_: str = "") -> str:
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        return current_datetime

    return Tool.from_function(
        name="get_current_datetime",
        func=_get_current_datetime,
        description="Returns the current date and time. Useful for answering questions about the present moment or scheduling events.",
    )
