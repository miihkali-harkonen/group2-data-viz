import matplotlib.pyplot as plt
import pandas as pd

    # Power BI passes data as 'dataset' DataFrame
df = dataset.copy()
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values('datetime')

legends = ["Production", "Wind power generation", "Consumption"]
# Plot all three time series
plt.figure(figsize=(12, 6))
for id in [241, 245, 165]:
    data = df[df['dataset_id'] == id]
    plt.plot(data['datetime'], data['value'], label=f'ID: {id}', marker='o', markersize=2)

plt.xlabel('DateTime')
plt.ylabel('Value')
plt.title('Time Series by ID')
plt.legend(legends)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
