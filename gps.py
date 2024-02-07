from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr
import numpy as np
import matplotlib.pyplot as plt

# Initialize lists to store latitude and longitude
latitudes = []
longitudes = []

with Reader('bags/tum_performance_gps') as reader:
    for connection, timestamp, rawdata in reader.messages():
        if connection.topic == '/vectornav/gnss':
            msg = deserialize_cdr(rawdata, connection.msgtype)
            latitudes.append(msg.latitude)
            longitudes.append(msg.longitude)

def latlon_to_local(latitudes, longitudes, origin_lat, origin_lon):
    # Earth's radius in meters
    R = 6378137
    
    # Convert degrees to radians
    lat_rad = np.radians(latitudes)
    lon_rad = np.radians(longitudes)
    origin_lat_rad = np.radians(origin_lat)
    origin_lon_rad = np.radians(origin_lon)
    
    # Calculate differences
    dlat = lat_rad - origin_lat_rad
    dlon = lon_rad - origin_lon_rad
    
    # Convert latitude and longitude differences to meters
    x = dlon * R * np.cos(origin_lat_rad)
    y = dlat * R
    
    return x, y

# Starting line coordinates in decimal degrees
origin_lat = 45.618972  # Updated origin latitude
origin_lon = 9.281167   # Updated origin longitude

x, y = latlon_to_local(latitudes, longitudes, origin_lat, origin_lon)

def detect_laps(x, y, threshold=2, cooldown=3):
    laps = []
    current_lap = []
    lap_in_progress = False
    cooldown_counter = 0  # Counter to manage cool-down period
    
    for i in range(len(x)):
        distance = np.sqrt(x[i]**2 + y[i]**2)  # Distance from start/finish
        if distance <= threshold and not lap_in_progress:
            if current_lap:  # Avoid adding very first point if it's near start/finish
                current_lap.append((x[i], y[i]))
                laps.append(current_lap)
                current_lap = []
            lap_in_progress = True
            cooldown_counter = cooldown  # Reset cooldown counter
        elif lap_in_progress and cooldown_counter > 0:
            cooldown_counter -= 1  # Decrement cooldown counter
        elif lap_in_progress and cooldown_counter == 0:
            lap_in_progress = False  # End cool-down period, allow detecting next lap
        
        current_lap.append((x[i], y[i]))
        
    if current_lap:  # Add the last lap if not empty
        laps.append(current_lap)
        
    return laps

laps = detect_laps(x, y)

import matplotlib.pyplot as plt

# Number of laps
num_laps = len(laps)

# Determine the layout size
cols = 2  # For example, arrange plots in 2 columns
rows = num_laps // cols + (num_laps % cols > 0)  # Calculate required rows

plt.figure(figsize=(15, rows * 5))  # Adjust figure size as needed

for i, lap in enumerate(laps):
    lap_x, lap_y = zip(*lap)  # Unpack coordinates
    ax = plt.subplot(rows, cols, i+1)  # Create a subplot for each lap
    ax.plot(lap_x, lap_y, marker='.', markersize=2, linestyle='-', label=f'Lap {i+1}')
    ax.plot(0, 0, 'ro', label='Start/Finish Line')  # Mark the start/finish line
    ax.set_xlabel('X Position (meters)')
    ax.set_ylabel('Y Position (meters)')
    ax.set_title(f'Lap {i+1}')
    ax.legend()
    ax.axis('equal')
    ax.grid(True)

plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()
