import subprocess
import os
import argparse
import sys
import pandas as pd

# --- Settings ---
MAIN_DATASET = "../annotation_part_1.csv" # Adjusted path assuming we run from team_toolkit/

def run_team_flow(subset_file):
    print("🚀 Starting Team Annotation Flow...")
    
    # 1. Run Inference
    print(f"\n--- [1/4] Generating AI Suggestions for {subset_file} ---")
    subprocess.run([sys.executable, "inference.py", subset_file])

    # 2. Filter Active Only
    print(f"\n--- [2/4] Filtering for 'Active' Suggestions (Non-None) ---")
    subprocess.run([sys.executable, "filter_active.py", subset_file])
    active_file = subset_file.replace(".csv", "_active.csv")

    # 3. Launch Annotation Tool
    print(f"\n--- [3/4] Launching Annotation Tool on ACTIVE rows ---")
    print(f"💡 Target: {active_file}")
    print("💡 Open http://localhost:8000 in your browser.")
    print("💡 Press CTRL+C in this terminal when you are COMPLETELY FINISHED labeling.")
    try:
        subprocess.run([sys.executable, "annotation_tool.py", active_file, "--master", MAIN_DATASET])
    except KeyboardInterrupt:
        print("\n🛑 Tool closed.")

    # 4. Sync Back to Main Dataset
    print(f"\n--- [4/4] Syncing Labels Back to Main Dataset ---")
    if os.path.exists(MAIN_DATASET):
        # Sync from the ACTIVE file we just labeled
        subprocess.run([sys.executable, "merge_sync.py", active_file, MAIN_DATASET])
    else:
        print(f"⚠️ Warning: Main dataset not found at {MAIN_DATASET}. skipping auto-sync.")
        print(f"You can manually sync later using: python merge_sync.py {subset_file} /path/to/main.csv")

    print("\n✅ All done! Your labels have been merged into the master file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="Optional: specific CSV file. If omitted, we pull 100 fresh rows from MASTER.")
    args = parser.parse_args()
    
    target_file = args.file
    
    # Auto-Batch Logic
    if not target_file:
        if os.path.exists(MAIN_DATASET):
            print(f"📦 No file provided. Pulling ALL unlabeled rows from {MAIN_DATASET}...")
            df_master = pd.read_csv(MAIN_DATASET)
            # Find rows where out_of_scope is completely empty/NaN
            unlabeled = df_master[~df_master['out_of_scope'].isin(['True', 'False', True, False])].head(1000)
            if len(unlabeled) == 0:
                print("🎉 No unlabeled rows left in Master! You are done.")
                sys.exit()
            
            print(f"📊 Found {len(unlabeled)} unlabeled rows. Preparing full batch...")
            target_file = "batch_full.csv"
            unlabeled.to_csv(target_file, index=False)
            print(f"✅ Created {target_file}")
        else:
            print(f"❌ Error: {MAIN_DATASET} not found. Please provide a file or fix the path.")
            sys.exit()

    if not os.path.exists(target_file):
        print(f"❌ Error: File {target_file} not found.")
    else:
        run_team_flow(target_file)
