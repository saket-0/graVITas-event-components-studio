import pandas as pd

failed_events = [
    "THE COSMOS PROTOCOL", "Bad Idea Billionaires 2.0", "FaultLine", "MyoSync", "HackGrid ",
    "Nutpam", "LAUNCHPAD'26", "Autodesk Fusion Workshop", "Follow Me: Build a Human Tracking Robot",
    "Autodesk Fusion x Standards: Industry Hackathon", "Alice in Borderland", "Crisis Inc. 3.0",
    "HuntVerse", "Manufacture Your Dream : RC Car Building and Racing", "Money Heist: Blueprint Vault — Tower Edition",
    "Operation signal chase", "RoboInvest", "Statecraft: India 2050", "The Last of Us", "Aero-crafters",
    "Cosmopoly", "EnergyThon", "HuntScape", "Right! A Tune", "Wanna Crack GSoc 3.0", "NERF WARS",
    "Squad-Up", "AIoTopia: Future with IoT", "Breadwinner", "Humanity Through Lens",
    "ISHRAE HVAC HACKATHON - ENGINEER THE FUTURE OF COOLING", "The Grand GraVITas Quiz", "Insight for Impact"
]

urls = []

for file in ["/Users/deep/Desktop/Profes/xcel/DnP Sheet.xlsx", "/Users/deep/Desktop/Profes/xcel/DnP.xlsx"]:
    df = pd.read_excel(file)
    # Check if 'event_name' and 'image_url' exist
    if 'event_name' in df.columns and 'image_url' in df.columns:
        for idx, row in df.iterrows():
            if str(row['event_name']).strip() in [e.strip() for e in failed_events]:
                urls.append((row['event_name'], row['image_url']))

for name, url in set(urls):
    print(f"{name}: {url}")
