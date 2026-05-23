import urllib.request
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np

state_abbrs = [
    'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 
    'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 
    'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 
    'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 
    'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY', 'PR', 'AS', 'GU', 'VI', 'MP', 'DA'
]

cd_delegates = []
pleo_delegates = []
at_large_delegates = []

print("Scraping DNC delegate data...")

for abbr in state_abbrs:
    url = f"https://www.thegreenpapers.com/P24/{abbr}-D"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        for tr in soup.find_all('tr'):
            tds = tr.find_all(['td', 'th'])
            if len(tds) > 3:
                text = tds[0].get_text(strip=True)
                if text.startswith('CD'):
                    try:
                        delegates = int(tds[3].get_text(strip=True))
                        cd_delegates.append(delegates)
                    except ValueError:
                        pass
                elif 'PLEO' in text:
                    try:
                        delegates = int(tds[3].get_text(strip=True))
                        pleo_delegates.append(delegates)
                    except ValueError:
                        pass
                elif 'At-Large' in text or 'Statewide' in text:
                    try:
                        delegates = int(tds[3].get_text(strip=True))
                        at_large_delegates.append(delegates)
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error fetching {abbr}: {e}")

print(f"Collected {len(cd_delegates)} districts, {len(pleo_delegates)} PLEO pools, {len(at_large_delegates)} At-Large pools.")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Histogram 1: District Delegates
bins_cd = np.arange(min(cd_delegates)-0.5, max(cd_delegates)+1.5, 1)
ax1.hist(cd_delegates, bins=bins_cd, color='#2c7bb6', edgecolor='white', alpha=0.8)
ax1.set_title('Distribution of Delegate Awards by District (CD)', fontsize=14)
ax1.set_xlabel('Number of Delegates per District', fontsize=12)
ax1.set_ylabel('Number of Districts', fontsize=12)
ax1.set_xticks(range(min(cd_delegates), max(cd_delegates)+1))
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Histogram 2: At-Large and PLEO Pools
bins_pools = np.arange(0, max(max(at_large_delegates), max(pleo_delegates)) + 5, 5)
ax2.hist(at_large_delegates, bins=bins_pools, color='#d7191c', alpha=0.6, label='At-Large Pools', edgecolor='white')
ax2.hist(pleo_delegates, bins=bins_pools, color='#fdae61', alpha=0.7, label='PLEO Pools', edgecolor='white')
ax2.set_title('Distribution of Statewide At-Large and PLEO Pool Sizes', fontsize=14)
ax2.set_xlabel('Number of Delegates in Pool', fontsize=12)
ax2.set_ylabel('Frequency (States/Territories)', fontsize=12)
ax2.legend(fontsize=11)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()

output_path = '/Users/m.dunitz/Desktop/code/crossratio/delegate_distributions.png'
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")
