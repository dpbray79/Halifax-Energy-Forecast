import requests
import json
import os
from datetime import datetime

# Halifax Coordinates
LAT = 44.6488
LON = -63.5752

def fetch_weather():
    print(f"Fetching weather for Halifax ({LAT}, {LON})...")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        output_path = os.path.join("public/data", "weather_raw.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Weather data saved to {output_path}")
        return data
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

if __name__ == "__main__":
    fetch_weather()
