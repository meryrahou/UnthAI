import pandas as pd
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
NAMES_JSON_PATH = os.path.join(BASE_DIR, "../../data/names.json")

def simplify_name(name):
    if not isinstance(name, str):
        return name
    
    # 1. Basic cleanup: remove . , ; and special chars at start/end
    # Also remove common suffixes like 'dz', 'oran', 'alger', numbers at the end
    orig_name = name
    
    # Remove leading @
    name = name.lstrip('@')
    
    # Replace . , ; _ with space
    name = re.sub(r'[.,;_]', ' ', name)
    
    # Remove "dz" or "dz13" or "dz31" at the end (case insensitive)
    # We look for dz followed by potential numbers or just dz at the end of a word
    name = re.sub(r'\bdz\d*\b', '', name, flags=re.IGNORECASE)
    
    # Remove standalone numbers at the end
    name = re.sub(r'\s+\d+$', '', name)
    
    # Remove trailing/leading spaces
    name = name.strip()
    
    # Fix random caps: if it's all caps or very messy, Title Case it.
    # Actually, Title Case is usually safest for restaurant names.
    name = name.title()
    
    # Remove extra spaces inside
    name = " ".join(name.split())
    
    return name

def update_dataset_names():
    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Keep track of unique names for the JSON
    unique_names = sorted(df['source_name'].unique())
    print(f"Found {len(unique_names)} unique names before cleanup.")
    
    # Apply simplification
    df['source_name'] = df['source_name'].apply(simplify_name)
    
    new_unique_names = sorted(df['source_name'].unique())
    print(f"Found {len(new_unique_names)} unique names after cleanup.")
    
    # Save dataset
    df.to_csv(CSV_PATH, index=False)
    print("Dataset updated.")
    
    # Save JSON for the login dropdown
    with open(NAMES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_unique_names, f, indent=4, ensure_ascii=False)
    print(f"JSON names file updated at {NAMES_JSON_PATH}")

if __name__ == "__main__":
    update_dataset_names()
