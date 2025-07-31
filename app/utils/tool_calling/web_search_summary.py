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
        return ""


def make_search_tool(model):
    def _search_and_summarize(query: str) -> str:
        logging.warning(f"Function search called")
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                if "href" in r:
                    results.append(r["href"])
                if len(results) == 3:
                    break

        summaries = []
        for url in results:
            content = fetch_and_clean(url)
            if content:
                prompt = f"Summarize the following content relevant to the question: '{query}'\n\n{content[:2000]}"
                try:
                    logging.warning("Model invoked to summarize individual URL")
                    summary = model.invoke(prompt)
                    summaries.append(
                        summary.content if hasattr(summary, "content") else summary
                    )

                except Exception:
                    logging.warning("Error during url search")
                    continue

        final_input = (
            "Combine and summarize these points. Make sure you do not repeat what is already said:\n\n"
            + "\n\n".join(summaries)
        )
        final_summary = model.invoke(final_input)
        return (
            final_summary.content
            if hasattr(final_summary, "content")
            else final_summary
        )

    return Tool.from_function(
        name="search_and_summarize",
        func=_search_and_summarize,
        description="Search the web and summarize the results to answer a user question. Do not repeat yourself when summarizing.",
    )
