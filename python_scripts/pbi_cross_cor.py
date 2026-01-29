import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = dataset.copy()
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values('datetime')

# Map dataset IDs to names
id_mapping = {241: 'Production', 165: 'Consumption', 245: 'Wind power generation'}

# Extract each time series separately
datasets = {}
for ds_id, name in id_mapping.items():
    data = df[df['dataset_id'] == ds_id].copy()
    data = data.drop_duplicates(subset=['datetime'], keep='first')
    data = data.set_index('datetime').sort_index()
    datasets[name] = data['value']

# Get common datetime index across all series
common_index = datasets[list(datasets.keys())[0]].index
for name in datasets.keys():
    common_index = common_index.intersection(datasets[name].index)

# Align all series to common index
for name in datasets.keys():
    datasets[name] = datasets[name].loc[common_index]

names = sorted(datasets.keys())
max_lag = 24*7

fig, axes = plt.subplots(len(names), len(names), figsize=(14, 14))

for i, name1 in enumerate(names):
    for j, name2 in enumerate(names):
        series1 = datasets[name1].values
        series2 = datasets[name2].values

        # Remove NaN values
        mask = ~(np.isnan(series1) | np.isnan(series2))
        s1 = series1[mask]
        s2 = series2[mask]

        if len(s1) == 0:
            axes[i,j].text(0.5, 0.5, 'No data', ha='center', va='center')
            continue

        # Normalize series
        s1_norm = (s1 - np.mean(s1)) / np.std(s1)
        s2_norm = (s2 - np.mean(s2)) / np.std(s2)

        # Calculate cross-correlation
        ccf = np.correlate(s1_norm, s2_norm, mode='full') / len(s1)

        # Extract relevant lags
        mid = len(ccf) // 2
        lags = np.arange(-max_lag, max_lag+1)
        ccf_plot = ccf[mid-max_lag:mid+max_lag+1]

        # Plot
        axes[i,j].stem(lags, ccf_plot, basefmt=' ', linefmt='C0-', markerfmt='C0o')
        axes[i,j].axhline(y=0, color='k', linestyle='-', linewidth=0.5)

        # Add confidence interval
        conf_interval = 1.96 / np.sqrt(len(s1))
        axes[i,j].axhline(y=conf_interval, color='r', linestyle='--', linewidth=0.5, alpha=0.5)
        axes[i,j].axhline(y=-conf_interval, color='r', linestyle='--', linewidth=0.5, alpha=0.5)

        if i == j:
            axes[i,j].set_title(f'{name1} (ACF)', fontsize=10)
        else:
            axes[i,j].set_title(f'{name1} vs {name2}', fontsize=10)

        axes[i,j].set_xlabel('Lag', fontsize=8)
        axes[i,j].set_ylabel('Correlation', fontsize=8)
        axes[i,j].tick_params(labelsize=8)
        axes[i,j].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()