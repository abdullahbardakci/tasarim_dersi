import pandas as pd
import folium
import os
import statistics
from main import ROAD_SEGMENTS

SEGMENT_KEY = 'avcilar'  

def create_map_for_segment(segment_key):
    
    if segment_key not in ROAD_SEGMENTS:
        print(f"Segment not found in segments")
        return None
    
    segment = ROAD_SEGMENTS[segment_key]
    grid_points = segment.get('grid_points')
    output_filename = segment['output_filename']
    
    if not grid_points:
        print(f"No grid points for the segment")
        return None
    
    data_folder = 'relevant_data'
    csv_path = os.path.join(data_folder, output_filename)
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found.")
        return None
    
    lats = [p[0] for p in grid_points]
    lons = [p[1] for p in grid_points]
    
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    sorted_lats = sorted(set(lats))
    sorted_lons = sorted(set(lons))
    
    lat_diffs = []
    for i in range(len(sorted_lats) - 1):
        difference = sorted_lats[i+1] - sorted_lats[i]
        if difference > 0:
            lat_diffs.append(difference)

    lon_diffs = []
    for i in range(len(sorted_lons) - 1):
        difference = sorted_lons[i+1] - sorted_lons[i]
        if difference > 0:
            lon_diffs.append(difference)

    if lat_diffs and lon_diffs:
        lat_spacing = statistics.median(lat_diffs)
        lon_spacing = statistics.median(lon_diffs)
    else:
        lat_spacing = 0.0054931641
        lon_spacing = 0.0109863281
    
    lat_half = lat_spacing / 2
    lon_half = lon_spacing / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
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
            color='red',
            weight=2,
            fillColor='red',
            fillOpacity=0.1,
            popup=f"Grid Cell<br>Center: ({lat}, {lon})",
            tooltip=f"Grid Cell"
        ).add_to(m)
        
    unique_locations = df.groupby(['LATITUDE', 'LONGITUDE']).agg({
        'AVERAGE_SPEED': 'mean',
        'NUMBER_OF_VEHICLES': 'mean',
        'MAXIMUM_SPEED': 'max',
        'DATE_TIME': 'count'
    }).reset_index()
    unique_locations.columns = ['LATITUDE', 'LONGITUDE', 'AVG_SPEED', 'AVG_VEHICLES', 'MAX_SPEED', 'DATA_POINTS']
    
    print(f"Unique locations: {len(unique_locations)}")

    min_speed_in_grid = unique_locations['AVG_SPEED'].min()
    max_speed_in_grid = unique_locations['AVG_SPEED'].max()

    def get_radius(speed):
        if max_speed_in_grid == min_speed_in_grid:
            return 8
            
        normalized = (speed - min_speed_in_grid) / (max_speed_in_grid - min_speed_in_grid)
        return 8 + ((1 - normalized) * 12)

    def get_color(speed):
        if speed < 30:
            return 'red'
        elif speed < 50:
            return 'orange'
        elif speed < 70:
            return 'yellow'
        else:
            return 'green'
    
    for idx, row in unique_locations.iterrows():
        popup_text = f"""
        <b>Location</b><br>
        Lat: {row['LATITUDE']:.6f}<br>
        Lon: {row['LONGITUDE']:.6f}<br>
        <b>Traffic Stats:</b><br>
        Avg Speed: {row['AVG_SPEED']:.1f} km/h<br>
        Max Speed: {row['MAX_SPEED']:.0f} km/h<br>
        Avg Vehicles: {row['AVG_VEHICLES']:.0f}<br>
        """
        
        current_speed = row['AVG_SPEED']
        
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=get_radius(current_speed),
            popup=folium.Popup(popup_text, max_width=300),
            color='black',
            weight=1,
            fillColor=get_color(current_speed),
            fillOpacity=0.8,
            tooltip=f"Speed: {current_speed:.1f} km/h"
        ).add_to(m)
    
    legend_html = '''
    <div style="position: fixed; 
         bottom: 60px; left: 50px; width: 180px; height: 190px; 
         background-color: white; z-index:9999; font-size:14px;
         border:2px solid grey; border-radius:5px; padding: 10px">
         <p><b>Speed Legend</b></p>
         <p><i class="fa fa-circle" style="color:red"></i> &lt; 30 km/h</p>
         <p><i class="fa fa-circle" style="color:orange"></i> 30-50 km/h</p>
         <p><i class="fa fa-circle" style="color:yellow"></i> 50-70 km/h</p>
         <p><i class="fa fa-circle" style="color:green"></i> &gt; 70 km/h</p>
         <hr>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    title_html = f'''
    <div style="position: fixed; 
         top: 10px; left: 50px; width: 200px; height: 60px; 
         background-color: white; z-index:9999; font-size:14px;
         border:2px solid grey; border-radius:5px; padding: 10px">
         <b>{segment['name']}</b><br>
         <small>Total Points: {len(df):,}</small><br>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    maps_folder = 'maps'
    
    map_filename = output_filename.replace('.csv', '_map.html')
    map_path = os.path.join(maps_folder, map_filename)
    m.save(map_path)
    
    return m

if __name__ == '__main__':
    if SEGMENT_KEY is None:
        for key in ROAD_SEGMENTS:
            create_map_for_segment(key)
    else:
        create_map_for_segment(SEGMENT_KEY)