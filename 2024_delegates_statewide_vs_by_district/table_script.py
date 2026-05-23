import json
import math
import re

with open("gp_results3.json", "r") as f:
    gp_data = json.load(f)
    
try:
    with open("cd_data.json", "r") as f:
        cd_data = json.load(f)
except:
    cd_data = {}
    
try:
    with open("actual_pledged.json", "r") as f:
        actual_pledged = json.load(f)
except:
    actual_pledged = {}

def normalize_name(name):
    name = name.split()[0].strip().replace(",", "")
    if name in ["Uninstructed", "No", "Noncommitted", "None"]: return "Uncommitted"
    if name == "BLANK" or name.lower() == "blank": return "Blank"
    if name in ["Jason", "PalmerJ", "Palmer"]: return "Palmer"
    if name in ["Stephen", "LyonsS", "Lyons"]: return "Lyons"
    if name in ["WilliamsonM", "Marianne"]: return "Williamson"
    if name in ["PhillipsD", "Dean"]: return "Phillips"
    return name

def allocate(votes, total_dels, threshold):
    total = sum(votes.values())
    if total == 0 or total_dels == 0: return {}
    viable = {c: v for c, v in votes.items() if v >= total * threshold}
    
    if not viable:
        top = max(votes, key=votes.get)
        new_threshold = (votes[top] / total) * 0.5
        viable = {c: v for c, v in votes.items() if v >= total * new_threshold}
        if not viable:
            viable = {top: votes[top]}
            
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

def add_dels(d1, d2):
    res = {}
    for c in set(d1.keys()) | set(d2.keys()):
        res[c] = d1.get(c, 0) + d2.get(c, 0)
    return res

states = ['SC', 'NV', 'MI', 'AL', 'AS', 'AR', 'CA', 'CO', 'IA', 'ME', 'MA', 'MN', 'NC', 'OK', 'TN', 'TX', 'UT', 'VT', 'VA', 'HI', 'DA', 'GA', 'MS', 'MP', 'WA', 'AZ', 'FL', 'IL', 'KS', 'OH', 'LA', 'MO', 'ND', 'CT', 'DE', 'NY', 'RI', 'WI', 'AK', 'WY', 'PA', 'NH', 'PR', 'IN', 'MD', 'NE', 'WV', 'KY', 'OR', 'ID', 'DC', 'MT', 'NJ', 'NM', 'SD', 'GU', 'VI']

expected_dels = {
    'AL': 52, 'AK': 15, 'AS': 6, 'AZ': 72, 'AR': 31, 'CA': 424, 'CO': 72, 'CT': 60, 'DE': 21, 'DC': 20, 
    'FL': 224, 'GA': 108, 'GU': 7, 'HI': 22, 'ID': 23, 'IL': 147, 'IN': 79, 'IA': 40, 'KS': 33, 'KY': 53, 
    'LA': 48, 'ME': 24, 'MD': 95, 'MA': 92, 'MI': 117, 'MN': 75, 'MS': 35, 'MO': 64, 'MT': 20, 'NE': 29, 
    'NV': 36, 'NH': 24, 'NJ': 126, 'NM': 34, 'NY': 268, 'NC': 116, 'ND': 13, 'MP': 6, 'OH': 127, 'OK': 36, 
    'OR': 66, 'PA': 159, 'PR': 55, 'RI': 26, 'SC': 55, 'SD': 16, 'TN': 63, 'TX': 244, 'UT': 30, 'VT': 16, 
    'VI': 7, 'VA': 99, 'WA': 92, 'WV': 20, 'WI': 82, 'WY': 13, 'DA': 13
}

out = []
out.append("\\begin{table}[h]")
out.append("\\centering")
out.append("\\resizebox{\\textwidth}{!}{")
out.append("\\begin{tabular}{l|c|c|c|c|c}")
out.append("\\hline")
out.append("\\textbf{State} & \\textbf{Dels} & \\textbf{Statewide (15\\%)} & \\textbf{Statewide (5\\%)} & \\textbf{Current (15\\%)} & \\textbf{Current (5\\%)} \\\\")
out.append("\\hline")

total_sw_15 = {}
total_sw_5 = {}
total_cur_15 = {}
total_cur_5 = {}

def fmt(d):
    if d is None: return "N/A"
    merged = {}
    for c,v in d.items():
        if v > 0:
            name = normalize_name(c)
            merged[name] = merged.get(name, 0) + v
    
    items = []
    for c,v in sorted(merged.items(), key=lambda x: -x[1]):
        items.append(f"{c}:{v}")
    return ", ".join(items) if items else "N/A"

