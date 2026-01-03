from langchain.agents import tool
import os, requests, json
import logging


@tool
def get_exchange_rates(from_currency: str, to_currency: str):
    """Get exchange rate for a given currency pair. Currently available source currency is USD to JPY and JPY to NPR, BDT, INR, PHP, IDR and VND."""
    logger = logging.getLogger(__name__)
    logger.info(f"💱 Getting exchange rate: {from_currency} → {to_currency}")

    # Input validation
    if not all(
        [
            from_currency,
            to_currency,
            isinstance(from_currency, str),
            isinstance(to_currency, str),
        ]
    ):
        logger.warning(f"❌ Invalid currency input: {from_currency} → {to_currency}")
        return {"error": "Error: Please provide valid 'from' and 'to' currency codes."}

    EXCHANGE_JP = os.getenv("EXCHANGE_JP")
    if not EXCHANGE_JP:
        return {"error": "Error: EXCHANGE_JP environment variable is not configured."}

    try:
        response = requests.get(EXCHANGE_JP, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

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

        from_currency_upper = from_currency.upper()
        to_currency_upper = to_currency.upper()

        for rate in exchange_rate_data:
            if (
                rate["sender_currency"] == from_currency_upper
                and rate["receiver_currency"] == to_currency_upper
            ):
                summary = f"The exchange rate from {from_currency_upper} to {to_currency_upper} is {rate['receiver_unit']}."
                logger.info(f"✅ Exchange rate found: {from_currency_upper} → {to_currency_upper} = {rate['receiver_unit']}")
                return {"summary": summary, "raw": exchange_rate_data}

        logger.warning(f"⚠️  No exchange rate available for {from_currency_upper} → {to_currency_upper}")
        return {
            "error": f"Sorry, we don't have an exchange rate for {from_currency_upper} to {to_currency_upper}."
        }

    except requests.exceptions.Timeout:
        return {"error": "Error: Request timeout while getting exchange rates."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Error: HTTP error from exchange rate service: {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error: Network error while getting exchange rates: {e}"}
    except (json.JSONDecodeError, KeyError) as e:
        return {
            "error": f"Error: Could not parse the response from the exchange rate service: {e}"
        }
    except Exception as e:
        return {"error": f"Error: An unexpected error occurred: {e}"}
