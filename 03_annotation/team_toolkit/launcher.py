import subprocess
import os
import argparse
import sys
import pandas as pd

# --- Settings ---
# Running from team_toolkit/
MAIN_DATASET = "../annotation_part_1.csv"
BATCH_FILE = "batch_full.csv"
AI_FILE = "batch_full_ai.csv"

def get_active_count(ai_file):
    if not os.path.exists(ai_file):
        return 0
    df = pd.read_csv(ai_file, keep_default_na=False)
    cats = ['ai_food', 'ai_service', 'ai_place', 'ai_delivery', 'ai_price', 'ai_treatment']
    # Active = at least one category is not None
    mask = df[cats].apply(lambda x: any(str(val).lower() != 'none' for val in x), axis=1)
    return mask.sum()

def run_team_flow():
    print("🚀 Starting Team Annotation Flow (Smart Mode)...")
    
    # 1. Cleanup: Remove already labeled rows
    print(f"\n--- [1/4] Cleaning up batches ---")
    subprocess.run([sys.executable, "clean_batches.py", MAIN_DATASET, "--batch", BATCH_FILE, "--ai", AI_FILE])

    # 2. Check Cache
    active_count = get_active_count(AI_FILE)
    print(f"\n--- [2/4] Checking AI Cache ---")
    print(f"📊 Found {active_count} active suggestions in cache.")

    if active_count < 100:
        print(f"📉 Cache low (< 100). Running incremental inference...")
        
        # Load unlabeled batch data
        if not os.path.exists(BATCH_FILE):
             print(f"❌ Error: {BATCH_FILE} missing.")
             return

        df_batch = pd.read_csv(BATCH_FILE)
        
        # Load existing AI results to know what to skip
        if os.path.exists(AI_FILE):
            df_ai = pd.read_csv(AI_FILE)
            processed_ids = set(df_ai['comment_id'].unique())
        else:
            processed_ids = set()
        
        # Find rows not yet predicted
        df_to_predict = df_batch[~df_batch['comment_id'].isin(processed_ids)]
        
        # Take chunks of 200 until we have enough active rows or run out of data
        chunk_size = 200
        needed = 100 - active_count
        
        print(f"🔍 Need to find new active rows. Scanning in chunks of {chunk_size}...")
        
        while active_count < 100 and len(df_to_predict) > 0:
            # Prepare chunk
            chunk = df_to_predict.head(chunk_size)
            chunk_file = "temp_chunk.csv"
            chunk.to_csv(chunk_file, index=False)
            
            print(f"🤖 analyzing next {len(chunk)} rows...")
            subprocess.run([sys.executable, "inference.py", chunk_file])
            
            # Load results and append to main AI file
            chunk_ai_file = chunk_file.replace(".csv", "_ai.csv")
            if os.path.exists(chunk_ai_file):
                df_chunk_ai = pd.read_csv(chunk_ai_file)
                
                # Append to main AI file
                if os.path.exists(AI_FILE):
                    df_chunk_ai.to_csv(AI_FILE, mode='a', header=False, index=False)
                else:
                    df_chunk_ai.to_csv(AI_FILE, index=False)
                
                # Update counts
                # Re-read or just calculate delta
                cats = ['ai_food', 'ai_service', 'ai_place', 'ai_delivery', 'ai_price', 'ai_treatment']
                # keep_default_na=False essential for 'None' check? 
                # Actually subprocess wrote it, so we read it back. Pandas might read 'None' as string or NaN.
                # Assuming 'None' string.
                # Let's just re-read full active count for safety or check chunk:
                # Simple check on chunk:
                mask_chunk = df_chunk_ai[cats].apply(lambda x: any(str(val).lower() != 'none' and str(val).lower() != 'nan' for val in x), axis=1)
                new_active = mask_chunk.sum()
                active_count += new_active
                print(f"   Found {new_active} active in this chunk. Total Cached: {active_count}")
                
                # Cleanup temp
                os.remove(chunk_file)
                os.remove(chunk_ai_file)
                
                # Advance cursor
                df_to_predict = df_to_predict.iloc[len(chunk):]
            else:
                print("❌ Inference failed for chunk.")
                break
    else:
        print("✅ Cache sufficient. Skipping inference.")

    # 3. Filter Active & Save for Tool
    # The filter_active script handles taking the head(100)
    print(f"\n--- [3/4] Preparing Tool Batch ---")
    subprocess.run([sys.executable, "filter_active.py", BATCH_FILE])
    active_file = BATCH_FILE.replace(".csv", "_active.csv")

    # 4. Launch Tool
    print(f"\n--- [4/4] Launching Annotation Tool ---")
    print(f"💡 Target: {active_file}")
    print("💡 Open http://localhost:8000 in your browser.")
    try:
        subprocess.run([sys.executable, "annotation_tool.py", active_file, "--master", MAIN_DATASET])
    except KeyboardInterrupt:
        print("\n🛑 Tool closed.")

    # 5. Sync handled by tool immediately, but we can do a final merge/clean check if needed.
    # Actually, we should clean batches again? Or just leave it for next run.
    # Leaving for next run is safer/faster.
    print("\n✅ Session finished. Run launcher again for next batch.")

if __name__ == "__main__":
    # Check Master
    if os.path.exists(MAIN_DATASET):
        # Always check if we need to refill batch_full_ai.csv from master if empty?
        # No, batch_full.csv is the source.
        
        # Ensure batch_full.csv exists
        if not os.path.exists(BATCH_FILE):
             print(f"📦 First run: Pulling ALL unlabeled data from {MAIN_DATASET}...")
             df_master = pd.read_csv(MAIN_DATASET)
             unlabeled = df_master[~df_master['out_of_scope'].isin(['True', 'False', True, False])]
             unlabeled.to_csv(BATCH_FILE, index=False)
             print(f"✅ Created {BATCH_FILE} with {len(unlabeled)} rows.")
        
        run_team_flow()
    else:
        print(f"❌ Error: {MAIN_DATASET} not found.")
