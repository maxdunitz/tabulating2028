import csv
import re
import math

def get_total_delegates(pledged_str):
    # '52' or '0|[|a|]'
    m2 = re.search(r'^(\d+)', pledged_str)
    if m2:
        return int(m2.group(1))
    return 0

def get_actual_delegates(cell):
    # '23|[|d|]|116,920|(27.30%)' -> 23
    # '10|15,338 (34.46%)' -> 10
    m = re.match(r'^(\d+)(?:\||\s)', cell)
    if m:
        return int(m.group(1))
    
    # if it's just '13' like Delaware caucus
    if re.match(r'^(\d+)$', cell.strip()):
        return int(cell.strip())
        
    return 0

def get_pct(cell):
    matches = re.findall(r'\(([\d\.]+)%\)', cell)
    if matches:
        return float(matches[-1])
    return 0.0

months = ('January', 'February', 'March', 'April', 'May', 'June')

state_results = {}

with open('1984_results_sep.csv', 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)

for row in rows[3:]:
    if len(row) < 6:
        continue
        
    offset = 0 if row[0].startswith(months) else 1
    
    try:
        pledged_str = row[1 - offset]
        contest = row[2 - offset]
    except IndexError:
        continue
        
    if "Total" in contest:
        continue
        
    contest_name = re.sub(r'\[.*?\]', '', contest)
    state_name = re.sub(r'(primary|caucus|State Committee|State Convention|Terr\.Caucus|CDConvention|Convention|Pref\.Pri|Reg\.Caucuses).*', '', contest_name).strip()
    
    total_del = get_total_delegates(pledged_str)
    
    try:
        jackson_cell = row[5 - offset]
        jackson_act = get_actual_delegates(jackson_cell)
        jackson_pct = get_pct(jackson_cell)
        
        pcts = []
        for i in range(3 - offset, 9 - offset):
            pcts.append(get_pct(row[i]))
    except IndexError:
        continue
        
    if state_name not in state_results:
        state_results[state_name] = {'total_del': 0, 'act': 0, 'hypo': 0, 'pct': 0.0}
        
    if state_results[state_name]['total_del'] < total_del:
        state_results[state_name]['total_del'] = total_del
        
    state_results[state_name]['act'] += jackson_act
    
    if sum(pcts) > 0 and state_results[state_name]['pct'] == 0:
        state_results[state_name]['pct'] = jackson_pct
        
        qualified_pcts = [p for p in pcts if p >= 15.0]
        sum_qualified = sum(qualified_pcts)
        
        hypo_jackson = 0
        if jackson_pct >= 15.0 and sum_qualified > 0:
            quotas = [(p / sum_qualified) * total_del for p in pcts]
            bases = [math.floor(q) if p >= 15.0 else 0 for p, q in zip(pcts, quotas)]
            remainders = [(q - math.floor(q)) if p >= 15.0 else 0 for p, q in zip(pcts, quotas)]
            
            awarded = sum(bases)
            remaining = total_del - awarded
            
            indexed_remainders = [(i, r) for i, r in enumerate(remainders)]
            indexed_remainders.sort(key=lambda x: x[1], reverse=True)
            
            for i in range(remaining):
                if i < len(indexed_remainders):
                    idx = indexed_remainders[i][0]
                    bases[idx] += 1
                    
            hypo_jackson = bases[2] # Jackson is index 2 in pcts (Mondale=0, Hart=1, Jackson=2)
            
        state_results[state_name]['hypo'] = hypo_jackson


import json
with open('1984_jackson_data.json', 'w') as f:
    json.dump(state_results, f, indent=2)

total_act = sum(v['act'] for v in state_results.values())
total_hyp = sum(v['hypo'] for v in state_results.values())
total_del = sum(v['total_del'] for v in state_results.values())

print(f"{'State':<20} | {'Tot':<5} | {'Jack%':<6} | {'Act':<3} | {'Hyp':<3}")
print("-" * 50)
for k, v in state_results.items():
    if v['total_del'] > 0:
        print(f"{k[:20]:<20} | {v['total_del']:<5} | {v['pct']:<6} | {v['act']:<3} | {v['hypo']:<3}")

print("-" * 50)
print(f"Total delegates: {total_del}. Act: {total_act}. Hypo: {total_hyp}")

