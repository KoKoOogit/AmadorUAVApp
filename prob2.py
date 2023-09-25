# %%
import numpy as np
import math

# %%
def read_from_file(filename):
    try:
        with open(filename, 'r') as file:
            altitude, current_gps_x, current_gps_y, N  = file.readline().strip().split()
            object_cordinates = []

            for _ in range(int(N)):
                x, y = map(float, file.readline().strip().split())
                object_cordinates.append([x,y])

            object_cordinates_array = np.array(object_cordinates)
            return  float(altitude), float(current_gps_x), float(current_gps_y), object_cordinates_array
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


filename = "pinpoint.in" 


# %%


# Define constants
FOV_VERTICAL = 15.6  # Vertical Field of View in degrees
FOV_HORIZONTAL = 23.4  # Horizontal Field of View in degrees
IMAGE_WIDTH = 5472  # Image width in pixels
IMAGE_HEIGHT = 3648  # Image height in pixels

# Get input data
altitude, drone_longitude, drone_latitude,object_coordinates = read_from_file("pinpoint.in")
drone_gps = (drone_longitude, drone_latitude)  # Current GPS coordinates of the drone
drone_altitude = altitude  # Altitude of the drone in meters


# Initialize an empty list to store GPS coordinates of objects
object_gps_coordinates = []

# Calculate angular resolution (degrees per pixel)
angular_resolution_vertical = FOV_VERTICAL / IMAGE_HEIGHT
angular_resolution_horizontal = FOV_HORIZONTAL / IMAGE_WIDTH



# Convert object_coordinates to a numpy array for vectorized calculations


# Calculate angles in degrees
angles_vertical = ((object_coordinates[:, 1] - IMAGE_HEIGHT / 2) * angular_resolution_vertical)
angles_horizontal = ((object_coordinates[:, 0] - IMAGE_WIDTH / 2) * angular_resolution_horizontal)

# Calculate distances in meters
distances_horizontal = drone_altitude * np.tan(np.radians(angles_horizontal))
distances_vertical = drone_altitude * np.tan(np.radians(angles_vertical))

# Calculate GPS coordinates of the objects relative to the drone
earth_radius = 6378137  # Earth's radius in meters
delta_longitude = np.degrees(distances_horizontal / (earth_radius * np.cos(np.radians(drone_latitude))))
delta_latitude = np.degrees(distances_vertical / earth_radius)

object_gps_coordinates = [
    (drone_gps[0] + dlon, drone_gps[1] + dlat)
    for dlon, dlat in zip(delta_longitude, delta_latitude)
]

# Print or use the object_gps_coordinates list

with open("pinpoint.out", "a") as f:
    for i, object_gps in enumerate(object_gps_coordinates):
        long, lat = object_gps
        f.write(f"{np.round(long,5)} {np.round(lat,5)}")
        if i < len(object_gps_coordinates) - 1:
            f.write('\n')  # Doesn't add balnk line in the end of file
 


