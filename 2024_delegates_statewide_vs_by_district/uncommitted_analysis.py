import json
import math
import re

with open("gp_results3.json", "r") as f:
    gp_data = json.load(f)
    
try:
    with open("actual_pledged.json", "r") as f:
        actual_pledged = json.load(f)
except:
    actual_pledged = {}

try:
    with open("cd_data.json", "r") as f:
        cd_data = json.load(f)
except:
    cd_data = {}

expected_dels = {
    'AL': 52, 'AK': 15, 'AS': 6, 'AZ': 72, 'AR': 31, 'CA': 424, 'CO': 72, 'CT': 60, 'DE': 21, 'DC': 20, 
    'FL': 224, 'GA': 108, 'GU': 7, 'HI': 22, 'ID': 23, 'IL': 147, 'IN': 79, 'IA': 40, 'KS': 33, 'KY': 53, 
    'LA': 48, 'ME': 24, 'MD': 95, 'MA': 92, 'MI': 117, 'MN': 75, 'MS': 35, 'MO': 64, 'MT': 20, 'NE': 29, 
    'NV': 36, 'NH': 24, 'NJ': 126, 'NM': 34, 'NY': 268, 'NC': 116, 'ND': 13, 'MP': 6, 'OH': 127, 'OK': 36, 
    'OR': 66, 'PA': 159, 'PR': 55, 'RI': 26, 'SC': 55, 'SD': 16, 'TN': 63, 'TX': 244, 'UT': 30, 'VT': 16, 
    'VI': 7, 'VA': 99, 'WA': 92, 'WV': 20, 'WI': 82, 'WY': 13, 'DA': 13
}

def normalize_name(name):
    name = name.split()[0].strip().replace(",", "")
    if name in ["Uninstructed", "No", "Noncommitted", "None"]: return "Uncommitted"
    if name.lower() in ["blank", "write-in"]: return "Blank"
    if name in ["Jason", "PalmerJ", "Palmer"]: return "Palmer"
    if name in ["Stephen", "LyonsS", "Lyons"]: return "Lyons"
    if name in ["WilliamsonM", "Marianne"]: return "Williamson"
    if name in ["PhillipsD", "Dean"]: return "Phillips"
    return name

def allocate(votes, total_dels, threshold):
    total = sum(votes.values())
    if total == 0 or total_dels == 0: return {}
    
    # "blank" or "write-in" cannot accumulate delegates, so they are never viable
    viable = {c: v for c, v in votes.items() if v >= total * threshold and c != "Blank"}
    
    if not viable:
        # If no one is viable, the top candidate (that is not Blank) gets a lowered threshold
        valid_votes = {c: v for c, v in votes.items() if c != "Blank"}
        if valid_votes:
            top = max(valid_votes, key=valid_votes.get)
            new_threshold = (valid_votes[top] / total) * 0.5
            viable = {c: v for c, v in valid_votes.items() if v >= total * new_threshold}
            if not viable:
                viable = {top: valid_votes[top]}
        else:
            return {}
            
    v_total = sum(viable.values())
    frac = {c: (v / v_total) * total_dels for c, v in viable.items()}
    alloc = {c: math.floor(f) for c, f in frac.items()}
    rem = total_dels - sum(alloc.values())
    remainders = {c: frac[c] - alloc[c] for c in frac}
    
    def sort_key(c):
        return (remainders[c], votes.get(c, 0))
        
    for c in sorted(remainders.keys(), key=sort_key, reverse=True)[:int(rem)]:
        alloc[c] += 1
    return alloc

state_results = {}

for s, total in expected_dels.items():
    s_key = s + "-D"
    info = gp_data.get(s_key, {})
    raw_votes = info.get("votes", {})
    
    # Fallback to cd_data.json if statewide votes are missing
    if not raw_votes and s in cd_data and "cd_votes" in cd_data[s]:
        for cd, cd_v in cd_data[s]["cd_votes"].items():
            for c, v in cd_v.items():
                raw_votes[c] = raw_votes.get(c, 0) + v
                
    # Normalize vote dictionary
    statewide_votes = {}
    for c, v in raw_votes.items():
        norm_c = normalize_name(c)
        statewide_votes[norm_c] = statewide_votes.get(norm_c, 0) + v
        
    total_votes = sum(statewide_votes.values())
    unc_votes = statewide_votes.get("Uncommitted", 0)
    unc_pct = (unc_votes / total_votes * 100) if total_votes > 0 else 0.0
    
    if not statewide_votes:
        statewide_votes = {"Biden": 100}
        
    sw_15 = allocate(statewide_votes, total, 0.15)
    sw_5 = allocate(statewide_votes, total, 0.05)
    
    # Actual
    cur_15 = actual_pledged.get(s, {})
    actual_unc = 0
    for c, v in cur_15.items():
        if normalize_name(c) == "Uncommitted":
            actual_unc += v
            
    hypo_15 = sw_15.get("Uncommitted", 0)
    hypo_5 = sw_5.get("Uncommitted", 0)
    
    # Only include the state if Uncommitted was an option (received > 0% of the vote or won actual delegates)
    if unc_pct > 0 or actual_unc > 0:
        state_results[s] = {
            'total_del': total,
            'pct': unc_pct,
            'act': actual_unc,
            'hypo': hypo_15,
            'hypo_5': hypo_5
        }

