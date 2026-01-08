import pandas as pd
import os

files = ["../01_collection/tiktok_dataset.csv", "../01_collection/tiktok_dataset_single.csv"]
dfs = []

for f in files:
    if os.path.exists(f):
        try:
            # Read CSV, skip empty lines or malformed ones if any
            df = pd.read_csv(f)
            print(f"Loaded {f}: {len(df)} rows")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")

if dfs:
    final_df = pd.concat(dfs, ignore_index=True)
    initial_count = len(final_df)
    
    # Deduplicate by comment_id
    final_df.drop_duplicates(subset=["comment_id"], keep="first", inplace=True)
    final_count = len(final_df)
    
    # Save to final
    final_file = "tiktok_final_dataset.csv"
    final_df.to_csv(final_file, index=False)
    
    print("\n--- Summary ---")
    print(f"Initial total rows (combined): {initial_count}")
    print(f"Final total rows (deduplicated): {final_count}")
    print(f"Duplicates removed: {initial_count - final_count}")
    print(f"Final dataset saved to: {final_file}")
else:
    print("No datasets found to merge.")
