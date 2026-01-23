import pandas as pd
from difflib import SequenceMatcher
import re

def normalize(name):
    if not isinstance(name, str): return ""
    # Remove @, .dz, dz at end, restaurant, snack, food, fastfood
    s = name.lower()
    s = re.sub(r'[@\.]', ' ', s)
    s = re.sub(r'\bdz\b', '', s)
    s = re.sub(r'\brestaurant\b', '', s)
    s = re.sub(r'\bsnack\b', '', s)
    s = re.sub(r'\bfood\b', '', s)
    s = re.sub(r'\bfastfood\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def check_similar_names(csv_path):
    df = pd.read_csv(csv_path)
    # Get unique names and their original forms
    raw_names = [str(x) for x in df['source_name'].unique() if pd.notnull(x)]
    
    # Pre-normalize for speed
    normalized_map = {n: normalize(n) for n in raw_names}
    
    similar = []
    threshold = 0.75
    
    for i in range(len(raw_names)):
        for j in range(i + 1, len(raw_names)):
            n1, n2 = raw_names[i], raw_names[j]
            s1, s2 = normalized_map[n1], normalized_map[n2]
            
            if not s1 or not s2: continue
            
            # Check 1: Simple fuzzy match on normalized
            ratio = SequenceMatcher(None, s1, s2).ratio()
            
            # Check 2: Substring match (one contains the other)
            is_substring = (s1 in s2 or s2 in s1) and min(len(s1), len(s2)) > 4
            
            if ratio >= threshold or is_substring:
                # Don't match if it's just common words like "algeria"
                if len(s1) < 4 and not is_substring: continue
                
                # Heuristic: if we have '@name' and 'name', it's a strong match
                res_ratio = ratio if not is_substring else 1.0
                similar.append((n1, n2, res_ratio))
                
    # Sort by similarity ratio
    similar.sort(key=lambda x: x[2], reverse=True)
    
    print(f"{'Name 1':<45} | {'Name 2':<45} | {'Score'}")
    print("-" * 105)
    for n1, n2, r in similar[:60]:
        print(f"{n1[:45]:<45} | {n2[:45]:<45} | {r:.2f}")

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Assuming this script is in app/services/, we need to go up two levels to get to backend root
    # Current file: backend/app/services/detect_duplicates.py
    # Data: backend/data/
    CSV_PATH = os.path.join(BASE_DIR, "../../data/master_data.csv")
    check_similar_names(CSV_PATH)
