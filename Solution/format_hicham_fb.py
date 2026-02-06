import pandas as pd
import os

FB_FILE = "Solution/backend/data/hichamcook_fb.csv"
OUTPUT_FILE = "Solution/backend/data/hichemcook_fb_formatted.csv"
RESTAURANT_NAME = "Hichem Cook"

if os.path.exists(FB_FILE):
    # Some FB exports might have a BOM
    df_fb = pd.read_csv(FB_FILE, encoding='utf-8-sig')
    
    # Mapping columns
    # hichemcook_data columns: comment_id, platform, source_name, comment_text, date, likesCount, video_id, video_url, restaurant
    
    formatted_df = pd.DataFrame()
    formatted_df['comment_id'] = df_fb['id']
    formatted_df['platform'] = 'facebook'
    formatted_df['source_name'] = df_fb['profileName']
    formatted_df['comment_text'] = df_fb['text']
    formatted_df['date'] = df_fb['date']
    formatted_df['likesCount'] = df_fb['likesCount'].fillna(0).astype(int)
    
    # For video_id, we can use facebookId if available, or extract from facebookUrl
    formatted_df['video_id'] = df_fb['facebookId']
    formatted_df['video_url'] = df_fb['facebookUrl']
    formatted_df['restaurant'] = RESTAURANT_NAME
    
    formatted_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Successfully formatted FB data to {OUTPUT_FILE}")
else:
    print(f"Error: {FB_FILE} not found.")
