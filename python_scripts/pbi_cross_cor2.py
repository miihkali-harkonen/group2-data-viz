import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = dataset.copy()
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values('datetime')

# Extract Consumption (165) and Production (241)
consumption = df[df['dataset_id'] == 165].copy()
consumption = consumption.drop_duplicates(subset=['datetime'], keep='first')
consumption = consumption.set_index('datetime').sort_index()['value']

production = df[df['dataset_id'] == 241].copy()
production = production.drop_duplicates(subset=['datetime'], keep='first')
production = production.set_index('datetime').sort_index()['value']

# Align to common index
common_index = consumption.index.intersection(production.index)
consumption = consumption.loc[common_index].values
production = production.loc[common_index].values

# Remove NaN values
mask = ~(np.isnan(consumption) | np.isnan(production))
cons = consumption[mask]
prod = production[mask]

# Normalize series
cons_norm = (cons - np.mean(cons)) / np.std(cons)
prod_norm = (prod - np.mean(prod)) / np.std(prod)

# Calculate cross-correlation
max_lag = 40
ccf = np.correlate(cons_norm, prod_norm, mode='full') / len(cons)

# Extract relevant lags
mid = len(ccf) // 2
lags = np.arange(-max_lag, max_lag+1)
ccf_plot = ccf[mid-max_lag:mid+max_lag+1]

# Plot (matching ACF style)
fig, ax = plt.subplots(figsize=(10, 4))
ax.stem(lags, ccf_plot, basefmt=' ')
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

# Add confidence interval
conf_interval = 1.96 / np.sqrt(len(cons))
ax.axhline(y=conf_interval, color='b', linestyle='--', linewidth=1, alpha=0.5)
ax.axhline(y=-conf_interval, color='b', linestyle='--', linewidth=1, alpha=0.5)

ax.set_xlabel('Lag')
ax.set_ylabel('Cross-Correlation')
ax.set_title('Cross-Correlation: Consumption vs Production')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()