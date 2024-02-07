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

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.cm import viridis
from matplotlib.colors import Normalize

# Curvature calculation function
def calculate_curvature(x, y):
    dx = np.gradient(x)
    dy = np.gradient(y)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)
    curvature = np.abs(dx * ddy - dy * ddx) / np.power(dx**2 + dy**2, 1.5)
    curvature[np.isnan(curvature)] = 0
    curvature[np.isinf(curvature)] = 0
    return curvature

# Assuming 'laps' is your list of laps with each lap being a list of (x, y) tuples
# Example: laps = [[(x1, y1), (x2, y2), ...], [...], ...]

# Create the main window
root = tk.Tk()
root.title("Lap Plots with Curvature")

# Create a tab control
tabControl = ttk.Notebook(root)

# For each lap, create a tab with a plot showing curvature
for i, lap in enumerate(laps):
    lap_x, lap_y = zip(*lap)  # Unpack coordinates
    lap_x = np.array(lap_x)
    lap_y = np.array(lap_y)
    
    # Calculate curvature
    curvature = calculate_curvature(lap_x, lap_y)
    norm = Normalize(vmin=min(curvature), vmax=max(curvature))

    # Creating a tab for each lap
    tab = ttk.Frame(tabControl)
    tabControl.add(tab, text=f'Lap {i+1}')
    
    # Creating a figure for the plot
    fig, ax = plt.subplots(figsize=(6, 4))
    scatter = ax.scatter(lap_x, lap_y, c=curvature, cmap='viridis', norm=norm, s=10)  # Adjust size with `s`
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label('Curvature')
    ax.plot(0, 0, 'ro', markersize=5, label='Start/Finish Line')  # Mark the start/finish line
    ax.set_title(f'Lap {i+1} Curvature')
    ax.set_xlabel('X Position (meters)')
    ax.set_ylabel('Y Position (meters)')
    ax.axis('equal')

    # Embedding the plot in the GUI
    canvas = FigureCanvasTkAgg(fig, master=tab)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

tabControl.pack(expand=1, fill="both")

root.mainloop()
