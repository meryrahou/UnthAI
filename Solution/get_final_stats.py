import pandas as pd
import os

CSV_PATH = 'Solution/backend/data/FinalDataset.csv'

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    print("### 📊 Final Dataset Statistics")
    print(f"- **Total Comments**: {len(df)}")
    print(f"- **Unique Restaurants**: {df['source_name'].nunique()}")
    
    print("\n#### 🏠 Restaurant Breakdown")
    counts = df['source_name'].value_counts()
    for name, count in counts.items():
        print(f"- **{name}**: {count} comments")
        
    print("\n#### 📱 Platform Breakdown")
    p_counts = df['platform'].value_counts()
    for plat, count in p_counts.items():
        print(f"- **{plat}**: {count} comments")
        
    print("\n#### 📍 Missing Data (Nulls)")
    nulls = df.isnull().sum()
    for col, count in nulls.items():
        if count > 0:
            print(f"- **{col}**: {count} missing")
else:
    print(f"Error: {CSV_PATH} not found.")
