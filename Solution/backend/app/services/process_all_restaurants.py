import pandas as pd
import os
from data_manager import refresh_restaurant_data, CSV_PATH

def process_all():
    print(f"Loading master dataset from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    unique_restaurants = df['source_name'].unique()
    
    print(f"Found {len(unique_restaurants)} unique restaurants. Starting processing...")
    
    success_count = 0
    fail_count = 0
    
    for name in unique_restaurants:
        if pd.isna(name) or str(name).strip() == "":
            continue
            
        print(f"Processing: {name}")
        success = refresh_restaurant_data(name)
        if success:
            success_count += 1
        else:
            fail_count += 1
            
    print(f"\nProcessing Complete!")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    process_all()
