import pandas as pd
import os

FINAL_33 = "Solution/backend/data/FinalDataset33.csv"
TEST_DS = "Solution/backend/data/TestDataset.csv"
OUTPUT_FILE = "Solution/backend/data/TestDataset_Hichem_Combined.csv"

# Load new data
df_test = pd.read_csv(TEST_DS)
print(f"Loaded TestDataset.csv with {len(df_test)} rows.")

# Load historical data
if os.path.exists(FINAL_33):
    df_33 = pd.read_csv(FINAL_33)
    # Filter for Hicham Cook (Maps/IG)
    df_hicham_hist = df_33[df_33['source_name'] == 'Hicham Cook'].copy()
    print(f"Found {len(df_hicham_hist)} historical rows for Hicham Cook in FinalDataset33.csv")
    
    # Standardize historical data to match TestDataset structure
    # TestDataset columns: comment_id, platform, user_name, comment_text, date, likesCount, post_id, post_url, source_name, final_id
    
    hist_standardized = pd.DataFrame()
    hist_standardized['comment_id'] = df_hicham_hist['comment_id']
    hist_standardized['platform'] = df_hicham_hist['platform']
    hist_standardized['user_name'] = "Unknown" # FinalDataset33 doesn't have user names
    hist_standardized['comment_text'] = df_hicham_hist['comment_text']
    hist_standardized['date'] = df_hicham_hist['date']
    hist_standardized['likesCount'] = df_hicham_hist['likesCount']
    hist_standardized['post_id'] = df_hicham_hist['post_id']
    hist_standardized['post_url'] = "" # No URL in FinalDataset33
    hist_standardized['source_name'] = df_hicham_hist['source_name']
    hist_standardized['final_id'] = df_hicham_hist['final_id']
    
    # Combine
    combined_df = pd.concat([df_test, hist_standardized], ignore_index=True)
    
    # Optional: Deduplicate by final_id or comment_text
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['comment_text', 'platform'])
    after_dedup = len(combined_df)
    print(f"Combined count: {before_dedup} -> {after_dedup} (after deduplication)")
    
    combined_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved combined dataset to {OUTPUT_FILE}")
    
    # Replace TestDataset.csv so the next steps use the full data
    # os.replace(OUTPUT_FILE, TEST_DS)
    # print(f"Replaced {TEST_DS} with combined data.")
else:
    print(f"Error: {FINAL_33} not found.")
