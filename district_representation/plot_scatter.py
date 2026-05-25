import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Load primary delegate data
try:
    with open("cd_data.json", "r") as f:
        cd_data = json.load(f)
except FileNotFoundError:
    print("Error: cd_data.json not found.")
    sys.exit(1)

# Read the newly downloaded dataset
xls = pd.ExcelFile("ds3.xlsx")
df = pd.read_excel(xls, sheet_name="Vote totals (new districts)")

x_biden_votes = []
y_delegates = []
labels = []

# Process the rows
for idx, row in df.iterrows():
    dist_str = str(row["District"]).strip()
    if "-" not in dist_str: continue
    
    state_abbr, cd_str = dist_str.split("-")
    
    # Parse CD number
    if cd_str.upper() == "AL":
        cd_num = "1"
    else:
        cd_num = str(int(cd_str)) if cd_str.isdigit() else cd_str
        
    biden_vote = float(row["Biden"])
    
    # Match with cd_data.json
    if state_abbr in cd_data:
        cd_dels_dict = cd_data[state_abbr].get("cd_dels", {})
        if cd_num in cd_dels_dict:
            dels = cd_dels_dict[cd_num]
            x_biden_votes.append(biden_vote)
            y_delegates.append(dels)
            labels.append(dist_str)

if not x_biden_votes:
    print("Error: No matching data found.")
    sys.exit(1)

plt.figure(figsize=(10, 6))
plt.scatter(x_biden_votes, y_delegates, alpha=0.5, color='blue', edgecolors='k')

# Calculate and plot regression line
import numpy as np
m, b = np.polyfit(x_biden_votes, y_delegates, 1)
x_line = np.linspace(min(x_biden_votes), max(x_biden_votes), 100)
plt.plot(x_line, m*x_line + b, color='red', linestyle='--', linewidth=2, label=f'Trend (Slope: {m:.5f})')

plt.title("District Delegates vs. 2020 Biden-Harris General Election Vote", fontsize=14)
plt.xlabel("2020 Biden-Harris Popular Vote", fontsize=12)
plt.ylabel("Number of Delegates Attributed (2024)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Format x-axis with commas
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))

plt.legend()
plt.tight_layout()
plt.savefig("delegates_vs_biden2020_scatter.png", dpi=300)
print(f"Success! Plotted {len(x_biden_votes)} districts.")
