import os
import re
import sys
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_DIR = "downloads"
EXCEL_FILES = [
    "/Users/deep/Desktop/Profes/xcel/DnP Sheet.xlsx",
    "/Users/deep/Desktop/Profes/xcel/DnP.xlsx"
]

def ensure_dir():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

def sanitize_filename(name):
    # Remove invalid characters for macOS/Windows filenames
    return re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip()

def resolve_google_drive(url):
    match = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    return url

def resolve_html_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and 'text/html' in r.headers.get('Content-Type', ''):
            soup = BeautifulSoup(r.text, 'html.parser')
            meta = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'twitter:image'})
            if meta and meta.get('content'):
                resolved = urllib.parse.urljoin(url, meta['content'])
                return resolved
    except Exception as e:
        print(f"  [WARN] Failed to resolve HTML for {url}: {e}")
    return url

def download_image(event_name, original_url):
    if not original_url or pd.isna(original_url):
        return False, "No URL"
        
    url = str(original_url).strip()
    safe_name = sanitize_filename(event_name)
    
    # Check if already downloaded
    existing_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(safe_name + ".")]
    if existing_files:
        return True, f"Already downloaded as {existing_files[0]}"

    try:
        # Pre-process URLs
        url = resolve_google_drive(url)
        
        if 'postimg.cc' in url or 'kommodo.ai' in url:
            if not url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                url = resolve_html_page(url)
        
        # Download
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15, stream=True)
        r.raise_for_status()
        
        # Determine extension from content-type
        ct = r.headers.get('Content-Type', '').lower()
        ext = '.png'
        if 'jpeg' in ct or 'jpg' in ct: ext = '.jpg'
        elif 'gif' in ct: ext = '.gif'
        elif 'webp' in ct: ext = '.webp'
        elif 'bmp' in ct: ext = '.bmp'
        
        filename = f"{safe_name}{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return True, f"Downloaded {filename}"
    except Exception as e:
        return False, str(e)

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()
        
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

def main():
    ensure_dir()
    
    events = []
    for file in EXCEL_FILES:
        print(f"Reading {file}...")
        df = pd.read_excel(file)
        if 'event_name' in df.columns and 'image_url' in df.columns:
            for _, row in df.iterrows():
                events.append((row['event_name'], row['image_url']))
    
    # Deduplicate
    events = list(set(events))
    print(f"Found {len(events)} unique events. Starting downloads...")
    
    success = 0
    failed = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(download_image, name, url): (name, url) for name, url in events}
        
        for i, future in enumerate(futures):
            name, url = futures[future]
            try:
                ok, msg = future.result()
                if ok:
                    success += 1
                    print(f"[{i+1}/{len(events)}] ✓ {name}")
                else:
                    failed.append((name, url, msg))
                    print(f"[{i+1}/{len(events)}] ✗ {name} -> {msg}")
            except Exception as e:
                failed.append((name, url, str(e)))
                print(f"[{i+1}/{len(events)}] ✗ {name} -> {e}")
                
    print("\n" + "="*40)
    print(f"DOWNLOAD COMPLETE")
    print(f"Successfully downloaded: {success}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed events:")
        for name, url, err in failed:
            print(f" - {name}: {err} ({url})")
            
    print("\n" + "="*40)
    print("Starting local CORS server on http://localhost:8000")
    print("Point your Figma plugin to use the local server.")
    print("Press Ctrl+C to stop.")
    
    os.chdir(DOWNLOAD_DIR)
    httpd = HTTPServer(('localhost', 8000), CORSRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == '__main__':
    main()
