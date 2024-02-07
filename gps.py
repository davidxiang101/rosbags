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

# Function to detect laps based on crossing the start/finish line
def detect_laps(x, y, threshold=10):
    laps = []
    current_lap = []
    for i in range(len(x)):
        distance = np.sqrt(x[i]**2 + y[i]**2)  # Distance from start/finish
        if distance <= threshold:
            if current_lap:  # Avoid adding very first point if it's near start/finish
                laps.append(current_lap)
            current_lap = []
        current_lap.append((x[i], y[i]))
    if current_lap:  # Add the last lap if not empty
        laps.append(current_lap)
    return laps

# Assuming a threshold distance to the start/finish line (adjust as necessary)
threshold_distance = 10  # meters, adjust based on track and GPS accuracy

laps = detect_laps(x, y, threshold_distance)

# Plot each lap with a different color
plt.figure(figsize=(10, 6))
for i, lap in enumerate(laps):
    lap_x, lap_y = zip(*lap)  # Unpack coordinates
    plt.plot(lap_x, lap_y, label=f'Lap {i+1}')

plt.plot(0, 0, 'ro', label='Start/Finish Line')  # Mark the start/finish line
plt.xlabel('X Position (meters)')
plt.ylabel('Y Position (meters)')
plt.title('Racecar Trajectory Separated Into Laps')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()
