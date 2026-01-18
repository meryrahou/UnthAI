import pandas as pd
import os
import argparse

def filter_active(batch_file):
    ai_file = batch_file.replace(".csv", "_ai.csv")
    if not os.path.exists(ai_file):
        print(f"❌ Error: AI predictions file {ai_file} not found. Run inference first!")
        return

    df = pd.read_csv(batch_file)
    ai_df = pd.read_csv(ai_file, keep_default_na=False)

    # Categories to check
    cats = ['ai_food', 'ai_service', 'ai_place', 'ai_delivery', 'ai_price', 'ai_treatment']
    
    # Identify rows where at least one category is not 'None'
    # Use lowercase comparison for robustness
    mask = ai_df[cats].apply(lambda x: any(str(val).lower() != 'none' for val in x), axis=1)
    
    active_ids = ai_df.loc[mask, 'comment_id'].tolist()
    
    df_active = df[df['comment_id'].isin(active_ids)].head(500)
    
    output_file = batch_file.replace(".csv", "_active.csv")
    df_active.to_csv(output_file, index=False)
    
    # Also create a matching _ai.csv for the tool to load suggestions
    # Filter ai_active to match the 100 rows in df_active
    final_active_ids = df_active['comment_id'].tolist()
    ai_active = ai_df[ai_df['comment_id'].isin(final_active_ids)]
    ai_active.to_csv(output_file.replace(".csv", "_ai.csv"), index=False)
    
    print(f"✅ Filtered {len(df_active)} active suggestions (out of {len(df)} total).")
    print(f"📁 Created: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The batch CSV file to filter")
    args = parser.parse_args()
    filter_active(args.file)
