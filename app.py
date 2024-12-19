import matplotlib
matplotlib.use('Agg')  # Required to run matplotlib in a headless environment, as it caused an error in the Flask app
from flask import Flask, request, render_template
from api_handler import WeatherAPIHandler
from safety_assessment import SafetyAssessment
from data import DataHandler
from sorting import quicksort, partition
import os
import openmeteo_requests
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io
from datetime import datetime



app = Flask(__name__)

# Initialize DataHandler and a dictionary of wind farms with their coordinates
data_handler = DataHandler('Global-Wind-Power-Tracker-June-2024.csv') 
wind_farm_dict = data_handler.process_data()

@app.route('/')
def home():
    # Pass the wind farm names to the template so they can be selected by the user
    wind_farm_names = list(wind_farm_dict.keys())

    # Using a quicksort algorithm to sort the wind farm names for an easier user experience
    quicksort(wind_farm_names, 0, len(wind_farm_names) - 1)
    return render_template('index.html', wind_farm_names=wind_farm_names)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        # Get user input from form (selected wind farm name)
        wind_farm_name = request.form.get('wind_farm')

    except Exception as e:
        return render_template('result.html', status="Error", details=f"Failed to retrieve user input: {str(e)}")
    
    try:
        # Get the latitude and longitude of the selected wind farm from the dictionary
        latitude, longitude = wind_farm_dict[wind_farm_name]

    except Exception as e:
        return render_template('result.html', status="Error", details=f"Error retrieving wind farm coordinates: {str(e)}")
    
    try:
        # Initialize OpenWeatherMap client for wind data
        key = "48eec2e7aada76fe1e272381a7a7edad"  # API key for OpenWeatherMap
        url_wind = "https://api.openweathermap.org/data/2.5/forecast"
        handler_wind = WeatherAPIHandler(url_wind, api_key=key)

        # Fetch wind data using the OpenWeatherMap API via handler_weather
        weather_data = handler_wind.get_weather_data(latitude, longitude)

        # Fetch current wind speed and wind speed forecast for the next 24 hours
        current_wind_speed = handler_wind.get_current_wind_speed(weather_data)
        wind_speed_forecast = handler_wind.get_wind_speed_forecast(weather_data)
        
    except Exception as e:
        return render_template('result.html', status="Error", details=f"Error fetching wind speed data: {str(e)}")
    
    try:
        # Initialize Open-Meteo client for wave data (no API key needed)
        url_wave = "https://marine-api.open-meteo.com/v1/marine"
        handler_wave = WeatherAPIHandler(url_wave)  

        # Fetch wave data using the Open-Meteo API via handler_wave
        wave_data, time_data = handler_wave.fetch_wave_data(latitude, longitude)
        
        # Transform the wave data into a DataFrame for the next 24 hours
        wave_forecast_df = handler_wave.transform_wave_data_to_dataframe(wave_data, time_data)
        
    except Exception as e:
        return render_template('result.html', status="Error", details=f"Error fetching or processing wave data: {str(e)}")
    
    try:
        # Plot wave height data using the wave forecast
        wave_plot_url = data_handler.create_graph(wave_forecast_df, 'Wave Height Development Over Next 24 Hours', 'Time', 'Wave Height (m)', 'date', 'wave_height', 'blue', 'Wave Height (m)', 3)

    except Exception as e:
        return render_template('result.html', status="Error", details=f"Error plotting wave height data: {str(e)}")
    
    try:
        # Plot wind speed over the next 24 hours
        wind_plot_url = data_handler.create_graph(wind_speed_forecast, 'Wind Speed Development Over Next 24 Hours', 'Time', 'Wind Speed (m/s)', 'datetime', 'wind_speed', 'red', 'Wind Speed (m/s)', 12.5)
     
    except Exception as e:
        return render_template('result.html', status="Error", details=f"Error plotting wind speed data: {str(e)}")
    
    try:
        # Initialize SafetyAssessment object with selected wind and wave thresholds
        assessment = SafetyAssessment(wind_threshold=12.5, wave_threshold=3)

        # Evaluate safety based on wind speed and wave height
        status, details = assessment.evaluate_safety(current_wind_speed, wave_forecast_df['wave_height'].iloc[0]) 
        details += f"<br>Current Wind Speed: {current_wind_speed} m/s"
        details += f"<br>Current Wave Height: {wave_forecast_df['wave_height'].iloc[0]} m"

        # Return the result to the user along with the plot images
        return render_template('result.html', 
                               status=status, 
                               details=details, 
                               wind_speed=current_wind_speed, 
                               wave_height=wave_forecast_df['wave_height'].iloc[0],
                               plot_url=wave_plot_url,
                               wind_plot_url=wind_plot_url,
                               name=wind_farm_name)
    except Exception as e:
        return render_template('result.html', status="Error", details=f"Error evaluating safety: {str(e)}")


if __name__ == "__main__":
    app.run(debug=False, port=5000, threaded=True)
