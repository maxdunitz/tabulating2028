import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

with open('/Users/m.dunitz/Desktop/code/crossratio/delegates_data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

polarized_states = ['Alabama', 'Mississippi', 'Louisiana', 'South Carolina', 'Georgia']
df = df[df['State'].isin(polarized_states)]

# Map states to distinct colors
states = df['State'].unique()
colors = cm.tab10(np.linspace(0, 1, len(states)))
color_map = dict(zip(states, colors))

plt.figure(figsize=(12, 8))

# Scatter plot loop
for state in states:
    state_df = df[df['State'] == state]
    plt.scatter(
        state_df['BlackPct'], 
        state_df['Delegates'], 
        color=color_map[state], 
        label=state,
        alpha=0.7,
        s=150,
        edgecolors='white'
    )

# Linear Regression Trend line and R^2
slope, intercept = np.polyfit(df['BlackPct'], df['Delegates'], 1)
correlation_matrix = np.corrcoef(df['BlackPct'], df['Delegates'])
correlation_xy = correlation_matrix[0,1]
r_squared = correlation_xy**2

x_range = np.array([df['BlackPct'].min(), df['BlackPct'].max()])
plt.plot(x_range, intercept + slope * x_range, 'k--', alpha=0.5, label=f'Trend (R² = {r_squared:.2f})')

# Annotations helper
def add_label(row, label_text, offset=(0, 0.2)):
    plt.annotate(
        label_text,
        (row['BlackPct'], row['Delegates']),
        xytext=(row['BlackPct'] + offset[0], row['Delegates'] + offset[1]),
        fontsize=11,
        weight='bold',
        arrowprops=dict(arrowstyle="-", color="black", alpha=0.5)
    )

# Label AL-7 and MS-2 since they are in this group
al7 = df[(df['State'] == 'Alabama') & (df['District'] == 7)].iloc[0]
ms2 = df[(df['State'] == 'Mississippi') & (df['District'] == 2)].iloc[0]

add_label(al7, 'AL-7', offset=(-6, -0.1))
add_label(ms2, 'MS-2', offset=(-6, -0.1))

# Maybe label the highest ones in GA, LA, SC?
# LA-2
la2 = df[(df['State'] == 'Louisiana') & (df['District'] == 2)].iloc[0]
add_label(la2, 'LA-2', offset=(-6, 0.3))

# SC-6
sc6 = df[(df['State'] == 'South Carolina') & (df['District'] == 6)].iloc[0]
add_label(sc6, 'SC-6', offset=(3, -0.1))

# Display Legend
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, labels, title="State / Trend", bbox_to_anchor=(1.05, 1), loc='upper left')

# Formatting
plt.title('2024 DNC Delegates vs Black Population\n(Deep South: AL, MS, LA, SC, GA)', fontsize=16)
plt.xlabel('Black Population (%)', fontsize=14)
plt.ylabel('Number of Delegates', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Save the output
output_path = '/Users/m.dunitz/Desktop/code/crossratio/deep_south_plot.png'
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")
