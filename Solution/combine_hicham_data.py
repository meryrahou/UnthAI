import pandas as pd
import os

TK_FILE = "Solution/backend/data/hichemcook_data.csv"
FB_FILE = "Solution/backend/data/hichemcook_fb_formatted.csv"
OUTPUT_FILE = "Solution/backend/data/hichemcook_combined_raw.csv"

dfs = []
if os.path.exists(TK_FILE):
    dfs.append(pd.read_csv(TK_FILE))
if os.path.exists(FB_FILE):
    dfs.append(pd.read_csv(FB_FILE))

if dfs:
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Combined {len(combined_df)} rows to {OUTPUT_FILE}")
else:
    print("No input files found.")
