import pandas as pd
import os

# --- INPUT CONFIGURATION ---
INPUT_FILES = [
    'raw_data/june.csv',
    'raw_data/April.csv',
    'raw_data/September.csv' # Added September for School Opening
]

# Define the exact dates we want to capture
# We use strings for easy comparison after converting to date
HOLIDAYS_TO_EXTRACT = {
    'Ramadan_Feast': ['2024-04-10', '2024-04-11', '2024-04-12'],
    'Sacrifice_Feast': ['2024-06-16', '2024-06-17', '2024-06-18', '2024-06-10'],
    'School_Opening': ['2024-09-09', '2024-09-10', '2024-09-11','2024-09-12','2024-09-13'],
}

# Flatten the dictionary values into a single list for the filter
ALL_HOLIDAY_DATES = [date for dates in HOLIDAYS_TO_EXTRACT.values() for date in dates]

# --- ROAD SEGMENTS ---
# (Using your provided ROAD_SEGMENTS dictionary)
ROAD_SEGMENTS = {
    'mecidiyekoy_d100': {
        'name': 'Mecidiyeköy D100',
        'grid_points': [
            (41.0641479492188, 28.9874267578125),
            (41.0696411132813, 28.9874267578125),
            (41.0641479492188, 28.9984130859375),
            (41.0641479492188, 29.0093994140625),
            (41.0696411132813, 29.0093994140625)
        ],
        'road_geometry': [
            (41.067182876360135, 28.98215768289143),
            (41.066502096679706, 28.996652709932523),
            (41.066870394042816, 29.010029912119386) 
        ],
        'output_filename': 'Mecidiyekoy_D100.csv',
    },
    'besiktas_meydan': {
        'name': 'Besiktas Meydan',
        'grid_points': [
            (41.0421752929688, 29.0093994140625)
        ],
        'road_geometry': [
            (41.041547423801894, 29.0040906695881),
            (41.043937064646315, 29.014436643156362)
        ],
        'output_filename': 'Besiktas_Meydan.csv',
    },
    'kopru': {
        'name': '15 Temmuz Köprüsü',
        'grid_points': [
            (41.0476684570313, 29.0313720703125),
            (41.0421752929688, 29.0313720703125),
            (41.0421752929688, 29.0423583984375)
        ],
        'road_geometry': [
            (41.0407267606662, 29.03917836678557),
            (41.04983196056567, 29.02968830103479)
        ],
        'output_filename': 'kopru.csv',
    },
    'buyukdere': {
        'name': 'Buyukdere',
        'grid_points': [
            (41.0861206054688, 29.0093994140625),
            (41.0806274414063, 29.0093994140625),
            (41.0806274414063, 29.0093994140625)
        ],
        'road_geometry': [
            (41.08633384273805, 29.007006849366046),
            (41.08535310553135, 29.007423228765294),
            (41.078293683837586, 29.012975956962265),
        ],
        'output_filename': 'Buyukdere.csv',
    },
    'cendere': {
        'name': 'Cendere Yolu',
        'grid_points': [
            (41.0806274414063, 28.9764404296875),
            (41.0861206054688, 28.9764404296875),
            (41.0861206054688, 28.9874267578125),
            (41.0916137695313, 28.9874267578125),
        ],
        'road_geometry': [
            (41.0801939407255, 28.975130232849637),
            (41.08357027188313, 28.976991474401203),
            (41.089551656529615, 28.984825051573196),
            (41.0912164812101, 28.985090943338836)
        ],
        'output_filename': 'cendere.csv',
    },
    'avcilar': {
        'name': 'Avcılar Metrobüs',
        'grid_points': [
            (40.9982299804688, 28.7017822265625),
            (40.9927368164063, 28.7127685546875),
            (40.9872436523438, 28.7127685546875),
            (40.9872436523438, 28.7237548828125)
        ],
        'road_geometry': [
            (40.98583172130115, 28.721995915589016),
            (40.99869821987855, 28.699997098937985)
        ],
        'output_filename': 'avcilar.csv',
    },
    'beylikduzu': {
        'name': 'Beylikdüzü E5',
        'grid_points': [
            (41.0092163085938, 28.6578369140625),
            (41.0092163085938, 28.6468505859375),
            (41.0147094726563, 28.6468505859375),
            (41.0147094726563, 28.6358642578125)
        ],
        'road_geometry': [
            (41.01691183367701, 28.63720453966137),
            (41.00655953054434, 28.665063278971022)
        ],
        'output_filename': 'beylikduzu.csv',
    },   
        'okmeydani': {
        'name': 'Okmeydanı - TEM Bağlantısı',
        'grid_points': [
            (41.0586547851563, 28.9654541015625),
            (41.0531616210938, 28.9544677734375)
        ],
        'road_geometry': [
            (41.05041382625551, 28.94844384864544),
            (41.056999249970794, 28.962363548496498),
            (41.06047129894944, 28.966094875149416)
        ],
        'output_filename': 'okmeydani.csv',
    },
        'kadikoy': {
        'name': 'Kadıköy - Rıhtım',
        'grid_points': [
            (40.9927368164063, 29.0313720703125),
            (40.9927368164063, 29.0203857421875),
        ],
        'road_geometry': [
            (40.99602861741476, 29.02437520867931),
            (40.992809975882146, 29.024842111678193),
            (40.99142379717707, 29.024188447479755),
            (40.99046050328627, 29.029293253600944),
            (40.99264734680128, 29.034911267063638)
        ],
        'output_filename': 'kadikoy.csv',
    },
        'altunizade': {
        'name': 'Altunizade - D100',
        'grid_points': [
            (41.0366821289063, 29.0423583984375),
            (41.0311889648438, 29.0423583984375),
            (41.0256958007813, 29.0423583984375)
        ],
        'road_geometry': [
            (41.0394497542302, 29.040563299602624),
            (41.0365633937752, 29.04339603116141),
            (41.032814684782245, 29.045185124777486),
            (41.027041255435506, 29.045781489316177),
            (41.0229545609317, 29.047520886057733)
        ],
        'output_filename': 'altunizade.csv',
    }                    
}

