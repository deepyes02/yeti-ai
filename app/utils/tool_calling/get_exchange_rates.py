from langchain.agents import tool
import os, requests, json


@tool
def get_exchange_rates(from_currency: str, to_currency: str):
    """Get exchange rate for a given currency pair. Currently available source currency is USD to JPY and JPY to NPR, BDT, INR, PHP, IDR and VND."""
    EXCHANGE_JP = os.getenv("EXCHANGE_JP")
    if not EXCHANGE_JP:
        raise ValueError("EXCHANGE_JP environment variable is not set.")
    response = requests.get(EXCHANGE_JP)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    response_json = response.json()
    rates = json.loads(response_json["Rates"])
    currency = rates["ALL_ALL_ALL"]["Currency"]

    exchange_rate_data = []
    for value in currency:
        data = currency[value]
        exchange_rate_data.append(
            {
                "sender_unit": float(1),
                "sender_currency": data["From"],
                "receiver_unit": float(data["SellingRate"]),
                "receiver_currency": data["To"],
            }
        )
    for rate in exchange_rate_data:
        if (
            rate["sender_currency"] == from_currency
            and rate["receiver_currency"] == to_currency
        ):
            summary = f"The exchange rate from {from_currency} to {to_currency} is {rate['receiver_unit']}."
            return {"summary": summary, "raw": exchange_rate_data}
    return f"Sorry we don't have exchange rate for {from_currency} to {to_currency}."
