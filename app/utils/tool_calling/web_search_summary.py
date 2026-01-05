from langchain_core.tools import Tool
import requests, logging, os
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
    """Search the web for the given query using Tavily and return a summary."""
    logger = logging.getLogger(__name__)
    raw_api_key = os.environ.get("TAVITY_SEARCH_API_KEY", "")
    
    # Clean the API key (strip quotes and whitespace)
    api_key = raw_api_key.strip().strip('"').strip("'")
    
    print("\n   " + "🔍" * 15)
    logger.info(f"   🔎  SEARCHING TAVILY: '{query}'")
    
    if not api_key:
        logger.error("   ❌  TAVITY_SEARCH_API_KEY NOT FOUND")
        return "Search is currently unavailable due to missing API key."

    try:
        # Tavily Search API endpoint
        url = "https://api.tavily.com/search"
        
        # Standard Tavily headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "search_depth": "basic",
            "max_results": 3
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
    except Exception as e:
        logger.error(f"   ❌  TAVILY SEARCH FAILED: {e}")
        return f"I could not search the web at this moment. Please try again later."

    if not results:
        logger.warning("   ⚠️  NO RESULTS FOUND")
        print("   " + "🔍" * 15 + "\n")
        return "No relevant search results found in the high valleys."

    logger.info(f"   ✅  FOUND {len(results)} RESULTS")
    output_parts = []
    
    for item in results:
        url = item.get("url")
        title = item.get("title", "No Title")
        content = item.get("content", "")
        
        if content:
            # Use Tavily's content, fallback to fetching if very short
            if len(content) < 200:
                logger.debug(f"   📄  Snippet short, fetching: {title[:30]}...")
                content = fetch_and_clean(url)
            
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
