# Visualizes the grid of unique latitude and longitude points from a master CSV file using Folium.

import pandas as pd
import folium
import math
import statistics


MASTER_DATA_PATH = 'raw_data/September.csv'

MAP_CENTER = [41.0082, 28.9784]
MAP_ZOOM = 11

OUTPUT_FILE = 'maps/master_data_grid.html'

def visualize_master_grid(input_csv=MASTER_DATA_PATH, sample_size=None):
    
    chunk_size = 100000
    all_coords = set()
    total_rows = 0
    
    for chunk_num, chunk in enumerate(pd.read_csv(input_csv, chunksize=chunk_size), 1):
        unique_pairs = chunk[['LATITUDE', 'LONGITUDE']].drop_duplicates()
        
        for _, row in unique_pairs.iterrows():
            all_coords.add((row['LATITUDE'], row['LONGITUDE']))
        
        total_rows += len(chunk)
        
    
    grid_points = list(all_coords)
    
    
    if grid_points:
        lats = [p[0] for p in grid_points]
        lons = [p[1] for p in grid_points]
        
        center_lat = (min(lats) + max(lats)) / 2
        center_lon = (min(lons) + max(lons)) / 2
        
        sorted_lats = sorted(set(lats))
        sorted_lons = sorted(set(lons))
        
        lat_diffs = [sorted_lats[i+1] - sorted_lats[i] for i in range(len(sorted_lats)-1)]
        lon_diffs = [sorted_lons[i+1] - sorted_lons[i] for i in range(len(sorted_lons)-1)]
        
        lat_spacing = statistics.median([d for d in lat_diffs if d > 0])
        lon_spacing = statistics.median([d for d in lon_diffs if d > 0])
        
        lat_half = lat_spacing / 2
        lon_half = lon_spacing / 2
        
        lon_km = lon_spacing * 111 * math.cos(math.radians(center_lat))
    else:
        return None
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=MAP_ZOOM,
        tiles='OpenStreetMap'
    )
    
    for lat, lon in grid_points:
        square_corners = [
            [lat - lat_half, lon - lon_half],
            [lat - lat_half, lon + lon_half],
            [lat + lat_half, lon + lon_half],
            [lat + lat_half, lon - lon_half],
            [lat - lat_half, lon - lon_half],
        ]
        
        folium.Polygon(
            locations=square_corners,
            color='blue',
            weight=1,
            fillColor='lightblue',
            fillOpacity=0.3,
            popup=f"Grid Cell<br>Center: ({lat}, {lon})",
            tooltip=f"Grid Cell: ({lat}, {lon})"
        ).add_to(m)
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            popup=f"Grid Point<br>Lat: {lat}<br>Lon: {lon}",
            color='darkblue',
            weight=2,
            fillColor='blue',
            fillOpacity=0.8,
            tooltip=f"Data Point: ({lat}, {lon})"
        ).add_to(m)
    
    
    info_html = f'''
    <div style="position: fixed; 
         top: 10px; left: 50px; width: 250px; height: 80px; 
         background-color: white; z-index:9999; font-size:14px;
         border:2px solid grey; border-radius:5px; padding: 10px">
         <b>Master Data Grid Visualization</b><br>
         <small>Total unique grid points: {len(grid_points):,}</small><br>
         <small>Total rows processed: {total_rows:,}</small><br>
         <small>Grid spacing: {lat_spacing*111:.2f} km (lat) × {lon_km:.2f} km (lon)</small><br>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(info_html))
    
    m.save(OUTPUT_FILE)
    
    return m

if __name__ == '__main__':
    visualize_master_grid()

