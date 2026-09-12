import os
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import urllib.parse

DOWNLOAD_DIR = "downloads_offline"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

EXCEL_FILES = [
    "/Users/deep/Desktop/Profes/NEW Excel/DNP 11.xlsx",
    "/Users/deep/Desktop/Profes/NEW Excel/Pre Grav DnP Events.xlsx"
]

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip()

def resolve_google_drive(url):
    match = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    return url

def resolve_html_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200 and 'text/html' in r.headers.get('Content-Type', ''):
            soup = BeautifulSoup(r.text, 'html.parser')
            meta = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'twitter:image'})
            if meta and meta.get('content'):
                return urllib.parse.urljoin(url, meta['content'])
    except:
        pass
    return url

total_events = 0
events = set()

for file in EXCEL_FILES:
    df = pd.read_excel(file)
    cols = {c.lower().replace(' ', '_'): c for c in df.columns}
    name_col = cols.get('event_name')
    image_col = cols.get('image_url')
    if name_col and image_col:
        for _, row in df.iterrows():
            name = str(row[name_col]).strip()
            if name != 'nan' and name:
                url = str(row[image_col]).strip()
                if url != 'nan' and url:
                    events.add((name, url))

print(f"Total unique events found: {len(events)}")

for name, url in events:
    try:
        url = resolve_google_drive(url)
        if 'postimg.cc' in url or 'kommodo.ai' in url:
            if not url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                url = resolve_html_page(url)
        
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, verify=False)
        if r.status_code == 200:
            ext = '.png'
            ct = r.headers.get('Content-Type', '').lower()
            if 'jpeg' in ct or 'jpg' in ct: ext = '.jpg'
            elif 'gif' in ct: ext = '.gif'
            elif 'webp' in ct: ext = '.webp'
            
            with open(os.path.join(DOWNLOAD_DIR, sanitize_filename(name) + ext), 'wb') as f:
                f.write(r.content)
    except Exception as e:
        print(f"Failed {name}: {e}")

print(f"Done downloading to {DOWNLOAD_DIR}")
