import os
from PIL import Image

DOWNLOAD_DIR = "downloads"
files = os.listdir(DOWNLOAD_DIR)
image_files = [f for f in files if os.path.isfile(os.path.join(DOWNLOAD_DIR, f)) and f != '.DS_Store']

print(f"Total files in downloads/: {len(image_files)}")

invalid = []
for f in image_files:
    filepath = os.path.join(DOWNLOAD_DIR, f)
    if os.path.getsize(filepath) == 0:
        invalid.append((f, "0 bytes"))
        continue
    
    try:
        with Image.open(filepath) as img:
            img.verify()
    except Exception as e:
        invalid.append((f, f"Corrupted or invalid: {str(e)}"))

print(f"Valid images: {len(image_files) - len(invalid)}")
if invalid:
    print("\nInvalid images found:")
    for name, reason in invalid:
        print(f" - {name}: {reason}")
else:
    print("\nAll downloaded images are perfectly valid and readable!")
