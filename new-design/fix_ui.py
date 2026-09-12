import re

with open('/Users/deep/Desktop/Profes/graVITas-event-components-studio-v8/new-design/ui.html', 'r') as f:
    content = f.read()

# Fix 1: loadEvents
old1 = """        slot_end_datetime: String(r.slot_end_datetime || ''),
        source_file: String(r.source_file || label),"""
new1 = """        slot_end_datetime: String(r.slot_end_datetime || ''),
        venue_alloted: String(r.venue_alloted || ''),
        image_base64: String(r.image_base64 || ''),
        source_file: String(r.source_file || label),"""
content = content.replace(old1, new1)

# Fix 2: parseDelimited
old2 = """      slot_start_datetime: o.slot_start_datetime || '',
      slot_end_datetime: o.slot_end_datetime || '',"""
new2 = """      slot_start_datetime: o.slot_start_datetime || '',
      slot_end_datetime: o.slot_end_datetime || '',
      venue_alloted: o.venue_alloted || '',"""
content = content.replace(old2, new2)

# Fix 3: parseXlsx
old3 = """        image_url: String(obj.image_url || ''),
        slot_start_datetime: excelDateMaybe(obj.slot_start_datetime),
        slot_end_datetime: excelDateMaybe(obj.slot_end_datetime),"""
new3 = """        image_url: String(obj.image_url || ''),
        venue_alloted: String(obj.venue_alloted || ''),
        slot_start_datetime: excelDateMaybe(obj.slot_start_datetime),
        slot_end_datetime: excelDateMaybe(obj.slot_end_datetime),"""
content = content.replace(old3, new3)

with open('/Users/deep/Desktop/Profes/graVITas-event-components-studio-v8/new-design/ui.html', 'w') as f:
    f.write(content)
print("done")
