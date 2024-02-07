from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr
import numpy as np

lateral_accelerations = []

with Reader('bags/tum_performance_gps') as reader:
    for connection, timestamp, rawdata in reader.messages():
        if connection.topic == '/vectornav/imu_uncompensated':
            msg = deserialize_cdr(rawdata, connection.msgtype)
            # Extract lateral (y-axis) acceleration
            lateral_acceleration = msg.linear_acceleration.y
            lateral_accelerations.append(lateral_acceleration)

# Convert to a NumPy array for analysis
lateral_accelerations = np.array(lateral_accelerations)

mean_lateral_acc = np.mean(lateral_accelerations)
max_lateral_acc = np.max(lateral_accelerations)
min_lateral_acc = np.min(lateral_accelerations)

print(f"Mean Lateral Acceleration: {mean_lateral_acc} m/s^2")
print(f"Max Lateral Acceleration: {max_lateral_acc} m/s^2")
print(f"Min Lateral Acceleration: {min_lateral_acc} m/s^2")

import matplotlib.pyplot as plt

plt.plot(lateral_accelerations)
plt.title('Lateral Acceleration Over Time')
plt.xlabel('Sample Number')
plt.ylabel('Lateral Acceleration (m/s^2)')
plt.show()



