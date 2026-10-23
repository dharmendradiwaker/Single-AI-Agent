from dotenv import load_dotenv
import getpass
import os
import requests
from langchain.tools import tool





# Load the APIs 
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")



# Custom weather api tool
@tool
def get_weather(city):

    """ 
    Search and get the weather data of any city.

    Args: 
        city: which city weather you want to find
    """

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    
    try:
        data = requests.get(url, params=params, timeout=10)
        
        if data.status_code != 200:
            return f"Weather Data failed to fatch: {data.json().get('message', data.text)}"
        

        data = data.json()
        weather = data['weather'][0]['main']
        Temp = data['main']['temp']
        Pressure = data['main']['pressure']
        humidity = data['main']['humidity']

        data = {"weather": weather,
                "temp": Temp,
                "Pressure": Pressure,
                "humidity": humidity}
        return data
    except:
        return f"Get Weather tool unable to fetch the weather data"