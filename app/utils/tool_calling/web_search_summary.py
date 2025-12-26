from langchain_core.tools import Tool
from duckduckgo_search import DDGS
import requests, logging
from bs4 import BeautifulSoup


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def fetch_and_clean(url):
    try:
        r = requests.get(url, timeout=5)
        return clean_html(r.text)
    except Exception as e:
        return "Error fetching the internet"


def make_search_tool():
    def _search_and_summarize(query: str) -> str:
        logging.warning(f"Function search called for query: {query}")
        results = []
        with DDGS() as ddgs:
            # Get top 3 results
            for r in ddgs.text(query, max_results=3):
                if "href" in r:
                    results.append({"url": r["href"], "title": r.get("title", "No Title")})

        if not results:
            return "No relevant search results found in the high valleys."

        output_parts = []
        for item in results:
            url = item["url"]
            title = item["title"]
            logging.warning(f"Fetching content from: {url}")
            content = fetch_and_clean(url)
            
            if content:
                # Truncate content to keep context size manageable but informative
                snippet = content[:1500].strip()
                output_parts.append(f"Source: {title} ({url})\nContent: {snippet}\n---")

        return "\n\n".join(output_parts)

    return Tool.from_function(
        name="web_search",
        func=_search_and_summarize,
        description="Search the high valleys of the internet for real-time information. Use this when the user's quest requires knowledge beyond your eternal memories.",
    )