def extract_holiday_data(segment_key, input_files, chunk_size=100000):
    segment = ROAD_SEGMENTS[segment_key]
    grid_points_set = set(segment.get('grid_points', []))
    
    filtered_chunks = []
    
    for file_path in input_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"Searching for holidays in: {file_path}")
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            
            # Convert to datetime
            chunk['DATE_TIME'] = pd.to_datetime(chunk['DATE_TIME'])
            
            # Filter for exact holiday dates
            date_mask = chunk['DATE_TIME'].dt.date.astype(str).isin(ALL_HOLIDAY_DATES)
            chunk = chunk[date_mask]
            
            if chunk.empty:
                continue

            # Coordinate Filtering
            chunk_coords = pd.Series(list(zip(chunk['LATITUDE'], chunk['LONGITUDE'])))
            coord_mask = chunk_coords.isin(grid_points_set)
            
            filtered_chunk = chunk[coord_mask.values]
            
            if not filtered_chunk.empty:
                filtered_chunks.append(filtered_chunk)
                
    if filtered_chunks:
        result_df = pd.concat(filtered_chunks, ignore_index=True)
        
        # Save to a DIFFERENT folder than your baseline
        output_folder = '/Users/abdullah/tasarım dersi/Season_Comparison/holiday_data'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        output_path = os.path.join(output_folder, segment['output_filename'])
        result_df.to_csv(output_path, index=False)
        print(f"Successfully extracted holiday data to {output_path}")
    else:
        print(f"No holiday data found for {segment_key}.")

if __name__ == '__main__':
    for key in ROAD_SEGMENTS:
        extract_holiday_data(key, INPUT_FILES)