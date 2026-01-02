import pandas as pd
import os

FILE_PATH = "tiktok_final_dataset.csv"

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    initial_count = len(df)
    print(f"Loaded {FILE_PATH} with {initial_count} rows.")

    # Patterns to match: French flag emoji (🇫🇷), $, €
    # French flag is usually \U0001f1eb\U0001f1f7
    french_flag = '🇫🇷'
    target_symbols = ['$', '€', french_flag]
    
    # Filtering logic
    # We drop rows where any of these exist in 'comment_text'
    # Use str.contains with regex=False for simple matches if possible, or '|'.join for list
    mask = df['comment_text'].str.contains(r'\$|€|🇫🇷', na=False, regex=True)
    
    df_filtered = df[~mask].copy()
    final_count = len(df_filtered)
    
    # Save back
    df_filtered.to_csv(FILE_PATH, index=False)
    
    print(f"\n--- Filtering Summary ---")
    print(f"Initial rows: {initial_count}")
    print(f"Final rows: {final_count}")
    print(f"Rows removed: {initial_count - final_count}")
    print(f"Updated dataset saved to {FILE_PATH}.")
else:
    print(f"File {FILE_PATH} not found.")
