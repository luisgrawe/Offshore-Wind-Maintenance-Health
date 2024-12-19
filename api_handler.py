import requests
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
from datetime import datetime

class WeatherAPIHandler:
    
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

    def get_weather_data(self, latitude, longitude):
        """Fetches weather data from the OpenWeatherMap API for the given latitude and longitude."""
        
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
  
        
    def get_current_wind_speed(self, weather_data):
        """Extracts the current wind speed from the weather data."""

        current_wind_speed = weather_data['list'][0]['wind']['speed']
        return current_wind_speed
        
        
    def get_wind_speed_forecast(self, weather_data):
        """
        Extracts datetime and wind speed for the next 24 hours from the weather data and returns them as a Pandas DataFrame."""

        # Extract datetime and wind speed for the next 24 hours (first 8 entries as data is provided in 3-hour intervals)
        data = [
            {"datetime": entry["dt_txt"], "wind_speed": entry["wind"]["speed"]}
            for entry in weather_data["list"][:8]
        ]
    
        # Create DataFrame from the extracted data
        df = pd.DataFrame(data)
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.strftime('%m-%d %H')
        return df

    def fetch_wave_data(self, latitude, longitude):
        """Fetches wave height data from the Open-Meteo Marine API for the given latitude and longitude."""

        url = self.base_url  
        params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wave_height"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Parse wave height data, filter for the next 24 hours, and create a DataFrame; taken from open-meteo documentation at https://open-meteo.com/en/docs/marine-weather-api
        response = responses[0]
        hourly = response.Hourly()
        hourly_wave_height = hourly.Variables(0).ValuesAsNumpy()

        return hourly_wave_height, hourly

    def transform_wave_data_to_dataframe(self, wave_data, time_data):
        """Transforms the raw wave data into a DataFrame for the next 24 hours."""

        hourly_data = {
            "date": pd.date_range(
                start = pd.to_datetime(time_data.Time(), unit = "s", utc = True),
                end = pd.to_datetime(time_data.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = time_data.Interval()),
                inclusive = "left"
        )}
        hourly_data["wave_height"] = wave_data.round(2)
        hourly_dataframe = pd.DataFrame(hourly_data)
        current_time = pd.to_datetime(datetime.now(), utc=True)
        wave_forecast_df = hourly_dataframe[(hourly_dataframe['date'] >= current_time) & (hourly_dataframe['date'] <= current_time + pd.Timedelta(hours = 24))]

        return wave_forecast_df

        
    