total_act = sum(v['act'] for v in state_results.values())
total_hyp = sum(v['hypo'] for v in state_results.values())
total_hyp_5 = sum(v['hypo_5'] for v in state_results.values())
total_del_all = sum(v['total_del'] for v in state_results.values())

weighted_pct_sum = sum(v['total_del'] * v['pct'] for v in state_results.values())
weighted_avg = weighted_pct_sum / total_del_all if total_del_all > 0 else 0.0

print(f"{'State':<6} | {'Tot':<4} | {'Unc%':<6} | {'Act':<3} | {'H15':<3} | {'Diff':<4} | {'H5':<3} | {'Diff':<4}")
print("-" * 65)

# Generate LaTeX table rows simultaneously
latex_rows = []

# Sort by Unc% descending for presentation
sorted_states = sorted(state_results.items(), key=lambda x: x[1]['pct'], reverse=True)

for k, v in sorted_states:
    diff15 = v['hypo'] - v['act']
    diff5 = v['hypo_5'] - v['act']
    
    diff15_str = f"+{diff15}" if diff15 > 0 else str(diff15)
    diff5_str = f"+{diff5}" if diff5 > 0 else str(diff5)
    
    print(f"{k:<6} | {v['total_del']:<4} | {v['pct']:<5.2f}% | {v['act']:<3} | {v['hypo']:<3} | {diff15_str:<4} | {v['hypo_5']:<3} | {diff5_str:<4}")
    
    latex_rows.append(f"{k} & {v['total_del']} & {v['pct']:.2f}\\% & {v['act']} & {v['hypo']} & {diff15_str} & {v['hypo_5']} & {diff5_str} \\\\")

print("-" * 65)
diff15_total = total_hyp - total_act
diff5_total = total_hyp_5 - total_act
diff15_t_str = f"+{diff15_total}" if diff15_total > 0 else str(diff15_total)
diff5_t_str = f"+{diff5_total}" if diff5_total > 0 else str(diff5_total)

print(f"{'TOTAL':<6} | {total_del_all:<4} | {'':<6} | {total_act:<3} | {total_hyp:<3} | {diff15_t_str:<4} | {total_hyp_5:<3} | {diff5_t_str:<4}")
print(f"\nWeighted average Uncommitted share: {weighted_avg:.2f}%")

# Save LaTeX table
with open("uncommitted_table.tex", "w") as f:
    f.write("\\begin{table}[ht]\n\\centering\n\\begin{tabular}{|l|c|c|c|c|c|c|c|}\n\\hline\n")
    f.write("\\textbf{State} & \\textbf{Total} & \\textbf{Unc\\%} & \\textbf{Act} & \\textbf{Hypo (15\\%)} & \\textbf{Diff (15\\%)} & \\textbf{Hypo (5\\%)} & \\textbf{Diff (5\\%)} \\\\\n\\hline\n")
    f.write("\n".join(latex_rows))
    f.write("\n\\hline\n")
    f.write(f"\\textbf{{TOTAL}} & \\textbf{{{total_del_all}}} & & \\textbf{{{total_act}}} & \\textbf{{{total_hyp}}} & \\textbf{{{diff15_t_str}}} & \\textbf{{{total_hyp_5}}} & \\textbf{{{diff5_t_str}}} \\\\\n")
    f.write("\\hline\n\\end{tabular}\n")
    f.write("\\caption{2024 Uncommitted Delegate Allocation: Actual vs. Hypothetical (Hamilton's Method, Statewide Pool)}\n")
    f.write("\\label{tab:uncommitted_2024}\n\\end{table}")
