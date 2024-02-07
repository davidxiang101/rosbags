from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr

# Initialize lists to store latitude and longitude
latitudes = []
longitudes = []

with Reader('/path/to/your/rosbag2_file') as reader:
    for connection, timestamp, rawdata in reader.messages():
        if connection.topic == '/vectornav/gnss':
            msg = deserialize_cdr(rawdata, connection.msgtype)
            latitudes.append(msg.latitude)
            longitudes.append(msg.longitude)


import numpy as np

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

# Assuming the first GPS coordinate is the origin
origin_lat = latitudes[0]
origin_lon = longitudes[0]

x, y = latlon_to_local(latitudes, longitudes, origin_lat, origin_lon)


