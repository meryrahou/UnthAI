import pandas as pd
import os
import json
from datetime import datetime

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: In the actual app, refresh_restaurant_data creates the file.
# Since I'm debugging, I'll simulate that if needed or use the existing one.
MASTER_CSV = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")

def debug_get_posts(restaurant_name, start_date, end_date):
    print(f"Debugging posts for: {restaurant_name}")
    print(f"Filter: {start_date} to {end_date}")
    
    # 1. Simulate data_manager.refresh_restaurant_data
    df_master = pd.read_csv(MASTER_CSV)
    df_user = df_master[df_master['source_name'].str.lower() == restaurant_name.lower()].copy()
    df_user = df_user.fillna("")
    
    # Simulate the feeling/prediction generation normally done in refresh_restaurant_data
    # (Just enough to make get_posts work)
    df_user['feeling'] = 'positive' 
    df_user['model_prediction'] = '[]'
    
    # 2. Main logic from main.py
    d_df = df_user.copy()
    d_df['date_dt'] = pd.to_datetime(d_df['date'], format='mixed', utc=True, errors='coerce')
    
    if start_date and end_date:
        s_dt = pd.to_datetime(start_date, utc=True)
        e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
        d_df = d_df[(d_df['date_dt'] >= s_dt) & (d_df['date_dt'] < e_dt)]

    print(f"Rows after filtering: {len(d_df)}")
    
    post_ids = d_df['post_id'].unique().tolist()
    print(f"Unique post_ids: {len(post_ids)}")
    
    posts = []
    for pid in post_ids[:20]: # Only first 20 for brevity
        print(f"Analyzing pid: {pid}")
        # Always use the FULL history to determine the true post date
        p_df_full = df_user[df_user['post_id'] == pid].copy()
        if p_df_full.empty:
            print(f"  Empty p_df_full for {pid}")
            continue

        p_df_full['date_dt'] = pd.to_datetime(p_df_full['date'], format='mixed', utc=True)
        creation_date_dt = p_df_full['date_dt'].min()
        print(f"  Creation date: {creation_date_dt}")
        
        if start_date and end_date:
             s_dt = pd.to_datetime(start_date, utc=True)
             e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
             if not (s_dt <= creation_date_dt < e_dt):
                 print(f"  Hidden by strict filter")
                 continue
        
        posts.append(pid)
        
    print(f"Successfully processed {len(posts)} posts.")

if __name__ == "__main__":
    # Filter from screenshot: 2017-02-06 to 2026-01-01
    debug_get_posts("Casbah Istanbul", "2017-02-06", "2026-01-01")
