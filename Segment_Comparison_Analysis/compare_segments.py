## Compare road segments based on daily traffic volume profiles using DTW distance and MDS with K-Means clustering.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from main import ROAD_SEGMENTS

DATA_FOLDER = 'weighted_data'

def simple_dtw_distance(s1, s2):

    n, m = len(s1), len(s2)
    dtw_matrix = np.zeros((n+1, m+1))
    
    # Initialize with infinity
    dtw_matrix.fill(np.inf)
    dtw_matrix[0, 0] = 0
    
    for i in range(1, n+1):
        for j in range(1, m+1):
            # Euclidean distance between points
            cost = abs(s1[i-1] - s2[j-1])
            
            # Take the minimum of insertion, deletion, or match
            last_min = min(dtw_matrix[i-1, j],    # Insertion
                           dtw_matrix[i, j-1],    # Deletion
                           dtw_matrix[i-1, j-1])  # Match
            
            dtw_matrix[i, j] = cost + last_min
            
    return dtw_matrix[n, m]

def get_daily_volume_profile(segment_key, mode='weekday'):
    segment = ROAD_SEGMENTS[segment_key]
    filename = segment['output_filename']
    
    # Prefer weighted data if it exists
    weighted_path = os.path.join(DATA_FOLDER, f"weighted_{filename}")
    original_path = os.path.join(DATA_FOLDER, filename)
    
    if os.path.exists(weighted_path):
        path = weighted_path
    elif os.path.exists(original_path):
        path = original_path
    else:
        print(f"Data not found for {segment['name']}")
        return None
        
    df = pd.read_csv(path)
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df['HOUR'] = df['DATE_TIME'].dt.hour
    df['DAY_OF_WEEK'] = df['DATE_TIME'].dt.dayofweek

    # Separate Weekdays
    if mode == 'weekday':
        df = df[df['DAY_OF_WEEK'] < 5]
    else:
        df = df[df['DAY_OF_WEEK'] >= 5] 
    if df.empty:
        return None
    # Group and normalize
    hourly_profile = df.groupby('HOUR')['NUMBER_OF_VEHICLES'].sum()
    hourly_profile = hourly_profile.reindex(range(24), fill_value=0)
    
    return hourly_profile.values

def main():
    print("Extracting daily volume profiles for all segments...")
    
    profiles = {}
    names = []
    
    for key, info in ROAD_SEGMENTS.items():
        profile = get_daily_volume_profile(key)
        if profile is not None:
            # Normalize profile (0-1)
            scaler = MinMaxScaler()
            profile_norm = scaler.fit_transform(profile.reshape(-1, 1)).flatten()
            
            profiles[key] = profile_norm
            names.append(info['name'])
    
    keys = list(profiles.keys())
    n_segments = len(keys)
    
    if n_segments < 2:
        print("Not enough segments to compare.")
        return

    print(f"Computing DTW Distance Matrix for {n_segments} segments...")
    dist_matrix = np.zeros((n_segments, n_segments))
    
    for i in range(n_segments):
        for j in range(n_segments):
            if i == j:
                dist_matrix[i, j] = 0
            elif i > j:
                # Matrix is symmetric
                dist_matrix[i, j] = dist_matrix[j, i]
            else:
                d = simple_dtw_distance(profiles[keys[i]], profiles[keys[j]])
                dist_matrix[i, j] = d

    # 1. Visualize the Distance Matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(dist_matrix, xticklabels=names, yticklabels=names, cmap="viridis", annot=True, fmt=".1f")
    plt.title("Segment Similarity Matrix (DTW Distance)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('maps/dtw_distance_matrix.png', dpi=300)
    print("Saved matrix heatmap to maps/dtw_distance_matrix.png")
    plt.show()

    # 2. K-Means Clustering
    # Since K-Means needs coordinates, we use MDS to project the Distance Matrix into 2D space
    print("Applying MDS and K-Means...")
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
    coords = mds.fit_transform(dist_matrix)
    
    # Determine K (Number of clusters)
    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(coords)
    
    # Visualize Clusters
    plt.figure(figsize=(10, 8))
    
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    
    for i in range(n_segments):
        plt.scatter(coords[i, 0], coords[i, 1], c=colors[clusters[i]], s=100, edgecolors='black')
        plt.text(coords[i, 0]+0.02, coords[i, 1]+0.02, names[i], fontsize=9)
        
    plt.title(f"Road Segment Grouping (MDS + K-Means, k={k})")
    plt.xlabel("Dimension 1 (MDS)")
    plt.ylabel("Dimension 2 (MDS)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig('maps/segment_clusters.png', dpi=300)
    print("Saved cluster plot to maps/segment_clusters.png")
    plt.show()
    
    # Print Groupings
    print("\n--- Groupings ---")
    df_results = pd.DataFrame({'Segment': names, 'Cluster': clusters})
    for c in range(k):
        print(f"\nCluster {c}:")
        group = df_results[df_results['Cluster'] == c]['Segment'].tolist()
        for g in group:
            print(f" - {g}")
            
    # 3. Validation: Silhouette Score
    score = silhouette_score(coords, clusters)
    print(f"\n--- Validation ---")
    print(f"Silhouette Score: {score:.3f}")
    print("(A score close to 1.0 indicates well-separated clusters, near 0 indicates overlapping.)")

    # 4. Visual Validation: Cluster Profiles
    print("\nGenerating cluster profile plots for visual inspection...")
    fig, axes = plt.subplots(k, 1, figsize=(10, 3*k), sharex=True)
    
    hours = range(24)
    for c in range(k):
        ax = axes[c]
        indices = [i for i, x in enumerate(clusters) if x == c]
        
        for idx in indices:
            key = keys[idx]
            ax.plot(hours, profiles[key], alpha=0.7, linewidth=2, label=names[idx])
            
        ax.set_title(f"Cluster {c+1} Profiles")
        ax.set_ylabel("Norm. Volume")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize='x-small')
        
    plt.xlabel("Hour of Day")
    plt.tight_layout()
    plt.savefig('maps/cluster_profiles.png', dpi=300)
    print("Saved cluster profiles to maps/cluster_profiles.png")
    plt.show()

if __name__ == '__main__':
    main()
