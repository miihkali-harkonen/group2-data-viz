import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf

df = dataset.copy()
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values('datetime')

# Map dataset IDs to names
id_mapping = {241: 'Production', 165: 'Consumption', 245: 'Wind power generation'}
df['dataset_name'] = df['dataset_id'].map(id_mapping)

# Create subplots for each ID
names = df['dataset_name'].unique()
fig, axes = plt.subplots(len(names), 1, figsize=(10, 4*len(names)))

if len(names) == 1:
    axes = [axes]

for i, name in enumerate(sorted(names)):
    data = df[df['dataset_name'] == name]['value']
    plot_acf(data, lags=24*7, ax=axes[i])
    axes[i].set_title(f'Autocorrelation - {name}')

plt.tight_layout()
plt.show()
