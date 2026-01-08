import pandas as pd
import emoji
from collections import Counter
import os

INPUT_FILE = "dataset.csv"
OUTPUT_FILE = "emoji_frequencies.csv"

def extract_emojis():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    # Ensure we only process strings
    comments = df['comment_text'].dropna().astype(str)
    
    print("Extracting emojis from comments...")
    all_emojis = []
    
    for comment in comments:
        # Extract all emojis from the string
        found = emoji.emoji_list(comment)
        all_emojis.extend([e['emoji'] for e in found])
    
    # Count frequencies
    counts = Counter(all_emojis)
    
    # Create a DataFrame for results
    results_df = pd.DataFrame(counts.items(), columns=['emoji', 'count'])
    results_df = results_df.sort_values(by='count', ascending=False).reset_index(drop=True)
    
    # Add descriptions using emoji library
    results_df['description'] = results_df['emoji'].apply(lambda x: emoji.demojize(x).strip(':'))
    
    # Save to CSV
    results_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\nExtraction complete! Found {len(counts)} unique emojis.")
    print(f"Top 15 Emojis:")
    print(results_df.head(15).to_string(index=False))
    print(f"\nFull list saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_emojis()
