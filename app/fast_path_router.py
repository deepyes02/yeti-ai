import re
import logging
from app.utils.tool_calling.current_datetime import get_current_datetime
from app.utils.tool_calling.get_weather import get_weather
from app.utils.tool_calling.get_exchange_rates import get_exchange_rates
from app.utils.tool_calling.web_search_summary import search_web

logger = logging.getLogger(__name__)

async def process_fast_path(prompt: str):
    """
    Analyzes the prompt for specific keywords/patterns and executes fast-path tools.
    Returns the response string if successful, or None if it should fall back to the Agent.
    """
    prompt_lower = prompt.lower()
    fast_response = None
    
    # --- 1. TIME CHECK ---
    # Regex for explicit time questions
    time_pattern = r"\b(what time|current time|time now|tell me the time|time is it|time in)\b"
    
    if re.search(time_pattern, prompt_lower):
        logger.info("⚡  FAST PATH TRIGGERED: TIME")
        try:
            result = get_current_datetime.invoke({})
            fast_response = f"The current time is: **{result}**"
        except Exception as e:
            logger.warning(f"⚠️  Time tool execution failed: {e} -> DEFERRING TO AGENT")
            fast_response = None
        return fast_response

    # --- 2. WEATHER CHECK ---
    elif "weather" in prompt_lower:
        logger.info("⚡  FAST PATH TRIGGERED: WEATHER")
        
        # Default
        city = "Chiyoda, Tokyo"
        
        # Regex extraction
        # Handle: "weather in London", "weather like in London", "weather for London"
        match = re.search(r"weather(?:.*)(?:in|for)\s+([a-zA-Z\s]+)", prompt_lower) 
        
        if match:
            raw_city = match.group(1).strip()
            # Clean up common tail phrases
            for filler in [" right now", " please", " today", " tomorrow", " like", "?"]:
                raw_city = raw_city.replace(filler, "")
            city = raw_city.strip()
        else:
            match_pre = re.search(r"([a-zA-Z\s]+) weather", prompt_lower)
            if match_pre:
                 candidate = match_pre.group(1).strip()
                 # Stricter filter: City names usually aren't 10 words long
                 if len(candidate.split()) <= 3 and candidate not in ["current", "the", "check", "get", "show", "tell me", "what's the", "what is the"]:
                     city = candidate

        logger.info(f"📍  EXTRACTED CITY: {city}")
        
        try:
            data = get_weather.invoke({"city": city})
            
            # VALIDATION: Check for tool errors
            is_error = False
            if isinstance(data, dict) and data.get("error"):
                is_error = True
            elif isinstance(data, str) and "error" in data.lower():
                is_error = True
                
            if is_error:
                 logger.info(f"⚠️  Weather tool returned error for '{city}' -> DEFERRING TO AGENT")
                 fast_response = None
            else:
                if isinstance(data, dict) and "location" in data:
                     curr = data['current']
                     fast_response = f"### 🌤️ Weather in {data['location']['name']}\n\n**Temperature:** {curr['temp_c']}°C\n**Condition:** {curr['condition']['text']}\n**Humidity:** {curr['humidity']}%\n**Wind:** {curr['wind_kph']} kph"
                else:
                    fast_response = str(data)
        except Exception as e:
            logger.warning(f"⚠️  Weather tool execution failed: {e} -> DEFERRING TO AGENT")
            fast_response = None
        return fast_response

    # --- 3. CURRENCY CHECK ---
    elif any(x in prompt_lower for x in ["rate", "exchange", "convert", "jpy", "inr", "usd", "eur"]):
        logger.info("⚡  FAST PATH TRIGGERED: EXCHANGE RATE")
        
        from_curr = None
        to_curr = None
        
        # Regex 1
        match = re.search(r"\b([A-Za-z]{3})\b\s+(?:to|in|into)\s+\b([A-Za-z]{3})\b", prompt_lower)
        if match:
            from_curr = match.group(1).upper()
            to_curr = match.group(2).upper()
        else:
            # Regex 2
            match_lazy = re.search(r"rate\s+\b([A-Za-z]{3})\b\s+\b([A-Za-z]{3})\b", prompt_lower)
            if match_lazy:
                 from_curr = match_lazy.group(1).upper()
                 to_curr = match_lazy.group(2).upper()

        valid_fast_path = False
        supported_pairs = [
            # JPY base
            ("JPY", "NPR"), ("JPY", "INR"), ("JPY", "USD"), ("JPY", "BDT"),
            ("JPY", "IDR"), ("JPY", "VND"), ("JPY", "PHP"),
            # CAD base
            ("CAD", "PHP"), ("CAD", "VND"),
            # SGD base
            ("SGD", "PHP"), ("SGD", "VND"),
            # USD base
            ("USD", "PHP"), ("USD", "VND")
        ]

        if from_curr and to_curr:
            if (from_curr, to_curr) in supported_pairs:
                valid_fast_path = True
            else:
                logger.info(f"⚠️  Pair {from_curr}-{to_curr} not in whitelist -> DEFERRING TO AGENT")
        else:
            logger.info("⚠️  No clear currencies found -> DEFERRING TO AGENT")

        if valid_fast_path:
            logger.info(f"💱  EXTRACTED PAIR: {from_curr} -> {to_curr}")
            try:
                result = get_exchange_rates.invoke({"from_currency": from_curr, "to_currency": to_curr})
                
                # Double check the result for error messages
                if isinstance(result, str) and "Sorry" in result:
                     logger.info("⚠️  Tool logic error -> DEFERRING TO AGENT")
                     fast_response = None
                elif isinstance(result, dict) and result.get("error"):
                     logger.info("⚠️  Tool error response -> DEFERRING TO AGENT")
                     fast_response = None
                else:
                    if isinstance(result, dict) and "summary" in result:
                        fast_response = result["summary"]
                    else:
                        fast_response = str(result)
            except Exception as e:
                logger.warning(f"⚠️  Exchange tool execution failed: {e} -> DEFERRING TO AGENT")
                fast_response = None
        return fast_response

    # --- 4. SEARCH DWC CHECK ---
    elif "search" in prompt_lower and "digital wallet" in prompt_lower:
         logger.info("⚡  FAST PATH TRIGGERED: SEARCH DWC")
         try:
            result = search_web("Digital Wallet Corporation")
            if "error" in str(result).lower():
                logger.info("⚠️  Search tool returned error -> DEFERRING TO AGENT")
                fast_response = None
            else:
                fast_response = result
         except Exception as e:
            logger.warning(f"⚠️  Search tool execution failed: {e} -> DEFERRING TO AGENT")
            fast_response = None
         return fast_response

    return None
