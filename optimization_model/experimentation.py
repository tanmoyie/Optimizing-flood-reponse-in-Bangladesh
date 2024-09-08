from optimization_model.vrp_tw import VRPTWData, VRPTWModel, VRPNetworkPlot
# Instantiate and solve the problem# Instantiate and solve the problem
data = VRPTWData()
vrp_model = VRPTWModel(data)
vrp_model.solve()
vrp_model.print_solution()

# Plot the solution
plot = VRPNetworkPlot(data, vrp_model.vehicle_routes)
plot.create_graph()
plot.draw()

#%%
# Calculate distance
import numpy as np
from scipy.spatial import distance_matrix
import re
# Define coordinates for the depot and 20 customers
np.random.seed(42)
coordinates = np.random.rand(21, 2) * 100  # Random points in a 100x100 area
print('coord', coordinates)

import re

# Example list of POINT strings (no commas between lat and lon)
points = ["POINT(29.9792 31.1342)", "POINT(48.8584 2.2945)", "POINT(40.6892 -74.0445)"]

# Function to convert POINT to a list of strings without commas
#%%
import re
from geopy.distance import geodesic

# Function to parse POINT(lat lon) into (lat, lon)
def parse_point(point_str):
    # Regular expression to extract latitude and longitude
    point_pattern = re.compile(r"POINT \(([-\d.]+) ([-\d.]+)\)")
    match = point_pattern.match(point_str)
    if match:
        lat_str, lon_str = match.groups()
        return float(lat_str), float(lon_str)
    else:
        raise ValueError(f"Invalid POINT format: {point_str}")

# Example POINT strings
point1_str = "POINT (91.36133329228886 23.01)"
point2_str = "POINT (91.28653656990846 22.9)"
import math
latitude_in_degrees = latitude_in_radians * 180 / math.pi

# Convert POINT strings to latitude and longitude tuples
point1 = parse_point(point1_str)
point2 = parse_point(point2_str)

# Calculate geodesic distance
distance_km = geodesic(point1, point2).kilometers

# Store the result in a dictionary
distance_dict = {
    'Point1_to_Point2': distance_km,
    'Coordinates_Point1': point1,
    'Coordinates_Point2': point2
}

print(distance_dict)


#%%
# Calculate the distance matrix
distance_matrix = distance_matrix(coordinates, coordinates)

# Convert to integer type
distance_matrix = distance_matrix.astype(int)

print("Distance Matrix:")
print(distance_matrix)
