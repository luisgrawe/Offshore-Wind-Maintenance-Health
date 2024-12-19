class SafetyAssessment:
    def __init__(self, wind_threshold, wave_threshold):
        self.wind_threshold = wind_threshold
        self.wave_threshold = wave_threshold

    def evaluate_safety(self, weather_data, wave_data):
        """Evaluate the safety of working conditions based on weather and wave data."""
        wind_speed = weather_data
        wave_height = wave_data

        if wind_speed > self.wind_threshold and wave_height > self.wave_threshold:
            return "Unsafe", f"Wind speed is {wind_speed} m/s and wave height is {wave_height}, which both exceed the safety threshold."
        
        if wind_speed > self.wind_threshold and wave_height <= self.wave_threshold:
            return "Caution", f"Wind speed is {wind_speed} m/s, which exceeds the threshold. Wave height is {wave_height} m, which is within the safe range."

        if wind_speed <= self.wind_threshold and wave_height > self.wave_threshold:
            return "Caution", f"Wave height is {wave_height} m, which exceeds the threshold. Wind speed is {wind_speed} m/s, which is within the safe range."

        if wave_height <= self.wave_threshold and wind_speed <= self.wind_threshold:
            return "Safe", "Conditions are safe for work."
