import pandas as pd
import os
import argparse

def merge_back(source_file, target_file):
    if not os.path.exists(source_file) or not os.path.exists(target_file):
        print(f"❌ Missing files: {source_file} or {target_file}")
        return

    df_source = pd.read_csv(source_file)
    df_target = pd.read_csv(target_file)

    # Filtering only labeled rows
    labeled_mask = df_source['out_of_scope'].isin(['True', 'False', True, False])
    labeled_source = df_source[labeled_mask].copy()

    if len(labeled_source) == 0:
        print("⚠️ No labeled rows to merge.")
        return

    print(f"🔄 Syncing {len(labeled_source)} labels back to {target_file}...")

    df_target.set_index('comment_id', inplace=True)
    df_source_indexed = labeled_source.set_index('comment_id')

    cols_to_update = ['food', 'service', 'place', 'delivery', 'price', 'treatment', 'out_of_scope']
    df_target.update(df_source_indexed[cols_to_update])

    df_target.reset_index(inplace=True)
    df_target.to_csv(target_file, index=False)
    print("✅ Sync Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Team member's CSV")
    parser.add_argument("target", help="Main project CSV")
    args = parser.parse_args()
    merge_back(args.source, args.target)
