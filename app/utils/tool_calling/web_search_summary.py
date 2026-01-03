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


def search_web(query: str) -> str:
    """Search the web for the given query and return a summary."""
    logger = logging.getLogger(__name__)
    print("\n   " + "🔍" * 15)
    logger.info(f"   🔎  SEARCHING WEB: '{query}'")
    
    results = []
    results = []
    try:
        with DDGS() as ddgs:
            # Get top 3 results
            for r in ddgs.text(query, max_results=3):
                if "href" in r:
                    results.append({"url": r["href"], "title": r.get("title", "No Title")})
    except Exception as e:
        logger.error(f"   ❌  SEARCH FAILED: {e}")
        return f"I could not search the web at this moment (Rate Limit or Error: {str(e)}). Please try again later."

    if not results:
        logger.warning("   ⚠️  NO RESULTS FOUND")
        print("   " + "🔍" * 15 + "\n")
        return "No relevant search results found in the high valleys."

    logger.info(f"   ✅  FOUND {len(results)} RESULTS")
    output_parts = []
    for item in results:
        url = item["url"]
        title = item["title"]
        logger.debug(f"   📄  READING: {title[:30]}...")
        content = fetch_and_clean(url)
        
        if content:
            # Truncate content to keep context size manageable but informative
            snippet = content[:1500].strip()
            output_parts.append(f"Source: {title} ({url})\nContent: {snippet}\n---")
    
    logger.info(f"   📚  SUMMARY COMPILED from {len(output_parts)} sources")
    print("   " + "🔍" * 15 + "\n")
    return "\n\n".join(output_parts)


def make_search_tool():
    return Tool.from_function(
        name="web_search",
        func=search_web,
        description="Search the high valleys of the internet for real-time information. Use this when the user's quest requires knowledge beyond your eternal memories.",
    )
