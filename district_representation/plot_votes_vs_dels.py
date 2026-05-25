import json
import matplotlib.pyplot as plt
import numpy as np
import sys

# Known party-run states/territories for the 2024 Democratic primaries
party_run_states = {'PR', 'VI', 'MP', 'ND', 'AS', 'AK', 'WY', 'HI', 'GU', 'UT', 'ID', 'MO', 'IA'}

try:
    with open("cd_data.json", "r") as f:
        cd_data = json.load(f)
except FileNotFoundError:
    print("Error: cd_data.json not found.")
    sys.exit(1)

# Scatter plot data
x_votes = []
y_dels = []
scatter_colors = []

# Histogram data (Votes per Delegate)
state_run_ratios = []
party_run_ratios = []

for state, info in cd_data.items():
    is_party_run = state in party_run_states
    
    cd_votes = info.get("cd_votes", {})
    cd_dels = info.get("cd_dels", {})
    
    for cd, votes_dict in cd_votes.items():
        # Sum total votes in this district
        total_votes = sum(votes_dict.values())
        dels = cd_dels.get(cd)
        
        # Only include if we have both delegates and a non-zero vote count
        if dels is not None and dels > 0 and total_votes > 0:
            x_votes.append(total_votes)
            y_dels.append(dels)
            
            ratio = total_votes / dels
            
            if is_party_run:
                party_run_ratios.append(ratio)
                scatter_colors.append('orange')
            else:
                state_run_ratios.append(ratio)
                scatter_colors.append('blue')

# --- Plot 1: Scatter Plot ---
plt.figure(figsize=(10, 6))

if state_run_ratios:
    sr_x = [x for x, c in zip(x_votes, scatter_colors) if c == 'blue']
    sr_y = [y for y, c in zip(y_dels, scatter_colors) if c == 'blue']
    plt.scatter(sr_x, sr_y, alpha=0.6, color='blue', edgecolors='k', label='State-run Primary')

if party_run_ratios:
    pr_x = [x for x, c in zip(x_votes, scatter_colors) if c == 'orange']
    pr_y = [y for y, c in zip(y_dels, scatter_colors) if c == 'orange']
    plt.scatter(pr_x, pr_y, alpha=0.8, color='orange', edgecolors='k', label='Party-run Primary/Caucus')

plt.title("District Delegates vs. 2024 Total Primary Votes", fontsize=14)
plt.xlabel("Total 2024 Democratic Primary Votes in District", fontsize=12)
plt.ylabel("Number of Delegates Attributed to District", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.legend()
plt.tight_layout()
plt.savefig("delegates_vs_primaryvotes_scatter.png", dpi=300)
print(f"Saved scatter plot to delegates_vs_primaryvotes_scatter.png (N={len(x_votes)})")

# --- Plot 2: Histograms (Votes per Delegate) ---
plt.figure(figsize=(10, 6))

all_ratios = state_run_ratios + party_run_ratios
# Use log scale bins for the ratio
bins = np.logspace(np.log10(max(1, min(all_ratios))), np.log10(max(all_ratios)), 30)

plt.hist(state_run_ratios, bins=bins, alpha=0.5, color='blue', edgecolor='black', label=f'State-run Primary (N={len(state_run_ratios)})')
plt.hist(party_run_ratios, bins=bins, alpha=0.7, color='orange', edgecolor='black', label=f'Party-run Primary/Caucus (N={len(party_run_ratios)})')

plt.xscale('log')
plt.title("Distribution of Primary Votes per Delegate (2024)", fontsize=14)
plt.xlabel("Primary Votes per Delegate (Log Scale)", fontsize=12)
plt.ylabel("Number of Districts", fontsize=12)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6, axis='y')
plt.tight_layout()
plt.savefig("primary_votes_histogram.png", dpi=300)
print("Saved histogram plot to primary_votes_histogram.png")
