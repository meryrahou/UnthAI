import pandas as pd
import os

FILE_PATH = "/Users/mery/GitHub/UnthAI/03_annotation/dataset_preprocessed.csv"

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    print(f"Original columns: {df.columns.tolist()}")

    # 1. Add new columns
    # Using 'treatment' as per guide consistency, but let's check user's 'treatement'
    new_cols = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
    for col in new_cols:
        df[col] = "" # Initialize with empty strings
    
    # 2. Delete unwanted columns
    cols_to_delete = ['Topic_REVIEWED', 'sentiment', 'intent']
    df.drop(columns=[c for c in cols_to_delete if c in df.columns], inplace=True)

    # Reorder columns: ID and Text first, then Metadata, then Annotation targets
    primary_cols = ['final_id', 'comment_text']
    remaining_cols = [c for c in df.columns if c not in primary_cols and c not in new_cols]
    final_order = primary_cols + remaining_cols + new_cols
    
    df = df[final_order]

    df.to_csv(FILE_PATH, index=False)
    print(f"Updated columns: {df.columns.tolist()}")
    print(f"Successfully modified {FILE_PATH}")
else:
    print(f"Error: {FILE_PATH} not found.")
