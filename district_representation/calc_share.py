import urllib.request
from bs4 import BeautifulSoup

state_abbrs = [
    'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 
    'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 
    'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 
    'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 
    'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY', 'PR', 'AS', 'GU', 'VI', 'MP', 'DA'
]

all_pools = []

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
                if text.startswith('CD') or 'PLEO' in text or 'At-Large' in text or 'Statewide' in text:
                    try:
                        all_pools.append(int(tds[3].get_text(strip=True)))
                    except ValueError:
                        pass
    except:
        pass

total_delegates = sum(all_pools)
delegates_in_small_pools = sum(x for x in all_pools if x <= 5)

print(f"Total pledged delegates: {total_delegates}")
print(f"Delegates in pools of <= 5: {delegates_in_small_pools}")
print(f"Share: {delegates_in_small_pools / total_delegates:.4%}")
