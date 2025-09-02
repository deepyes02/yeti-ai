from langchain.agents import tool
import os
import requests
import json
import logging


@tool
def get_weather(city: str) -> dict:
    """Get the weather for a given city with comprehensive error handling. Returns a dictionary with a summary string and raw weather data."""
    # Input validation
    logging.warning(f"Function get weather called")
    if not city or not isinstance(city, str):
        return {"error": "Error: Please provide a valid city name."}
    city = city.strip()
    if not city:
        return {"error": "Error: City name cannot be empty."}
    # API key validation
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    if not WEATHER_API_KEY:
        return {"error": "Error: Weather API key is not configured."}
    try:
        # Construct API URL
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
        # Make API request with timeout
        response = requests.get(url, timeout=10)
        # Handle different HTTP status codes
        if response.status_code == 200:
            try:
                data = response.json()
                # Validate response structure
                if "location" not in data or "current" not in data:
                    return {"error": f"Error: Unexpected response format for {city}."}
                if "name" not in data["location"] or "temp_c" not in data["current"]:
                    return {"error": f"Error: Missing weather data for {city}."}
                # Extract data safely
                location = data["location"]["name"]
                temp_c = data["current"]["temp_c"]
                condition = data["current"].get("condition", {}).get("text", "")
                condition_icon = data["current"].get("condition", {}).get("icon", "")

                # Format response
                return data

            except json.JSONDecodeError:
                return {
                    "error": f"Error: Invalid response format from weather service for {city}."
                }
            except KeyError as e:
                return {
                    "error": f"Error: Missing expected data in weather response for {city}: {str(e)}"
                }

        elif response.status_code == 400:
            return {
                "error": f"Error: '{city}' is not a valid location. Please check the city name."
            }
        elif response.status_code == 401:
            return {"error": "Error: Weather API key is invalid or expired."}
        elif response.status_code == 403:
            return {
                "error": "Error: Access to weather API is forbidden. Check your API key permissions."
            }
        elif response.status_code == 429:
            return {
                "error": "Error: Too many requests to weather API. Please try again later."
            }
        elif response.status_code == 500:
            return {
                "error": "Error: Weather service is temporarily unavailable. Please try again later."
            }
        else:
            return {
                "error": f"Error: Weather service returned status {response.status_code}. Please try again later."
            }

    except requests.exceptions.Timeout:
        return {
            "error": f"Error: Request timeout while getting weather for {city}. Please try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": f"Error: Unable to connect to weather service for {city}. Check your internet connection."
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Error: Network error while getting weather for {city}: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Error: Unexpected error while getting weather for {city}: {str(e)}"
        }
