import pandas as pd
import os
import numpy as np

FILE_PATH = "/Users/mery/GitHub/UnthAI/03_annotation/dataset_preprocessed.csv"
OUTPUT_DIR = "/Users/mery/GitHub/UnthAI/03_annotation"

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    total_rows = len(df)
    print(f"Total rows to split: {total_rows}")

    # Split into 4 parts
    parts = np.array_split(df, 4)
    
    for i, part in enumerate(parts):
        part_name = f"annotation_part_{i+1}.csv"
        part_path = os.path.join(OUTPUT_DIR, part_name)
        part.to_csv(part_path, index=False)
        print(f"Saved {part_name} with {len(part)} rows.")

    print("\nSUCCESS! Dataset split into 4 equal parts.")
else:
    print(f"Error: {FILE_PATH} not found.")
