import pandas as pd
df = pd.read_excel('/Users/deep/Desktop/Profes/xcel/DnP Sheet.xlsx')
row = df[df['event_name'].str.contains('Doomsday', na=False, case=False)]
if not row.empty:
    print(row[['event_name', 'image_url']])
else:
    df2 = pd.read_excel('/Users/deep/Desktop/Profes/xcel/DnP.xlsx')
    row2 = df2[df2['event_name'].str.contains('Doomsday', na=False, case=False)]
    print(row2[['event_name', 'image_url']])
