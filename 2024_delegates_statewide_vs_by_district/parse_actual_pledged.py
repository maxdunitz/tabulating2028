import os
import re
from bs4 import BeautifulSoup
import json

states = ['SC', 'NV', 'MI', 'AL', 'AS', 'AR', 'CA', 'CO', 'IA', 'ME', 'MA', 'MN', 'NC', 'OK', 'TN', 'TX', 'UT', 'VT', 'VA', 'HI', 'DA', 'GA', 'MS', 'MP', 'WA', 'AZ', 'FL', 'IL', 'KS', 'OH', 'LA', 'MO', 'ND', 'CT', 'DE', 'NY', 'RI', 'WI', 'AK', 'WY', 'PA', 'NH', 'PR', 'IN', 'MD', 'NE', 'WV', 'KY', 'OR', 'ID', 'DC', 'MT', 'NJ', 'NM', 'SD', 'GU', 'VI']

actual_pledged = {}

for s in states:
    s_key = s + "-D"
    filepath = f"htmls/{s_key}.html"
    try:
        with open(filepath, 'r', errors='ignore') as f:
            html = f.read()
    except:
        continue
        
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    # 1. Find the number of Unpledged PLEOs
    unpledged_m = re.search(r'(\d+)\s+Unpledged\s+PLEOs?', text, re.IGNORECASE)
    unpledged = int(unpledged_m.group(1)) if unpledged_m else 0
    
    cand_dels = {}
    found = False
    
    for t in soup.find_all("table"):
        if "Delegate Votes" in t.text and "Hard Total" in t.text:
            rows = t.find_all("tr")
            for r in rows:
                cols = [c.text.strip().replace("\xa0", " ") for c in r.find_all(["th", "td"])]
                if len(cols) >= 2 and cols[0] not in ["", "Candidate", "Hard Total", "Total"] and not cols[0].startswith("("):
                    name = cols[0]
                    # Format: "115  83.33%"
                    val_str = cols[1].split()[0] if cols[1] else "0"
                    if val_str.isdigit():
                        cand_dels[name] = cand_dels.get(name, 0) + int(val_str)
            found = True
            break
            
    if found:
        # Subtract Unpledged PLEOs from Uncommitted
        clean_dels = {}
        for c, v in cand_dels.items():
            if c == "Harris, Kamala Devi": continue # Ignore virtual roll call header if it appears
            name = c.split()[0].strip().replace(",", "")
            if name in ["Uninstructed", "No", "Noncommitted", "None", "Uncommitted"]: 
                name = "Uncommitted"
            if name == "BLANK" or name.lower() == "blank": name = "Blank"
            if name in ["Jason", "PalmerJ", "Palmer"]: name = "Palmer"
            if name in ["Stephen", "LyonsS", "Lyons"]: name = "Lyons"
            if name in ["WilliamsonM", "Marianne"]: name = "Williamson"
            if name in ["PhillipsD", "Dean"]: name = "Phillips"
            
            clean_dels[name] = clean_dels.get(name, 0) + v
            
        if "Uncommitted" in clean_dels:
            clean_dels["Uncommitted"] -= unpledged
            if clean_dels["Uncommitted"] < 0: clean_dels["Uncommitted"] = 0
            
        # Clean up 0s
        final_dels = {k: v for k, v in clean_dels.items() if v > 0}
        actual_pledged[s] = final_dels
        
print(f"Parsed {len(actual_pledged)} states.")

with open("actual_pledged.json", "w") as f:
    json.dump(actual_pledged, f, indent=2)
