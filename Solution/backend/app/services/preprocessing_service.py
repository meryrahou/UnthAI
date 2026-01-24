import pandas as pd
import json
import os
import re
import hashlib
import sys

# Add current directory to path for local imports
sys.path.append(os.getcwd())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEST_DATASET_PATH = os.path.join(DATA_DIR, "TestDataset.csv")
# Crucial: FinalDataset.csv is the actual file the app reads
FINAL_DATASET_PATH = os.path.join(DATA_DIR, "FinalDataset.csv")

def generate_final_id(row):
    """Generates a unique ID based on comment content and metadata if final_id is missing."""
    seed = f"{row.get('comment_id', '')}{row.get('comment_text', '')}{row.get('date', '')}"
    return hashlib.md5(seed.encode()).hexdigest()[:10]

def generate_post_id(url):
    """Generates a very safe integer-based post ID from the URL."""
    if not url or pd.isna(url):
        return 0
    # Use MD5 and take first 6 hex chars (Max value 16,777,215)
    return int(hashlib.md5(str(url).encode()).hexdigest()[:6], 16)

def preprocess_new_data(input_csv_path, restaurant_override=None):
    """
    Standardizes new scraped data, cleans it, and prepares it for the pipeline.
    DOES NOT run model inference (this happens at login/refresh).
    Saves to TestDataset.csv and replaces FinalDataset.csv.
    """
    print(f"--- 🚀 Starting Preprocessing Pipeline (No Model) for {input_csv_path} ---")
    
    if not os.path.exists(input_csv_path):
        print(f"❌ Error: Input file {input_csv_path} not found.")
        return False

    try:
        df = pd.read_csv(input_csv_path)
        print(f"📈 Loaded {len(df)} rows.")

        # 1. Standardize Columns (Mapping Raw Scraper to System Schema)
        column_mapping = {
            'video_id': 'post_id',
            'video_url': 'post_url',
            'source_name': 'user_name',  # Scraper source_name is often the user
            'restaurant': 'source_name', # Scraper restaurant is our system source_name
            'likesCount': 'likesCount'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Ensure essential columns exist
        essential_columns = ['comment_id', 'comment_text', 'platform', 'source_name', 'date']
        for col in essential_columns:
            if col not in df.columns:
                if col == 'source_name' and restaurant_override:
                    df[col] = restaurant_override
                elif col == 'platform':
                    df[col] = "tiktok" # Default for this scraper flow
                else:
                    df[col] = ""
        
        if restaurant_override:
            df['source_name'] = restaurant_override

        # 2. Cleanup & Deduplication
        if 'comment_id' in df.columns:
            initial_count = len(df)
            df = df.drop_duplicates(subset=['comment_id'])
            print(f"Deduplicated: {initial_count} -> {len(df)} rows.")
            
        df['comment_text'] = df['comment_text'].fillna("").astype(str)
        
        # Clean tags if any (Removing [COMPLAINT] style tags from scraper)
        df['comment_text'] = df['comment_text'].apply(
            lambda x: re.sub(r'\s*\[(COMPLAINT|INQUIRY|APPRECIATION|RECOMMENDATION|OUT_OF_SCOPE)\]\s*$', '', x, flags=re.IGNORECASE)
        )


        # 3. ID Generation (Safe Post IDs & unique Final IDs)
        # Regenerate post_id from post_url to avoid big integer issues in JS
        if 'post_url' in df.columns:
            print("Regenerating safe post_ids from URLs...")
            df['post_id'] = df['post_url'].apply(generate_post_id)
        elif 'post_id' in df.columns:
            # Fallback: take last 9 digits of the big integer to keep it safe for JS
            df['post_id'] = df['post_id'].apply(lambda x: int(str(x)[-9:]) if str(x).isdigit() else 0)

        if 'final_id' not in df.columns:
            df['final_id'] = df.apply(generate_final_id, axis=1)

        # 5. Save to TestDataset.csv
        df.to_csv(TEST_DATASET_PATH, index=False)
        print(f"✅ Preprocessed data (Cleaned & Schema-ready) saved to {TEST_DATASET_PATH}")

        # 6. Replace FinalDataset.csv
        import shutil
        shutil.copy2(TEST_DATASET_PATH, FINAL_DATASET_PATH)
        print(f"🚀 pipeline update: FinalDataset.csv has been REPLACED by the new preprocessed data.")
        print(f"📊 Total records ready for model: {len(df)}")
        
        return True

    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    # Example usage: python app/services/preprocessing_service.py data/new_american_burger_data.csv "American Burger"
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        restaurant = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.isabs(input_path):
            potential_path = os.path.join(os.getcwd(), input_path)
            if os.path.exists(potential_path):
                input_path = potential_path

        preprocess_new_data(input_path, restaurant)
    else:
        print("Usage: python preprocessing_service.py <input_csv_path> [restaurant_name]")