for s in states:
    s_key = s + "-D"
    info = gp_data.get(s_key, {})
    statewide_votes = info.get("votes", {})
    cd_expected = info.get("cd", 0)
    al = info.get("al", 0)
    pleo = info.get("pleo", 0)
    
    total = expected_dels.get(s, 0)
    if total == 0: continue
    
    is_cd = (cd_expected > 0)
    asterisk = "" if not is_cd else ""
    if not is_cd: asterisk = "*"
    
    if not statewide_votes:
        statewide_votes = {"Biden": 100}
        
    sw_15 = allocate(statewide_votes, total, 0.15)
    sw_5 = allocate(statewide_votes, total, 0.05)
    
    cur_15 = actual_pledged.get(s, {}).copy()
    
    cur_sum = sum(cur_15.values())
    if cur_sum != total:
        if cur_sum == 0:
            cur_15 = {"Biden": total}
        else:
            diff = total - cur_sum
            cur_15["Biden"] = cur_15.get("Biden", 0) + diff
            
    cur_5 = None
    
    if not is_cd:
        cur_5 = sw_5
    else:
        if s in cd_data:
            c_info = cd_data[s]
            cd_votes = c_info["cd_votes"]
            cd_dels = c_info["cd_dels"]
            
            sum_cd_dels = sum(cd_dels.values())
            
            # Check if CD votes are empty/zeroes for any CD
            has_empty_cd_votes = any(sum(v_dict.values()) == 0 for v_dict in cd_votes.values())
            
            if abs(sum_cd_dels - cd_expected) > 3 or has_empty_cd_votes:
                cur_5 = None
            else:
                al_actual = c_info.get("pools", {}).get("al", al)
                pleo_actual = c_info.get("pools", {}).get("pleo", pleo)
                
                if al_actual + pleo_actual == 0:
                    remainder = total - sum_cd_dels
                    if remainder > 0:
                        al_actual = math.ceil(remainder * (25 / 40))
                        pleo_actual = remainder - al_actual
                
                al_5 = allocate(statewide_votes, al_actual, 0.05)
                pleo_5 = allocate(statewide_votes, pleo_actual, 0.05)
                
                cur_5 = add_dels(al_5, pleo_5)
                
                for cd_id_str, v_dict in cd_votes.items():
                    d = cd_dels.get(cd_id_str)
                    if not d: continue
                    c5 = allocate(v_dict, d, 0.05)
                    cur_5 = add_dels(cur_5, c5)
        else:
            cur_5 = None
            
    def add_to_total(tot, d):
        if d:
            for k, v in d.items(): 
                name = normalize_name(k)
                tot[name] = tot.get(name, 0) + v
            
    add_to_total(total_sw_15, sw_15)
    add_to_total(total_sw_5, sw_5)
    add_to_total(total_cur_15, cur_15)
    add_to_total(total_cur_5, cur_5)
        
    link = f"\\href{{https://www.thegreenpapers.com/P24/{s}-D}}{{{s}}}"
    out.append(f"{link}{asterisk} & {total} & {fmt(sw_15)} & {fmt(sw_5)} & {fmt(cur_15)} & {fmt(cur_5)} \\\\")

out.append("\\hline")

def fmt_final(d):
    items = []
    for c,v in sorted(d.items(), key=lambda x: -x[1]):
        items.append(f"{c}:{v}")
    return ", ".join(items) if items else "N/A"

out.append(f"\\textbf{{Total}} & \\textbf{{{sum(expected_dels.values())}}} & {fmt_final(total_sw_15)} & {fmt_final(total_sw_5)} & {fmt_final(total_cur_15)} & {fmt_final(total_cur_5)} \\\\")
out.append("\\hline")
out.append("\\end{tabular}")
out.append("}")
out.append("\\caption{Delegate allocation under various viability scenarios. * indicates state parties that do not allocate by district-level performance. Scenarios marked N/A lack comprehensive district-level vote data. Current scheme (15\\%) represents the actual pledged delegates awarded in 2024. Current scheme (5\\%) runs Hamilton's method twice, once each for the At-Large and PLEO pools, plus district-level allocation where data permits.}")
out.append("\\end{table}")

with open("delegate_table.tex", "w") as f:
    f.write("\n".join(out))
