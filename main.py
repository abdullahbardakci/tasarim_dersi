import pandas as pd
import os

INPUT_FILES = [
    'raw_data/July.csv',
    'raw_data/August.csv', 
    'raw_data/September.csv'
]

##kriging method to use

ROAD_SEGMENTS = {
    'mecidiyekoy_d100': {
        'name': 'Mecidiyeköy D100',
        'grid_points': [
            (41.0641479492188, 28.9874267578125),
            (41.0696411132813, 28.9874267578125),
            (41.0641479492188, 28.9984130859375),
            (41.0696411132813, 28.9984130859375),
            (41.0641479492188, 29.0093994140625),
            (41.0696411132813, 29.0093994140625)
        ],
        'output_filename': 'Mecidiyekoy_D100.csv',
    },
    'besiktas_meydan': {
        'name': 'Besiktas Meydan',
        'grid_points': [
            (41.0421752929688, 29.0093994140625)
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
        'output_filename': 'kopru.csv',
    },
    'buyukdere': {
        'name': 'Buyukdere',
        'grid_points': [
            (41.0861206054688, 29.0093994140625),
            (41.0806274414063, 29.0093994140625),
            (41.0806274414063, 29.0093994140625)
        ],
        'output_filename': 'Buyukdere.csv',
    },
        'cendere': {
        'name': 'Cendere Yolu',
        'grid_points': [
            (41.0806274414063, 28.9764404296875),
            (41.0861206054688, 28.9764404296875),
            (41.0916137695313, 28.9764404296875),
            (41.0916137695313, 28.9874267578125),
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
        'output_filename': 'beylikduzu.csv',
    },
        'bakirkoy': {
        'name': 'Bakırköy - İncirli E5',
        'grid_points': [
            (40.9927368164063, 28.8555908203125),
            (40.9927368164063, 28.8665771484375),
            (40.9982299804688, 28.8665771484375),
            (40.9982299804688, 28.8775634765625),
            (41.0037231445313, 28.8885498046875),
        ],
        'output_filename': 'bakirkoy.csv',
    },
        'topkapi': {
        'name': 'Topkapı - E5',
        'grid_points': [
            (41.0202026367188, 28.9324951171875),
            (41.0147094726563, 28.9434814453125),
        ],
        'output_filename': 'topkapi.csv',
    },
        'eminonu': {
        'name': 'Eminönü - Unkapanı Köprüsü',
        'grid_points': [
            (41.0256958007813, 28.9654541015625)
        ],
        'output_filename': 'eminonu.csv',
    },
        'karakoy': {
        'name': 'Karaköy - Galata Köprüsü',
        'grid_points': [
            (41.0202026367188, 28.9764404296875)
        ],
        'output_filename': 'karakoy.csv',
    },   
        'okmeydani': {
        'name': 'Okmeydanı - TEM Bağlantısı',
        'grid_points': [
            (41.0586547851563, 28.9654541015625),
            (41.0531616210938, 28.9544677734375)
        ],
        'output_filename': 'okmeydani.csv',
    },
        'kadikoy': {
        'name': 'Kadıköy - Rıhtım',
        'grid_points': [
            (40.9927368164063, 29.0313720703125),
            (40.9927368164063, 29.0203857421875),
            (40.9872436523438, 29.0313720703125)
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
        'output_filename': 'altunizade.csv',
    },                
        'kozyatagi': {
        'name': 'Kozyatağı - D100',
        'grid_points': [
            (40.9872436523438, 29.0863037109375),
            (40.9817504882813, 29.0972900390625),
            (40.9762573242188, 29.0972900390625)
        ],
        'output_filename': 'kozyatagi.csv',
    },
        'atasehir': {
        'name': 'Ataşehir - Finans Merkezi',
        'grid_points': [
            (40.9872436523438, 29.1082763671875),
            (40.9927368164063, 29.1082763671875),
            (40.9927368164063, 29.1192626953125)
        ],
        'output_filename': 'atasehir.csv',
    },        
        'umraniye': {
        'name': 'Ümraniye - TEM',
        'grid_points': [
            (41.0311889648438, 29.1192626953125),
            (41.0311889648438, 29.1082763671875),
            (41.0256958007813, 29.1192626953125),
            (41.0256958007813, 29.1302490234375)
        ],
        'output_filename': 'umraniye.csv',
    },
        'pendik': {
        'name': 'Pendik - D100',
        'grid_points': [
            (40.8663940429688, 29.2730712890625),
            (40.8718872070313, 29.2730712890625),
            (40.8718872070313, 29.2620849609375),
            (40.8773803710938, 29.2620849609375)
        ],
        'output_filename': 'pendik.csv',
    },
        'kartal': {
        'name': 'Kartal - D100',
        'grid_points': [
            (40.9048461914063, 29.2071533203125),
            (40.9103393554688, 29.2071533203125),
            (40.9103393554688, 29.1961669921875),
            (40.9048461914063, 29.2181396484375)
        ],
        'output_filename': 'kartal.csv',
    },             
        'maltepe': {
        'name': 'Maltepe - Başıbüyük',
        'grid_points': [
            (40.9378051757813, 29.1522216796875),
            (40.9432983398438, 29.1632080078125),
            (40.9487915039063, 29.1632080078125),
            (40.9487915039063, 29.1741943359375)
        ],
        'output_filename': 'maltepe.csv',
    },                      
}

def extract_road_segment(segment_key, input_files, chunk_size=100000):
    
    segment = ROAD_SEGMENTS[segment_key]
    grid_points = segment.get('grid_points', [])
    
    if not grid_points:
        print(f"No grid points for segment '{segment_key}'")
        return None
    
    grid_points_set = set(grid_points)
    
    filtered_chunks = []
    filtered_rows = 0
    
    for file_path in input_files:
        print(f"Processing file: {file_path}")
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            
            chunk_coords = pd.Series(list(zip(chunk['LATITUDE'], chunk['LONGITUDE'])))
            mask = chunk_coords.isin(grid_points_set)
            
            filtered_chunk = chunk[mask.values]
            
            if not filtered_chunk.empty:
                filtered_chunks.append(filtered_chunk)
                filtered_rows += len(filtered_chunk)

    if filtered_chunks:
        print(f"Combine and save data for {segment['name']}...")
        result_df = pd.concat(filtered_chunks, ignore_index=True)
        
        data_folder = 'relevant_data'
        
        output_filename = segment['output_filename']
        output_path = os.path.join(data_folder, output_filename)
        result_df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
        
        return result_df
    else:
        print(f"No data found for {segment_key} in any input files.")
        return None


if __name__ == '__main__':
    for segment_key in ROAD_SEGMENTS:
        extract_road_segment(segment_key, input_files=INPUT_FILES)