import subprocess
import os
import argparse
import sys
import pandas as pd

# --- Default Settings ---
def run_instant_flow(main_file, ai_source):
    print("🚀 Starting Instant Annotation Flow (Global AI Mode)...")
    
    batch_active = "batch_full_active.csv"
    batch_active_ai = "batch_full_active_ai.csv"

    if not os.path.exists(ai_source):
        print(f"❌ Error: AI predictions not found at {ai_source}")
        print(f"Please run: python3 06_train_inference.py --input {main_file} --predict_only")
        return

    # 1. Load AI Suggestions
    print("📊 Loading AI Suggestions...")
    ai_df = pd.read_csv(ai_source, keep_default_na=False)
    
    # 2. Filter for Active (not all None)
    cats = ['ai_food', 'ai_service', 'ai_place', 'ai_delivery', 'ai_price', 'ai_treatment']
    mask_active = ai_df[cats].apply(lambda x: any(str(v).lower() != 'none' for v in x), axis=1)
    active_ids_df = ai_df[mask_active].copy()
    
    print(f"🔍 Found {len(active_ids_df)} active suggestions in total.")

    # 3. Load Master and Filter out already labeled
    print(f"🧹 Filtering out already labeled rows from {main_file}...")
    master_df = pd.read_csv(main_file, keep_default_na=False)
    labeled_mask = master_df['out_of_scope'].isin(['True', 'False', True, False])
    labeled_ids = set(master_df[labeled_mask]['comment_id'].unique())
    
    # Keep only unlabeled active suggestions
    unlabeled_active_ai = active_ids_df[~active_ids_df['comment_id'].isin(labeled_ids)]
    
    if len(unlabeled_active_ai) == 0:
        print("🎉 Mission Accomplished! No unlabeled active comments left.")
        return

    # Take all of them
    batch_ai = unlabeled_active_ai.copy()
    batch_ids = batch_ai['comment_id'].tolist()
    
    # 4. Get text for these IDs
    batch_text = master_df[master_df['comment_id'].isin(batch_ids)]
    
    # 5. Save temporary batch files for the tool
    batch_text.to_csv(batch_active, index=False)
    batch_ai.to_csv(batch_active_ai, index=False)
    
    print(f"✅ Prepared {len(batch_text)} comments for this session.")
    
    # Launch Tool
    print("\n--- Launching Annotation Tool ---")
    tool_path = "annotation_tool.py"
    subprocess.run([sys.executable, tool_path, batch_active, "--master", main_file])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default="../annotation_part_1.csv", help="Master CSV to label")
    parser.add_argument("--ai", help="Pre-labeled AI CSV for suggestions")
    args = parser.parse_args()

    if not args.ai:
        args.ai = args.master.replace(".csv", "_ai.csv")

    run_instant_flow(args.master, args.ai)
