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

plt.figure(figsize=(10, 6))
plt.plot(x, y, label='Trajectory', marker='.', markersize=2, linestyle='-')
plt.plot(0, 0, marker='o', markersize=5, color='red', label='Starting Line')  # Mark the starting line
plt.xlabel('X Position (meters)')
plt.ylabel('Y Position (meters)')
plt.title('Racecar Trajectory with Monza Starting Line as Origin')
plt.legend()
plt.axis('equal')  # Ensures equal aspect ratio
plt.grid(True)
plt.show()
