import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

class DataHandler:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = self.load_data()

    def load_data(self):
        """Load data from the CSV file."""
        data = pd.read_csv(self.csv_file)
        return data
    
    def get_offshore_wind_data(self):
        """Filter the data for offshore wind farms that are operating."""
        offshore_data = self.data[self.data['Installation Type'].str.contains('offshore', case=False, na=False)]
        offshore_data = offshore_data[offshore_data['Status'] == 'operating']
        offshore_data = offshore_data[['Project Name', 'Latitude', 'Longitude']]
        return offshore_data
    
    def process_data(self):
        """Create a dictionary with wind farm names as keys and coordinates (Latitude, Longitude) as tuple values."""
        offshore_data = self.get_offshore_wind_data()
        wind_farm_dict = {
            row['Project Name']: (row['Latitude'], row['Longitude'])
            for _, row in offshore_data.iterrows()
        }
        return wind_farm_dict
    
    def create_graph(self, df, title, xlabel, ylabel, xaxis, yaxis, color, label, threshold):
        """Create a line graph from the given DataFrame and return it as a base64 encoded string."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df[xaxis], df[yaxis], label=label, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.axhline(y=threshold, color=color, linestyle='--', linewidth=1)
        plt.xticks(rotation=45, ha='right')  # Rotate labels by 45 degrees

        # Save the plot to a BytesIO object
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png')
        img_stream.seek(0)
        plot_url = base64.b64encode(img_stream.getvalue()).decode('utf8')
        return plot_url
