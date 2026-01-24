import pandas as pd
import os
import sys

def generate_post_ids(df, max_comments_per_post=356):
    """
    Generates post_ids based on contiguous blocks of restaurant/platform.
    """
    post_ids = []
    current_post_id = 10000
    prev_restaurant = None
    prev_platform = None
    count_in_current_post = 0

    for idx, row in df.iterrows():
        restaurant = str(row['source_name']).strip().lower()
        platform = str(row['platform']).strip().lower()

        # Logic to start a new post_id:
        # 1. Restaurant changes
        # 2. Platform changes
        # 3. We exceed max comments per post
        if (restaurant != prev_restaurant or 
            platform != prev_platform or 
            count_in_current_post >= max_comments_per_post):
            
            current_post_id += 1
            count_in_current_post = 0
        
        post_ids.append(float(current_post_id))
        count_in_current_post += 1
        prev_restaurant = restaurant
        prev_platform = platform
    
    df['post_id'] = post_ids
    return df

def process_missing_columns(csv_path):
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Remove existing post_id if it exists to start fresh
    if 'post_id' in df.columns:
        df = df.drop(columns=['post_id'])
    
    print("Sorting dataset by source_name and platform...")
    # Sorting ensures that comments for the same restaurant/platform are contiguous,
    # which allows the generate_post_ids logic to group them correctly.
    df = df.sort_values(by=['source_name', 'platform']).reset_index(drop=True)
    
    print("Generating post_ids based on grouping logic...")
    df = generate_post_ids(df)
    
    # Save back
    df.to_csv(csv_path, index=False)
    print(f"Done! Updated {csv_path} with new post_ids.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
    process_missing_columns(CSV_PATH)
