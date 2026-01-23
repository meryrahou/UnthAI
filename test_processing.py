
import sys
import os
import pandas as pd

# Add app to path
sys.path.append(os.path.abspath("Solution/backend"))

from app.services.data_manager import refresh_restaurant_data, get_processed_path

def test_processing(name):
    print(f"Testing for: {name}")
    success = refresh_restaurant_data(name)
    print(f"Refresh success: {success}")
    
    if success:
        path = get_processed_path(name)
        print(f"Processed path: {path}")
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"Row count: {len(df)}")
            if not df.empty:
                print("Columns:", df.columns.tolist())
                print("Sample Date:", df['date'].iloc[0] if 'date' in df.columns else "No date col")
                
                # Check date parsing
                df['date_dt'] = pd.to_datetime(df['date'], format='mixed', utc=True, errors='coerce')
                valid_dates = df['date_dt'].dropna()
                print(f"Valid dates count: {len(valid_dates)}")
                if len(valid_dates) == 0:
                    print("ERROR: No valid dates parsed!")
            else:
                print("ERROR: Dataframe empty after read")
        else:
            print("ERROR: File does not exist after success return")

if __name__ == "__main__":
    test_processing("@quick_bite")
