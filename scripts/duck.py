from duckduckgo_search import DDGS

query = (
    "Send money to Nepal"
    "site:smileswallet.com OR site:digitalwallet.global OR site:smilesconnect.com"
)
with DDGS() as ddgs:
    results = ddgs.text(query, max_results=10)
print(results)
