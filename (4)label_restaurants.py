import pandas as pd
import os
import webbrowser

FILE_PATH = "tiktok_final_dataset.csv"

def label_restaurants():
    if not os.path.exists(FILE_PATH):
        print(f"Error: {FILE_PATH} not found.")
        return

    df = pd.read_csv(FILE_PATH)
    
    # We group by video_url to label all comments from the same video at once
    unique_videos = df[['video_url', 'source_name']].drop_duplicates().values.tolist()
    total_videos = len(unique_videos)
    
    print(f"--- Restaurant Labeling Tool ---")
    print(f"Found {total_videos} unique videos to verify.")
    print(f"Instructions:")
    print(f"1. A video will open in your browser.")
    print(f"2. Enter the real name of the restaurant.")
    print(f"3. Press Enter to keep the current name: {unique_videos[0][1] if unique_videos else 'N/A'}")
    print(f"4. Type 'quit' to save and exit.\n")

    for i, (url, current_name) in enumerate(unique_videos):
        print(f"[{i+1}/{total_videos}] Current: {current_name}")
        print(f"URL: {url}")
        
        # Open in browser
        webbrowser.open(url)
        
        new_name = input("Enter new name (or Enter to skip, 'quit' to stop): ").strip()
        
        if new_name.lower() == 'quit':
            print("Exiting and saving...")
            break
        
        if new_name:
            # Format as @name if user didn't include it, or keep as is? 
            # User said: "replace source_name by @{input}"
            if not new_name.startswith('@'):
                new_name = f"@{new_name}"
            
            # Update all rows with this video_url
            df.loc[df['video_url'] == url, 'source_name'] = new_name
            print(f"   Updated to: {new_name}")
            
            # Optional: Intermediate save to prevent data loss
            df.to_csv(FILE_PATH, index=False)
        else:
            print("   Keeping original.")

    # Final save
    df.to_csv(FILE_PATH, index=False)
    print(f"\nProgress saved to {FILE_PATH}. Total videos processed: {i if new_name.lower() == 'quit' else total_videos}")

if __name__ == "__main__":
    label_restaurants()
