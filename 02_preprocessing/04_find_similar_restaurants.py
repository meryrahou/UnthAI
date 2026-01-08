import pandas as pd
from difflib import SequenceMatcher
import json

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_duplicates(file_path, threshold=0.8):
    df = pd.read_csv(file_path)
    unique_names = sorted(df['source_name'].astype(str).unique())
    
    suggestions = []
    seen = set()
    
    for i, name1 in enumerate(unique_names):
        for name2 in unique_names[i+1:]:
            score = similarity(name1, name2)
            if score >= threshold:
                # Check for common prefixes or suffixes that strongly suggest a match
                # e.g. "restaurant", "dz", "oran"
                suggestions.append({
                    "name1": name1,
                    "name2": name2,
                    "score": round(score, 3)
                })
    
    return suggestions

if __name__ == "__main__":
    file_path = "tiktok_final_dataset.csv"
    matches = find_duplicates(file_path)
    # Filter matches to avoid too many overlaps
    # Just print the top ones for user selection
    print(json.dumps(matches, indent=2))
