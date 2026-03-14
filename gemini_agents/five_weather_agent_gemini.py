"""
Weather Agent using Gemini + Visual Crossing Timeline Weather API
Interactive Q&A mode — type 'exit' to quit.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain import hub
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "false"

api_key                = os.getenv('GEMINI_API_KEY')
model                  = os.getenv('GEMINI_MODEL')
VISUALCROSSING_API_KEY = os.getenv('VISUALCROSSING_API_KEY', 'your_api_key_here')

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"


# ---------------------------------------------------------------------------
# Tool 1 — Current weather
# ---------------------------------------------------------------------------
@tool
def get_current_weather(location: str) -> str:
    """Get current weather information for a location. Input is a city name."""
    try:
        import requests

        url = (
            f"{BASE_URL}/{location}/today"
            f"?unitGroup=metric"
            f"&include=current,days"
            f"&key={VISUALCROSSING_API_KEY}"
            f"&contentType=json"
        )
        response = requests.get(url)

        if response.status_code == 200:
            data    = response.json()
            current = data.get('currentConditions', {})
            days    = data.get('days', [{}])[0]

            return f"""
Current Weather in {data.get('resolvedAddress')}:
- Temperature   : {current.get('temp')}°C
- Feels Like    : {current.get('feelslike')}°C
- Min / Max     : {days.get('tempmin')}°C / {days.get('tempmax')}°C
- Humidity      : {current.get('humidity')}%
- Pressure      : {current.get('pressure')} hPa
- Condition     : {current.get('conditions', 'N/A')}
- Wind Speed    : {current.get('windspeed')} km/h
- Wind Direction: {current.get('winddir')}°
- Cloud Cover   : {current.get('cloudcover')}%
- Visibility    : {current.get('visibility')} km
- UV Index      : {current.get('uvindex')}
- Dew Point     : {current.get('dew')}°C
- Sunrise       : {current.get('sunrise', 'N/A')}
- Sunset        : {current.get('sunset', 'N/A')}
            """.strip()
        else:
            return f"Could not fetch weather data. Status: {response.status_code} — {response.text}"

    except Exception as e:
        return f"Error fetching weather: {str(e)}"


# ---------------------------------------------------------------------------
# Tool 2 — 5-day forecast
# ---------------------------------------------------------------------------
@tool
def get_forecast(location: str) -> str:
    """Get 5-day weather forecast for a location. Input is a city name."""
    try:
        import requests

        url = (
            f"{BASE_URL}/{location}/next5days"
            f"?unitGroup=metric"
            f"&include=days"
            f"&key={VISUALCROSSING_API_KEY}"
            f"&contentType=json"
        )
        response = requests.get(url)

        if response.status_code == 200:
            data          = response.json()
            forecast_info = f"5-Day Forecast for {data.get('resolvedAddress')}:\n"

            for i, day in enumerate(data.get('days', [])[:5]):
                forecast_info += f"""
Day {i + 1} ({day.get('datetime', 'N/A')}):
  Temperature   : {day.get('temp')}°C (feels like {day.get('feelslike')}°C)
  Min / Max     : {day.get('tempmin')}°C / {day.get('tempmax')}°C
  Condition     : {day.get('conditions', 'N/A')}
  Description   : {day.get('description', 'N/A')}
  Humidity      : {day.get('humidity')}%
  Wind Speed    : {day.get('windspeed')} km/h
  Precipitation : {day.get('precipprob', 0)}% chance / {day.get('precip', 0)} mm
  Snow          : {day.get('snow', 0)} cm
  UV Index      : {day.get('uvindex')}
  Sunrise       : {day.get('sunrise', 'N/A')}
  Sunset        : {day.get('sunset', 'N/A')}
"""
            return forecast_info.strip()
        else:
            return f"Could not fetch forecast data. Status: {response.status_code} — {response.text}"

    except Exception as e:
        return f"Error fetching forecast: {str(e)}"


# ---------------------------------------------------------------------------
# Tool 3 — Compare weather between two cities
# ---------------------------------------------------------------------------
@tool
def compare_weather(locations: str) -> str:
    """Compare weather between two locations. Input is two city names separated by a comma."""
    try:
        import requests

        parts = [loc.strip() for loc in locations.split(",")]
        if len(parts) != 2:
            return "Please provide exactly two locations separated by a comma, e.g. 'Paris,Tokyo'"

        comparison = "Weather Comparison:\n"

        for city in parts:
            url = (
                f"{BASE_URL}/{city}/today"
                f"?unitGroup=metric"
                f"&include=current,days"
                f"&key={VISUALCROSSING_API_KEY}"
                f"&contentType=json"
            )
            response = requests.get(url)

            if response.status_code == 200:
                data    = response.json()
                current = data.get('currentConditions', {})
                days    = data.get('days', [{}])[0]

                comparison += f"""
{data.get('resolvedAddress')}:
  Temperature : {current.get('temp')}°C (feels like {current.get('feelslike')}°C)
  Min / Max   : {days.get('tempmin')}°C / {days.get('tempmax')}°C
  Condition   : {current.get('conditions', 'N/A')}
  Humidity    : {current.get('humidity')}%
  Wind Speed  : {current.get('windspeed')} km/h
  UV Index    : {current.get('uvindex')}
"""
            else:
                comparison += f"\n{city}: Failed to fetch (status {response.status_code})\n"

        return comparison.strip()

    except Exception as e:
        return f"Error comparing weather: {str(e)}"


# ---------------------------------------------------------------------------
# LangChain / Gemini agent setup
# ---------------------------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0.7,
    google_api_key=api_key
)

tools  = [get_current_weather, get_forecast, compare_weather]
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


# ---------------------------------------------------------------------------
# Interactive Q&A loop
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("   🌤️  Weather Assistant (powered by Visual Crossing)")
    print("=" * 60)
    print("Ask me anything about the weather!")
    print("Examples:")
    print("  • What's the weather in Tokyo?")
    print("  • Give me a 5-day forecast for Paris")
    print("  • Compare weather between London and New York")
    print("\nType 'exit' or 'quit' to stop.\n")
    print("-" * 60)

    chat_history = []   # stores {"role": ..., "content": ...} for context

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            print("   ⚠️  Please enter a question.")
            continue

        if user_input.lower() in {"exit", "quit", "bye", "goodbye"}:
            print("\n👋 Goodbye! Stay weather-aware!")
            break

        # Build input with conversation history as context
        history_text = ""
        if chat_history:
            history_text = "\n\nPrevious conversation:\n"
            for turn in chat_history[-6:]:   # keep last 3 exchanges (6 messages)
                role  = "User"  if turn["role"] == "user" else "Assistant"
                history_text += f"{role}: {turn['content']}\n"
            history_text += "\nNow answer the latest question using the above context if relevant."

        full_input = user_input + history_text

        print("\n🤖 Assistant: ", end="", flush=True)
        try:
            result = executor.invoke({"input": full_input})
            answer = result.get("output", "Sorry, I couldn't process that.")
            print(answer)

            # Save to history
            chat_history.append({"role": "user",      "content": user_input})
            chat_history.append({"role": "assistant",  "content": answer})

        except Exception as e:
            print(f"❌ Error: {str(e)}")

        print("-" * 60)


if __name__ == "__main__":
    main()
