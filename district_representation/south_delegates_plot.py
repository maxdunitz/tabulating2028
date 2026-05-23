import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# The data below is statically embedded to ensure 100% reproducibility for the 2024 analysis
# This protects against any post-Callais (Louisiana) redistricting or other future Wikipedia edits.
# Data scraped from The Green Papers and 2024 Wikipedia infoboxes.
csv_data = """State,District,Delegates,BlackPct
Alabama,1,3,16.1
Alabama,2,7,48.9
Alabama,3,4,20.3
Alabama,4,2,6.9
Alabama,5,5,17.4
Alabama,6,4,17.4
Alabama,7,9,52.5
Arkansas,1,4,17.3
Arkansas,2,7,20.2
Arkansas,3,5,2.9
Arkansas,4,4,19.5
Florida,1,4,12.8
Florida,2,5,22.5
Florida,3,5,15.5
Florida,4,5,31.1
Florida,5,5,11.6
Florida,6,5,11.0
Florida,7,5,8.8
Florida,8,5,9.1
Florida,9,5,9.3
Florida,10,6,24.2
Florida,11,5,11.7
Florida,12,5,4.4
Florida,13,5,6.6
Florida,14,6,17.7
Florida,15,5,13.7
Florida,16,5,11.1
Florida,17,5,5.2
Florida,18,5,12.3
Florida,19,5,5.9
Florida,20,6,49.1
Florida,21,5,12.1
Florida,22,6,15.6
Florida,23,6,12.2
Florida,24,6,39.8
Florida,25,6,15.0
Florida,26,5,4.8
Florida,27,5,4.8
Florida,28,5,8.6
Georgia,1,4,27.5
Georgia,2,5,49.0
Georgia,3,4,22.6
Georgia,4,7,47.5
Georgia,5,7,49.8
Georgia,6,5,18.2
Georgia,7,6,7.7
Georgia,8,4,29.7
Georgia,9,4,11.9
Georgia,10,4,23.3
Georgia,11,5,11.4
Georgia,12,5,36.1
Georgia,13,7,49.6
Georgia,14,4,11.9
Louisiana,1,4,12.1
Louisiana,2,8,50.4
Louisiana,3,5,22.6
Louisiana,4,5,20.1
Louisiana,5,5,27.5
Louisiana,6,5,54.4
Mississippi,1,5,27.2
Mississippi,2,9,62.9
Mississippi,3,5,32.9
Mississippi,4,4,22.7
North Carolina,1,6,39.3
North Carolina,2,7,22.7
North Carolina,3,4,20.2
North Carolina,4,7,19.7
North Carolina,5,5,17.7
North Carolina,6,6,18.4
North Carolina,7,5,19.1
North Carolina,8,4,16.5
North Carolina,9,5,20.8
North Carolina,10,3,15.5
North Carolina,11,5,3.3
North Carolina,12,7,36.5
North Carolina,13,6,17.8
North Carolina,14,6,15.2
South Carolina,1,6,16.9
South Carolina,2,5,24.9
South Carolina,3,3,17.0
South Carolina,4,4,18.3
South Carolina,5,5,23.8
South Carolina,6,8,46.8
South Carolina,7,5,25.8
Tennessee,1,4,2.1
Tennessee,2,4,5.8
Tennessee,3,4,10.0
Tennessee,4,4,9.2
Tennessee,5,5,11.8
Tennessee,6,4,9.0
Tennessee,7,5,15.8
Tennessee,8,4,17.3
Tennessee,9,7,60.2
Texas,1,3,17.5
Texas,2,4,11.2
Texas,3,4,9.4
Texas,4,4,8.8
Texas,5,3,13.8
Texas,6,3,13.6
Texas,7,6,18.9
Texas,8,3,12.4
Texas,9,6,35.8
Texas,10,4,9.3
Texas,11,2,10.8
Texas,12,4,11.4
Texas,13,2,6.5
Texas,14,4,15.3
Texas,15,4,1.0
Texas,16,5,2.9
Texas,17,3,15.0
Texas,18,6,32.2
Texas,19,2,6.3
Texas,20,5,5.6
Texas,21,5,3.4
Texas,22,4,11.2
Texas,23,4,3.3
Texas,24,5,7.0
Texas,25,3,11.7
Texas,26,4,8.9
Texas,27,4,4.1
Texas,28,4,4.4
Texas,29,4,13.2
Texas,30,7,40.0
Texas,31,4,7.5
Texas,32,5,19.2
Texas,33,4,18.6
Texas,34,4,0.4
Texas,35,5,11.9
Texas,36,3,11.9
Texas,37,9,5.5
Texas,38,4,9.6
Virginia,1,6,13.0
Virginia,2,6,22.0
Virginia,3,6,43.2
Virginia,4,7,40.7
Virginia,5,5,20.7
Virginia,6,4,7.8
Virginia,7,6,20.4
Virginia,8,8,12.3
Virginia,9,3,5.7
Virginia,10,6,8.0
Virginia,11,8,9.0
"""

# Load the data
df = pd.read_csv(io.StringIO(csv_data))

# Map states to distinct colors
states = df['State'].unique()
colors = cm.tab20(np.linspace(0, 1, len(states)))
color_map = dict(zip(states, colors))

plt.figure(figsize=(14, 9))

# Scatter plot loop
for state in states:
    state_df = df[df['State'] == state]
    plt.scatter(
        state_df['BlackPct'], 
        state_df['Delegates'], 
        color=color_map[state], 
        label=state,
        alpha=0.6,
        s=120,
        edgecolors='white'
    )

# Linear Regression Trend line and R^2
slope, intercept = np.polyfit(df['BlackPct'], df['Delegates'], 1)
correlation_matrix = np.corrcoef(df['BlackPct'], df['Delegates'])
correlation_xy = correlation_matrix[0,1]
r_squared = correlation_xy**2

x_range = np.array([df['BlackPct'].min(), df['BlackPct'].max()])
plt.plot(x_range, intercept + slope * x_range, 'k--', alpha=0.3, label=f'Trend (R² = {r_squared:.2f})')

# Annotations helper
def add_label(row, label_text, offset=(0, 0.2)):
    plt.annotate(
        label_text,
        (row['BlackPct'], row['Delegates']),
        xytext=(row['BlackPct'] + offset[0], row['Delegates'] + offset[1]),
        fontsize=10,
        weight='bold',
        arrowprops=dict(arrowstyle="-", color="black", alpha=0.5)
    )

# Required specific annotations
al7 = df[(df['State'] == 'Alabama') & (df['District'] == 7)].iloc[0]
ms2 = df[(df['State'] == 'Mississippi') & (df['District'] == 2)].iloc[0]
tx37 = df[(df['State'] == 'Texas') & (df['District'] == 37)].iloc[0]

add_label(al7, 'AL-7', offset=(-6, -0.1))
add_label(ms2, 'MS-2', offset=(-6, -0.1))
add_label(tx37, 'TX-37', offset=(3, -0.1))

# VA seats with 8 delegates
va8 = df[(df['State'] == 'Virginia') & (df['Delegates'] == 8)]
for _, row in va8.iterrows():
    add_label(row, f"VA-{row['District']}", offset=(2, 0.2))

# Display Legend
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, labels, title="State / Trend", bbox_to_anchor=(1.05, 1), loc='upper left')

# Formatting
plt.title('2024 DNC Delegates vs Black Population by Congressional District (South)', fontsize=16)
plt.xlabel('Black Population (%)', fontsize=14)
plt.ylabel('Number of Delegates', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Save the output
output_path = 'south_delegates_plot_final.png'
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")
