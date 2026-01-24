import pandas as pd
import json
import os
import sys

# Mocking the environment for testing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_PATH = os.path.join(BASE_DIR, "../../data/processed_casbah_istanbul.csv")

def test_get_posts():
    if not os.path.exists(PROCESSED_PATH):
        print(f"File not found: {PROCESSED_PATH}")
        return

    df_user = pd.read_csv(PROCESSED_PATH)
    print(f"Total rows for Casbah Istanbul: {len(df_user)}")
    
    d_df = df_user.copy()
    d_df['date_dt'] = pd.to_datetime(d_df['date'], format='mixed', utc=True, errors='coerce')
    
    # Filter as in screenshot: 2017-02-06 to 2026-01-01
    start_date = "2017-02-06"
    end_date = "2026-01-01"
    
    s_dt = pd.to_datetime(start_date, utc=True)
    e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
    
    d_df_filtered = d_df[(d_df['date_dt'] >= s_dt) & (d_df['date_dt'] < e_dt)]
    print(f"Rows after date filter: {len(d_df_filtered)}")
    
    post_ids = d_df_filtered['post_id'].unique().tolist()
    print(f"Unique post_ids: {post_ids}")
    
    posts = []
    for pid in post_ids:
        if pd.isna(pid):
            print("Found NaN post_id!")
            continue
            
        p_df_full = df_user[df_user['post_id'] == pid]
        print(f"Post {pid} has {len(p_df_full)} comments in full history.")
        
        if p_df_full.empty:
            continue
            
        platform = p_df_full['platform'].iloc[0]
        p_df_full = p_df_full.copy()
        p_df_full['date_dt'] = pd.to_datetime(p_df_full['date'], format='mixed', utc=True)
        creation_date_dt = p_df_full['date_dt'].min()
        
        # Check strict filter
        if not (s_dt <= creation_date_dt < e_dt):
            print(f"Post {pid} hidden by strict filter (Creation date: {creation_date_dt})")
            continue
            
        posts.append(pid)

    print(f"Final posts list count: {len(posts)}")

if __name__ == "__main__":
    test_get_posts()
