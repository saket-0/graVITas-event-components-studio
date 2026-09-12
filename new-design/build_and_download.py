import os
import re
import sys
import base64
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
import time

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EXCEL_FILES = [
    "/Users/deep/Desktop/Profes/NEW Excel/DNP 11.xlsx",
    "/Users/deep/Desktop/Profes/NEW Excel/Pre Grav DnP Events.xlsx"
]

DOWNLOAD_DIR = "downloads_offline"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

def fetch_and_save_image(ev):
    url = ev['image_url']
    name = ev['event_name']
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resolved = resolve_google_drive(url)
            if 'postimg.cc' in resolved or 'kommodo.ai' in resolved:
                if not resolved.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    resolved = resolve_html_page(resolved)
                    
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(resolved, headers=headers, timeout=20, verify=False)
            r.raise_for_status()
            
            ct = r.headers.get('Content-Type', '').lower()
            if 'svg' in ct or 'html' in ct:
                raise Exception("Invalid content type: " + ct)
                
            # Determine extension
            ext = '.png'
            if 'jpeg' in ct or 'jpg' in ct: ext = '.jpg'
            elif 'gif' in ct: ext = '.gif'
            elif 'webp' in ct: ext = '.webp'
            
            filepath = os.path.join(DOWNLOAD_DIR, sanitize_filename(name) + ext)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            
            b64 = base64.b64encode(r.content).decode('utf-8')
            ev['image_base64'] = b64
            print(f"[✓] Successfully downloaded {name}")
            return ev
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"[X] Error fetching {name} ({url}): {e}")
                
    return ev

def main():
    events_map = {}
    
    for file in EXCEL_FILES:
        print(f"Reading {file}...")
        df = pd.read_excel(file)
        cols = {c.lower().strip(): c for c in df.columns}
        
        name_col = next((c for k, c in cols.items() if 'event' in k and 'name' in k), None)
        image_col = next((c for k, c in cols.items() if 'image' in k), None)
        venue_col = next((c for k, c in cols.items() if 'venue' in k), None)
        start_col = next((c for k, c in cols.items() if 'start' in k and ('date' in k or 'datetime' in k or 'slot' in k)), None)
        end_col = next((c for k, c in cols.items() if 'end' in k and ('date' in k or 'datetime' in k or 'slot' in k)), None)
        
        if name_col:
            for _, row in df.iterrows():
                name = str(row[name_col]).strip()
                if name == 'nan' or not name: continue
                
                url = str(row[image_col]).strip() if image_col and pd.notna(row[image_col]) else ""
                if url == 'nan' or not url: continue
                
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
    print(f"Total unique events found with valid images: {len(events_list)}")
    
    print("Starting multi-threaded parallel downloads with fail-safes...")
    processed_events = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(fetch_and_save_image, ev) for ev in events_list]
        for future in as_completed(futures):
            processed_events.append(future.result())
            
    print("Downloads complete. Injecting default data into ui.html...")
    
    js_content = "window.DEFAULT_EVENTS = " + json.dumps(processed_events, separators=(',', ':')) + ";\n"
    script_tag = f"\n<script id=\"injected_defaults\">\n{js_content}</script>\n</body>"
    
    ui_path = "/Users/deep/Desktop/Profes/graVITas-event-components-studio-v8/new-design/ui.html"
    with open(ui_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
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
