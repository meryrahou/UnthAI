import pandas as pd
import os
import glob

# Apply to all partitions and the main preprocessed file
FILES_TO_UPDATE = glob.glob("/Users/mery/GitHub/UnthAI/03_annotation/*.csv")

for file_path in FILES_TO_UPDATE:
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"Updating {os.path.basename(file_path)}...")

        # Add 'out_of_scope' if it doesn't exist
        if 'out_of_scope' not in df.columns:
            df['out_of_scope'] = "" # Initialize as empty/unlabeled
        
        # Ensure 'out_of_scope' is placed after the topic columns
        topic_cols = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
        other_cols = [c for c in df.columns if c not in topic_cols and c != 'out_of_scope']
        
        final_order = other_cols + topic_cols + ['out_of_scope']
        df = df[[c for c in final_order if c in df.columns]]

        df.to_csv(file_path, index=False)
        print(f"Successfully updated columns in {os.path.basename(file_path)}")
