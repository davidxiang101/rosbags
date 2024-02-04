import pandas as pd
from rosbag2_py import Reader, StorageOptions, ConverterOptions

# Define the path to your ROS bag
bag_file_path = '/path/to/your/rosbag2_file'

# Setup storage options for reading the bag
storage_options = StorageOptions(uri=bag_file_path, storage_id='sqlite3')

# No conversion is needed since we're reading raw data
converter_options = ConverterOptions('', '')

# Initialize a reader
reader = Reader()
reader.open(storage_options, converter_options)

# Move to the first topic
if reader.has_next():
    # Assuming you know the topic name and message type
    topic_name = '/vectornav/imu'
    message_type = 'sensor_msgs/msg/Imu'

    # Create an empty list to hold your data
    data = []

    # Iterate through the bag
    while reader.has_next():
        (topic, msg, t) = reader.read_next()
        if topic == topic_name:
            # Extract the data you're interested in
            # For IMU, let's say we want the linear acceleration and angular velocity
            msg_dict = {
                'time': t,
                'linear_acceleration_x': msg.linear_acceleration.x,
                'linear_acceleration_y': msg.linear_acceleration.y,
                'linear_acceleration_z': msg.linear_acceleration.z,
                'angular_velocity_x': msg.angular_velocity.x,
                'angular_velocity_y': msg.angular_velocity.y,
                'angular_velocity_z': msg.angular_velocity.z
            }
            data.append(msg_dict)

# Convert the list of dicts to a Pandas DataFrame
df = pd.DataFrame(data)

# Now you can save this DataFrame to CSV, or work with it directly
df.to_csv('imu_data.csv', index=False)

