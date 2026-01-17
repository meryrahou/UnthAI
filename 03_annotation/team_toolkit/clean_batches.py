import pandas as pd
import os
import argparse

def clean_batches(master_file, batch_file, ai_file):
    if not os.path.exists(master_file):
        print(f"⚠️ Master file {master_file} not found. Skipping cleanup.")
        return

    print(f"🧹 CLeaning batches against {master_file}...")
    
    # Load Master and get labeled IDs
    df_master = pd.read_csv(master_file, keep_default_na=False)
    labeled_mask = df_master['out_of_scope'].isin(['True', 'False', True, False])
    labeled_ids = set(df_master[labeled_mask]['comment_id'].unique())
    
    print(f"ℹ️ Found {len(labeled_ids)} labeled comments in Master.")

    # Clean Batch File
    if os.path.exists(batch_file):
        df_batch = pd.read_csv(batch_file)
        initial_len = len(df_batch)
        df_batch = df_batch[~df_batch['comment_id'].isin(labeled_ids)]
        removed = initial_len - len(df_batch)
        if removed > 0:
            df_batch.to_csv(batch_file, index=False)
            print(f"✅ Removed {removed} labeled rows from {batch_file}.")
        else:
            print(f"running clean on {batch_file}: No rows to remove.")

    # Clean AI File
    if os.path.exists(ai_file):
        df_ai = pd.read_csv(ai_file)
        initial_len = len(df_ai)
        df_ai = df_ai[~df_ai['comment_id'].isin(labeled_ids)]
        removed = initial_len - len(df_ai)
        if removed > 0:
            df_ai.to_csv(ai_file, index=False)
            print(f"✅ Removed {removed} labeled rows from {ai_file}.")
        else:
            print(f"running clean on {ai_file}: No rows to remove.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("master", help="Path to master CSV")
    parser.add_argument("--batch", default="batch_full.csv", help="Path to batch CSV")
    parser.add_argument("--ai", default="batch_full_ai.csv", help="Path to AI predictions CSV")
    args = parser.parse_args()
    
    clean_batches(args.master, args.batch, args.ai)
