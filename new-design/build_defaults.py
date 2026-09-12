import os
import re
import sys
import base64
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import urllib.parse

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
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

def fetch_image_base64(url):
    try:
        url = resolve_google_drive(url)
        if 'postimg.cc' in url or 'kommodo.ai' in url:
            if not url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                url = resolve_html_page(url)
                
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        r.raise_for_status()
        
        # Check content type
        ct = r.headers.get('Content-Type', '').lower()
        if 'svg' in ct or 'html' in ct:
            return None
        
        b64 = base64.b64encode(r.content).decode('utf-8')
        return b64
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    events_map = {}
    
    for file in EXCEL_FILES:
        print(f"Reading {file}...")
        df = pd.read_excel(file)
        
        # Determine relevant columns (Venue Alloted vs venue_alloted etc)
        # Standardize column names
        cols = {c.lower().replace(' ', '_'): c for c in df.columns}
        
        name_col = cols.get('event_name')
        image_col = cols.get('image_url')
        venue_col = cols.get('venue_alloted') or cols.get('venue')
        start_col = cols.get('slot_start') or cols.get('slot_start_datetime')
        end_col = cols.get('slot_end') or cols.get('slot_end_datetime')
        
        if name_col and image_col:
            for _, row in df.iterrows():
                name = str(row[name_col]).strip()
                if name == 'nan' or not name: continue
                
                url = str(row[image_col]).strip() if pd.notna(row[image_col]) else ""
                venue = str(row[venue_col]).strip() if venue_col and pd.notna(row[venue_col]) else ""
                start = str(row[start_col]).strip() if start_col and pd.notna(row[start_col]) else ""
                end = str(row[end_col]).strip() if end_col and pd.notna(row[end_col]) else ""
                
                if name not in events_map:
                    events_map[name] = {
                        'event_name': name,
                        'image_url': url,
                        'venue_alloted': venue,
                        'slot_start_datetime': start,
                        'slot_end_datetime': end
                    }

    events_list = list(events_map.values())
    print(f"Found {len(events_list)} unique events.")
    
    # Fetch images concurrently
    def process_event(ev):
        if ev['image_url']:
            print(f"Fetching {ev['event_name']}...")
            b64 = fetch_image_base64(ev['image_url'])
            if b64:
                ev['image_base64'] = b64
        return ev
        
    with ThreadPoolExecutor(max_workers=10) as ex:
        events_list = list(ex.map(process_event, events_list))
        
    # Generate JS block
    js_content = "window.DEFAULT_EVENTS = " + json.dumps(events_list, separators=(',', ':')) + ";\n"
    
    script_tag = f"\n<script id=\"injected_defaults\">\n{js_content}</script>\n</body>"
    
    # Update ui.html
    ui_path = "/Users/deep/Desktop/Profes/graVITas-event-components-studio-v8/new-design/ui.html"
    with open(ui_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Remove existing injected tag if present
    html = re.sub(r'\n<script id="injected_defaults">.*?</script>\n', '\n', html, flags=re.DOTALL)
    
    if '</body>' in html:
        html = html.replace('</body>', script_tag)
    else:
        html += script_tag
        
    with open(ui_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Successfully injected default data into {ui_path} (length: {len(js_content)} bytes)")

if __name__ == '__main__':
    main()
