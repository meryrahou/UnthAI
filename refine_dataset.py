import pandas as pd
import os

FILE_PATH = "tiktok_final_dataset.csv"

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    print(f"Loaded {FILE_PATH} with {len(df)} rows.")

    # 1. Rename 'source_name' to 'user_name'
    if 'source_name' in df.columns:
        df.rename(columns={'source_name': 'user_name'}, inplace=True)
        print("Renamed 'source_name' to 'user_name'.")

    # 2. Add 'source_name' column and extract @handle from 'video_url'
    def extract_handle(url):
        if pd.isna(url):
            return "unknown"
        # Example URL: https://www.tiktok.com/@le16emearrondissements16/video/7415172872856964357
        if '@' in url:
            try:
                # Extract part after @ and before the next /
                handle = "@" + url.split('@')[-1].split('/')[0]
                return handle
            except:
                return "unknown"
        return "unknown"

    df['source_name'] = df['video_url'].apply(extract_handle)
    print("Extracted restaurant handles into new 'source_name' column.")

    # Reorder columns for clarity
    cols = ['comment_id', 'platform', 'source_name', 'user_name', 'comment_text', 'date', 'likesCount', 'video_id', 'video_url', 'hashtag']
    # Filter to only existing columns in case some are missing
    cols = [c for c in cols if c in df.columns]
    df = df[cols]

    # Save back
    df.to_csv(FILE_PATH, index=False)
    print(f"Saved refined dataset to {FILE_PATH}.")
else:
    print(f"File {FILE_PATH} not found.")
