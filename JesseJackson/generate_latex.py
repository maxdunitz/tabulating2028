import json

def tex_escape(text):
    return text.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}')

def generate_table(json_file, year):
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    lines = []
    lines.append(r"\begin{table}[ht]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{|l|c|c|c|c|c|}")
    lines.append(r"\hline")
    lines.append(r"\textbf{State} & \textbf{Total Del} & \textbf{Jackson \%} & \textbf{Act Del} & \textbf{Hypo Del} & \textbf{Net Diff} \\")
    lines.append(r"\hline")
    
    total_del = 0
    total_act = 0
    total_hyp = 0
    
    # Sort alphabetically by state
    sorted_states = sorted([k for k in data.keys() if data[k]['total_del'] > 0 and data[k]['pct'] > 0.0])
    
    for state in sorted_states:
        v = data[state]
        diff = v['hypo'] - v['act']
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        lines.append(f"{tex_escape(state)} & {v['total_del']} & {v['pct']}\\% & {v['act']} & {v['hypo']} & {diff_str} \\\\")
        total_del += v['total_del']
        total_act += v['act']
        total_hyp += v['hypo']
        
    lines.append(r"\hline")
    diff_total = total_hyp - total_act
    diff_total_str = f"+{diff_total}" if diff_total > 0 else str(diff_total)
    lines.append(f"\\textbf{{TOTAL}} & \\textbf{{{total_del}}} & & \\textbf{{{total_act}}} & \\textbf{{{total_hyp}}} & \\textbf{{{diff_total_str}}} \\\\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(f"\\caption{{Jesse Jackson {year} Primary Delegate Allocation: Actual vs. Hypothetical (Hamilton's Method, 15\\% Threshold, Statewide Pool)}}")
    lines.append(f"\\label{{tab:jackson_{year}}}")
    lines.append(r"\end{table}")
    
    return "\n".join(lines)

tex_1984 = generate_table('1984_jackson_data.json', '1984')
tex_1988 = generate_table('1988_jackson_data.json', '1988')

with open('jackson_tables.tex', 'w') as f:
    f.write(tex_1984 + "\n\n" + tex_1988)

