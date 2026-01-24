import pandas as pd
import os
import sys
from detect_duplicates import check_similar_names

def interactive_merge(csv_path):
    print(f"Reading {csv_path} for interactive merging...")
    similar_pairs = check_similar_names(csv_path)
    
    if not similar_pairs:
        print("No similar restaurant names detected.")
        return

    merges = {}
    print("\nStarting Interactive Merge Process...")
    print("Type 'y' to merge (First name will be replaced by the second), 'n' to skip, or 'q' to stop.")
    
    for n1, n2, score in similar_pairs:
        # Avoid already merged or chain merges for now to keep it simple
        if n1 in merges or n2 in merges:
            continue
            
        choice = input(f"Merge '{n1}' INTO '{n2}'? (Similarity: {score:.2f}) [y/n/q]: ").strip().lower()
        
        if choice == 'y':
            merges[n1] = n2
            print(f"Recorded: {n1} -> {n2}")
        elif choice == 'q':
            break
        else:
            continue

    if merges:
        print(f"\nApplying {len(merges)} merges...")
        df = pd.read_csv(csv_path)
        for old_name, new_name in merges.items():
            mask = df['source_name'] == old_name
            df.loc[mask, 'source_name'] = new_name
            print(f"Merged '{old_name}' -> '{new_name}'")
        
        df.to_csv(csv_path, index=False)
        print("\nCSV updated successfully.")
    else:
        print("\nNo merges were performed.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
    interactive_merge(CSV_PATH)
