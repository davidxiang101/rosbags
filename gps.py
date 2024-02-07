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
