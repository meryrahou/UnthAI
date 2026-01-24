import pandas as pd
import os
import re

def clean_name(name):
    if not isinstance(name, str):
        return "Unknown"
    
    # Remove @
    name = name.replace('@', ' ')
    
    # Replace _ with space
    name = name.replace('_', ' ')
    
    # Remove extra spaces and newlines
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Title Case (handles random CAPS nicely)
    # But we should be careful with some words. 
    # Usually .title() works well for restaurant names.
    name = name.title()
    
    return name

def perform_cleanup(csv_path):
    print(f"Reading {csv_path} for name cleanup...")
    df = pd.read_csv(csv_path)
    
    df['source_name'] = df['source_name'].fillna("Unknown")
    
    old_unique = df['source_name'].nunique()
    
    print("Cleaning source_name column...")
    df['source_name'] = df['source_name'].apply(clean_name)
    
    new_unique = df['source_name'].nunique()
    
    print(f"Unique names reduced from {old_unique} to {new_unique}.")
    
    # Save back
    df.to_csv(csv_path, index=False)
    print(f"Successfully cleaned names and updated {csv_path}.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
    perform_cleanup(CSV_PATH)
