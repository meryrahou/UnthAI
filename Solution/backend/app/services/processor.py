import pandas as pd
import json

def process_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df = df.fillna("")
        
        target_res = "Restaurant San Benito"
        df_res = df[df['source_name'] == target_res].copy()
        
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
            
            # Apps and Recs are positive factors
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
        
        return df_res
    except Exception as e:
        print(f"Error in processing: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    CSV_PATH = "/Users/mery/GitHub/UnthAI/03_annotation/annotation_part_1.csv"
    processed = process_data(CSV_PATH)
    processed.to_csv("/Users/mery/GitHub/UnthAI/Solution/backend/processed_san_benito.csv", index=False)
    print("Processed file created at Solution/backend/processed_san_benito.csv")
