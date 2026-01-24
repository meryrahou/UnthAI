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

from app.services.model_service import get_model_service

def refresh_restaurant_data(restaurant_name):
    print(f"Refreshing data for: {restaurant_name}")
    try:
        # Load Model Service (Lazy loads on first call)
        model_service = get_model_service()
        
        df = pd.read_csv(CSV_PATH)
        df = df.fillna("")
        
        # Filter for this specific restaurant (Case insensitive)
        df_res = df[df['source_name'].str.lower() == restaurant_name.lower()].copy()
        
        if df_res.empty:
            print(f"Warning: No data found for {restaurant_name}")
            return False

        # --- STRICT CLEAN SLATE ---
        # Explicitly drop the columns the model is supposed to predict.
        # This ensures we are NOT using any old labels from the CSV.
        categories = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
        cols_to_drop = categories + ['out_of_scope', 'feeling', 'model_prediction']
        df_res = df_res.drop(columns=[c for c in cols_to_drop if c in df_res.columns])
        
        # Batch Predict all comments using the BERT model
        comments = df_res['comment_text'].tolist()
        # Clean text: Remove trailing [COMPLAINT], [INQUIRY], etc tags that might confuse the model
        import re
        clean_comments = [re.sub(r'\s*\[(COMPLAINT|INQUIRY|APPRECIATION|RECOMMENDATION|OUT_OF_SCOPE)\]\s*$', '', str(c), flags=re.IGNORECASE) for c in comments]
        
        print(f"--- 🧠 Running Model Inference on {len(comments)} comments ---")
        all_preds = model_service.predict_batch(clean_comments, threshold=0.5)
        
        # Prepare processed columns
        feelings = []
        platform_labels = []
        cat_data = {cat: [] for cat in categories}
        out_of_scope_list = []
        
        for preds in all_preds:
            # 1. Calculate overall feeling
            feelings.append(model_service.get_feeling(preds))
            
            # 2. Map labels to platform format for storage
            platform_labels.append(json.dumps(model_service.map_to_platform_labels(preds)))
            
            # 3. Determine out of scope status
            is_out_of_scope = any('out_of_scope' in p for p in preds)
            out_of_scope_list.append(is_out_of_scope)
            
            # 4. Fill individual category columns (for dashboard summary logic)
            # This ensures compatibility with existing main.py logic
            row_cats = {cat: "" for cat in categories}
            for p in preds:
                for cat in categories:
                    if p.startswith(f"{cat}_"):
                        if "_positive" in p: 
                            row_cats[cat] = "appreciation"
                        elif "_negative" in p: 
                            row_cats[cat] = "complaint"
                        # We can add inquiry/recommendation if the model supported them specifically
                        # For now, BERT maps most to appreciation/complaint/neutral
            
            for cat in categories:
                cat_data[cat].append(row_cats[cat])

        # Apply processed data back to dataframe
        df_res['feeling'] = feelings
        df_res['model_prediction'] = platform_labels
        df_res['out_of_scope'] = out_of_scope_list
        for cat in categories:
            df_res[cat] = cat_data[cat]
        
        output_path = get_processed_path(restaurant_name)
        df_res.to_csv(output_path, index=False)
        print(f"Success: Processed {len(df_res)} rows with BERT model. Saved to {output_path}")
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
