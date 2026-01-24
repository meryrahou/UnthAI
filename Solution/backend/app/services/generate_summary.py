import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
SUMMARY_PATH = os.path.join(BASE_DIR, "../../data/Restaurant_Summary.csv")

def generate_summary():
    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Normalize platform names for consistency in aggregation
    df['platform_norm'] = df['platform'].str.lower().str.strip().str.replace(' ', '')
    
    # Group by restaurant and platform
    # Each row is a comment, unique post_id is a post
    summary = df.groupby(['source_name', 'platform_norm']).agg(
        posts=('post_id', 'nunique'),
        comments=('comment_id', 'count')
    ).unstack(fill_value=0)
    
    # Flatten multi-index columns
    summary.columns = [f"{col}_{plat}" for col, plat in summary.columns]
    summary = summary.reset_index()
    
    # Rename columns to match user request as closely as possible
    # Expected platforms: facebook, instagram, tiktok, googlemaps
    rename_map = {
        'posts_facebook': 'nb of posts fb',
        'comments_facebook': 'nb comments fb',
        'posts_instagram': 'nb posts insta',
        'comments_instagram': 'nb comments insta',
        'posts_tiktok': 'nb posts tik',
        'comments_tiktok': 'nb comm tik',
        'posts_googlemaps': 'nb of posts maps',
        'comments_googlemaps': 'nb comments maps'
    }
    
    # Check what columns actually exist before renaming
    actual_rename = {k: v for k, v in rename_map.items() if k in summary.columns}
    summary = summary.rename(columns=actual_rename)
    
    # Ensure all columns exist even if 0 (in case a platform has no data at all)
    required_cols = [
        'nb of posts fb', 'nb comments fb', 
        'nb posts insta', 'nb comments insta', 
        'nb posts tik', 'nb comm tik', 
        'nb of posts maps', 'nb comments maps'
    ]
    for col in required_cols:
        if col not in summary.columns:
            summary[col] = 0
            
    # Define explicitly which columns to sum for totals
    post_cols = ['nb of posts fb', 'nb posts insta', 'nb posts tik', 'nb of posts maps']
    comm_cols = ['nb comments fb', 'nb comments insta', 'nb comm tik', 'nb comments maps']
    
    # Calculate totals using explicit column lists
    summary['total posts'] = summary[post_cols].sum(axis=1)
    summary['total comments'] = summary[comm_cols].sum(axis=1)
    
    # Reorder columns as requested
    final_cols = ['source_name', 'nb of posts fb', 'nb comments fb', 'nb posts insta', 'nb comments insta', 
                  'nb posts tik', 'nb comm tik', 'nb of posts maps', 'nb comments maps', 'total posts', 'total comments']
    
    # Filter only available columns from requested list
    summary = summary[final_cols]
    
    # Sort: desc by total comments, then total posts
    summary = summary.sort_values(by=['total comments', 'total posts'], ascending=False)
    
    # Save
    summary.to_csv(SUMMARY_PATH, index=False)
    print(f"Summary generated successfully at {SUMMARY_PATH}")
    print("\nTop 5 Restaurants by total comments:")
    print(summary.head(5).to_string(index=False))

if __name__ == "__main__":
    generate_summary()
