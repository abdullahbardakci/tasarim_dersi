##This code is to get the weighted vehicle counts based on distance to road segments.


import pandas as pd
import math
import os
from main import ROAD_SEGMENTS

# Configuration
DATA_FOLDER = 'relevant_data'
OUTPUT_FOLDER = 'weighted_data'
SIGMA_KM = 0.5  # Standard deviation in km. 
                # Points 0.5km away will have their count reduced by ~40%.
                # Points 1.0km away will have their count reduced by ~87%.

def get_distance_point_to_segment(lat, lon, p1, p2):
    """
    Calculates the minimum distance (in km) from a point (lat, lon) 
    to a line segment defined by p1 and p2 (tuples of lat, lon).
    Uses a local flat-earth approximation.
    """
    # Convert lat/lon to approximate km offsets relative to p1
    # 1 deg lat ~= 111 km
    # 1 deg lon ~= 111 * cos(lat) km
    
    avg_lat_rad = math.radians((p1[0] + p2[0]) / 2)
    lon_scale = math.cos(avg_lat_rad)
    
    # Vector AB (segment)
    dx = (p2[1] - p1[1]) * 111 * lon_scale
    dy = (p2[0] - p1[0]) * 111
    
    # Vector AP (point to start)
    px = (lon - p1[1]) * 111 * lon_scale
    py = (lat - p1[0]) * 111
    
    # Project point onto line (parameter t)
    len_sq = dx*dx + dy*dy
    if len_sq == 0:
        return math.sqrt(px*px + py*py)
        
    t = (px * dx + py * dy) / len_sq
    
    # Clamp t to segment [0, 1]
    t = max(0, min(1, t))
    
    # Closest point on segment
    closest_x = t * dx
    closest_y = t * dy
    
    # Distance
    dist_km = math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    return dist_km

def get_min_distance_to_geometry(lat, lon, geometry):
    """Finds the shortest distance from point to any segment in the polyline."""
    min_dist = float('inf')
    
    for i in range(len(geometry) - 1):
        p1 = geometry[i]
        p2 = geometry[i+1]
        dist = get_distance_point_to_segment(lat, lon, p1, p2)
        if dist < min_dist:
            min_dist = dist
            
    return min_dist

def apply_weights_to_segment(segment_key):
    segment = ROAD_SEGMENTS[segment_key]
    
    if 'road_geometry' not in segment:
        print(f"Skipping {segment['name']}: No 'road_geometry' defined.")
        return

    filename = segment['output_filename']
    input_path = os.path.join(DATA_FOLDER, filename)
    
    if not os.path.exists(input_path):
        print(f"Skipping {segment['name']}: File {filename} not found.")
        return

    print(f"Processing {segment['name']}...")
    df = pd.read_csv(input_path)
    
    # We need to calculate weights for each unique location in the grid
    # To save time, we calculate unique weights first
    unique_locs = df[['LATITUDE', 'LONGITUDE']].drop_duplicates()
    weights = {}
    
    for _, row in unique_locs.iterrows():
        lat, lon = row['LATITUDE'], row['LONGITUDE']
        dist = get_min_distance_to_geometry(lat, lon, segment['road_geometry'])
        
        # Gaussian Weight: exp(-0.5 * (dist / sigma)^2)
        weight = math.exp(-0.5 * (dist / SIGMA_KM)**2)
        weights[(lat, lon)] = weight

    # Apply weights to the dataframe
    # We multiply NUMBER_OF_VEHICLES by the weight

    df['ORIGINAL_VEHICLES'] = df['NUMBER_OF_VEHICLES']
    df['WEIGHT_COEFFICIENT'] = df.apply(lambda row: weights.get((row['LATITUDE'], row['LONGITUDE']), 1.0), axis=1)
    df['NUMBER_OF_VEHICLES'] = (df['ORIGINAL_VEHICLES'] * df['WEIGHT_COEFFICIENT']).round().astype(int)
    
    
    # Save to a new file
    output_filename = f"weighted_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    df.to_csv(output_path, index=False)
    
    print(f"  -> Saved weighted data to {output_filename}")

if __name__ == '__main__':
    # You can process specific segments or all of them
    # apply_weights_to_segment('avcilar')
    
    for key in ROAD_SEGMENTS:
        apply_weights_to_segment(key)
