import pandas as pd
import os
import sys

def merge_case_differences(csv_path):
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Fill NAs to avoid issues
    df['source_name'] = df['source_name'].fillna("Unknown")
    
    # Find all unique names
    unique_names = df['source_name'].unique()
    
    # Create a mapping from lowercase to a representative original case
    # Logic: Pick the most frequent case version for each restaurant
    name_counts = df['source_name'].value_counts()
    
    case_map = {}
    for name in unique_names:
        low_name = name.lower().strip()
        if low_name not in case_map:
            case_map[low_name] = name
        else:
            # If we find a version that is more frequent, use it as the representative
            if name_counts.get(name, 0) > name_counts.get(case_map[low_name], 0):
                case_map[low_name] = name
                
    print(f"Detected {len(unique_names)} unique variations. Reducing based on case...")
    
    # Apply the merge
    # We use a copy to avoid SettingWithCopyWarning
    df['source_name_new'] = df['source_name'].apply(lambda x: case_map[x.lower().strip()])
    
    changes = df[df['source_name'] != df['source_name_new']]
    num_changes = len(changes)
    
    if num_changes > 0:
        print(f"Merging {num_changes} rows with case/whitespace variations...")
        df['source_name'] = df['source_name_new']
        df = df.drop(columns=['source_name_new'])
        df.to_csv(csv_path, index=False)
        print("CSV updated successfully.")
    else:
        print("No case differences found to merge.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
    merge_case_differences(CSV_PATH)
