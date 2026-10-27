from dotenv import load_dotenv
import os
import requests
from langchain.tools import tool


# Load the APIs
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# Custom weather api tool
@tool
def get_weather(city: str):
    """
    Search and get the weather data of any city.

    Args:
        city: which city weather you want to find
    """

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    try:
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code != 200:
            return f"Weather data failed to fetch: {resp.json().get('message', resp.text)}"

        data = resp.json()
        return {"weather": data['weather'][0]['main'],
                "temp": data['main']['temp'],
                "pressure": data['main']['pressure'],
                "humidity": data['main']['humidity']}
    except Exception:
        return "Get Weather tool unable to fetch the weather data"
