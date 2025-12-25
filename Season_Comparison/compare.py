import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os
from sklearn.preprocessing import MinMaxScaler

# Folders configuration
BASELINE_FOLDER = 'Season_Comparison/weighted_baseline'
HOLIDAY_FOLDER = 'Season_Comparison/weighted_holiday'

def simple_dtw_distance(s1, s2):
    """Calculates DTW distance to measure temporal rhythm drift."""
    n, m = len(s1), len(s2)
    dtw_matrix = np.zeros((n+1, m+1))
    dtw_matrix.fill(np.inf)
    dtw_matrix[0, 0] = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = abs(s1[i-1] - s2[j-1])
            last_min = min(dtw_matrix[i-1, j], dtw_matrix[i, j-1], dtw_matrix[i-1, j-1])
            dtw_matrix[i, j] = cost + last_min
    return dtw_matrix[n, m]

def get_aggregate_profile(folder_path, date_filter=None, normalize=True):
    """
    Combines segments into a master profile.
    normalize=True: Returns rhythm signature.
    normalize=False: Returns raw vehicle density.
    """
    all_profiles = []
    if not os.path.exists(folder_path):
        print(f"Directory not found: {folder_path}")
        return None
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    for f in files:
        df = pd.read_csv(os.path.join(folder_path, f))
        df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
        
        if date_filter:
            df = df[df['DATE_TIME'].dt.date.astype(str).isin(date_filter)]
            
        if df.empty: continue
            
        hourly = df.groupby(df['DATE_TIME'].dt.hour)['NUMBER_OF_VEHICLES'].mean()
        hourly = hourly.reindex(range(24), fill_value=0)
        
        if normalize:
            scaler = MinMaxScaler()
            data = scaler.fit_transform(hourly.values.reshape(-1, 1)).flatten()
        else:
            data = hourly.values
            
        all_profiles.append(data)
    
    return np.mean(all_profiles, axis=0) if all_profiles else None

def main():

    holiday_targets = {
    'Ramadan Holiday': ['2024-04-10', '2024-04-11', '2024-04-12'],
    'Feast of Sacrifice': ['2024-06-16', '2024-06-17', '2024-06-18'],
    'School Opening': ['2024-09-09', '2024-09-10', '2024-09-11','2024-09-12','2024-09-13'],
}

    # 1. EXTRACT DATA
    sig_norm = {'Baseline': get_aggregate_profile(BASELINE_FOLDER, normalize=True)}
    sig_raw = {'Baseline': get_aggregate_profile(BASELINE_FOLDER, normalize=False)}

    for name, dates in holiday_targets.items():
        print(f"Processing {name}...")
        sig_norm[name] = get_aggregate_profile(HOLIDAY_FOLDER, date_filter=dates, normalize=True)
        sig_raw[name] = get_aggregate_profile(HOLIDAY_FOLDER, date_filter=dates, normalize=False)

    labels = [k for k, v in sig_norm.items() if v is not None]
    colors = ['red', 'blue', 'green']

    # --- PLOT 1: RHYTHM LINE GRAPH (NORMALIZED) ---
    plt.figure(figsize=(12, 5))
    plt.plot(range(24), sig_norm['Baseline'], 'k--', label='BASELINE', linewidth=3)
    for i, label in enumerate(labels):
        if label == 'Baseline': continue
        plt.plot(range(24), sig_norm[label], color=colors[i-1], label=label, linewidth=2)
    plt.title("Analysis 1: Traffic Rhythm Shift (Normalized Pattern Comparison)", fontsize=14)
    plt.xlabel("Hour of Day")
    plt.ylabel("Min-Max Scaled Volume")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('global_seasonality_line_graph.png', dpi=300, bbox_inches='tight')
    plt.show()

    # --- PLOT 2: DENSITY LINE GRAPH (RAW VOLUME) ---
    plt.figure(figsize=(12, 5))
    plt.plot(range(24), sig_raw['Baseline'], 'k--', label='BASELINE', linewidth=3)
    for i, label in enumerate(labels):
        if label == 'Baseline': continue
        plt.plot(range(24), sig_raw[label], color=colors[i-1], label=label, linewidth=2)
    plt.title("Analysis 2: Traffic Density Comparison (Raw Vehicle Counts)", fontsize=14)
    plt.xlabel("Hour of Day")
    plt.ylabel("Mean Vehicle Count")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('density_line_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

    # --- PLOT 3: DTW DISTANCE MATRIX ---
    n = len(labels)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = simple_dtw_distance(sig_norm[labels[i]], sig_norm[labels[j]])
    plt.figure(figsize=(9, 7))
    sns.heatmap(dist_matrix, annot=True, fmt=".2f", cmap="YlOrRd", xticklabels=labels, yticklabels=labels)
    plt.title("Analysis 3: Behavioral Similarity Matrix (DTW Score)", fontsize=14)
    plt.savefig('dtw_similarity_matrix.png', dpi=300, bbox_inches='tight')
    plt.tight_layout()
    plt.show()

    # --- PLOT 4: DENSITY BAR CHART ---
    total_volumes = [np.sum(sig_raw[label]) for label in labels]
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, total_volumes, color=['gray'] + colors[:len(labels)-1])
    base_vol = total_volumes[0]
    for i, bar in enumerate(bars):
        if i == 0: continue
        percent_diff = ((total_volumes[i] - base_vol) / base_vol) * 100
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                 f"{percent_diff:+.1f}%", ha='center', fontweight='bold')
    plt.title("Analysis 4: Total Daily Traffic Load Comparison", fontsize=14)
    plt.ylabel("Sum of Hourly Vehicle Counts")
    plt.savefig('density_comparison_bars.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    main()