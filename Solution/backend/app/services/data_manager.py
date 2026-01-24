import pandas as pd
import json
import os
import sys

# Master File Path
# Master File Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up 2 levels: services -> app -> backend, then into data
CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
DATA_DIR = os.path.join(BASE_DIR, "../../data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_processed_path(restaurant_name):
    # Sanitize filename
    safe_name = "".join([c if c.isalnum() else "_" for c in restaurant_name]).lower()
    return os.path.join(DATA_DIR, f"processed_{safe_name}.csv")

def refresh_restaurant_data(restaurant_name):
    print(f"Refreshing data for: {restaurant_name}")
    try:
        df = pd.read_csv(CSV_PATH)
        df = df.fillna("")
        
        # Filter for this specific restaurant (Case insensitive)
        df_res = df[df['source_name'].str.lower() == restaurant_name.lower()].copy()
        
        if df_res.empty:
            print(f"Warning: No data found for {restaurant_name}")
            return False

        categories = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
        
        def get_model_prediction(row):
            predictions = []
            for cat in categories:
                val = str(row[cat]).lower()
                if val == 'appreciation':
                    predictions.append(f"{cat}_appreciation")
                elif val == 'complaint':
                    predictions.append(f"{cat}_complaint")
                elif val == 'inquiry':
                    predictions.append(f"{cat}_inquiry")
                elif val == 'recommendation':
                    predictions.append(f"{cat}_recommendation")
            return predictions

        def get_feeling(row):
            if str(row['out_of_scope']).lower() == 'true':
                return "neutral"
            
            p = get_model_prediction(row)
            apps = [x for x in p if 'appreciation' in x]
            recs = [x for x in p if 'recommendation' in x]
            comps = [x for x in p if 'complaint' in x]
            
            pos_factors = len(apps) + len(recs)
            neg_factors = len(comps)
            
            if pos_factors > neg_factors:
                return "positive"
            elif neg_factors > pos_factors:
                return "negative"
            else:
                return "neutral"

        df_res['model_prediction'] = df_res.apply(lambda r: json.dumps(get_model_prediction(r)), axis=1)
        df_res['feeling'] = df_res.apply(get_feeling, axis=1)
        
        output_path = get_processed_path(restaurant_name)
        df_res.to_csv(output_path, index=False)
        print(f"Success: Processed {len(df_res)} rows. Saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error in processing {restaurant_name}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = " ".join(sys.argv[1:])
        refresh_restaurant_data(name)
    else:
        print("Please provide a restaurant name.")
