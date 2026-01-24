import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")

def refine_autros_demo():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    print("--- �️  Refining 'Autros' Showcase Data ---")
    df = pd.read_csv(CSV_PATH).fillna('')
    
    # 1. DEFINE TOP PROTECTED (DO NOT TOUCH)
    top_protected = [
        'American Burger', 'San Benito', 'Hicham Cook', 'Casbah Istanbul', 
        'Dzforestrestaurants', 'Casa Bella - Draria', 'À Petit Feu', 'Street2261', 
        'Pont Hydra', 'Sinai', 'Kfc', 'Lemanrais', 'Maestro', 
        'Helena', 'Cote Oran', 'تاج محل بن عكنون', 'Seven Times La Villa', 
        'Le216', 'Lagegarestaurant'
    ]
    
    # Reset existing Autros to start fresh with a balanced set (optional, but cleaner)
    # df.loc[df['source_name'] == 'Autros', 'source_name'] = 'Old_Autros_Data'
    
    # 2. SELECT BALANCED SAMPLES FROM ELIGIBLE LIST
    # We target ~6 posts per platform from non-top restaurants.
    
    selected_merges = {
        'tiktok': [
            'Mardoum', 'Bladi Oran', 'Labelladalger16', 
            'Maison Sardoudi', 'Madala', 'Budz'
        ],
        'instagram': [
            'Brother Tselbiar', 'Amine La Cantine', 'Mimas Donuts', 
            'The Bakery', 'Mahroussaglace', 'Teyr Ellil'
        ],
        'Facebook': [
            'Unknown', 'Tassili', 'Restaurantabarkannaba', 
            'Terre Et Mer Annaba', 'Naps Oran', 'Budz' # Budz is on both tik/fb
        ],
        'Google Maps': [
            'Laurel', 'L’Alchimiste Pâtisserie', 'Taylor', 
            'Babor alger', 'Le Majestic', 'Woodgrill'
        ]
    }
    
    # Flatten the list
    all_to_merge = []
    for platform in selected_merges:
        all_to_merge.extend(selected_merges[platform])
    
    # Remove duplicates
    all_to_merge = list(set(all_to_merge))
    
    # Ensure we aren't merging protected ones by accident
    all_to_merge = [r for r in all_to_merge if r not in top_protected]

    print(f"Merging {len(all_to_merge)} restaurants into 'Autros'.")
    
    # Update source_name
    mask = df['source_name'].isin(all_to_merge)
    df.loc[mask, 'source_name'] = 'Autros'

    # 3. PRUNE TO BALANCED POST COUNT
    # Aiming for ~13-14 total posts for maximum snappiness
    autros_df = df[df['source_name'] == 'Autros'].copy()
    
    # Get stats per post
    post_stats = autros_df.groupby(['platform', 'post_id']).size().reset_index(name='count')
    
    limits = {
        'tiktok': 4,        # Up to 4
        'instagram': 4,     # Up to 4
        'Facebook': 4,      # Up to 4
        'Google Maps': 2    # Keep 2
    }
    
    posts_to_keep = []
    for platform, limit in limits.items():
        # User requested "ones with less comments" for FB/TikTok (and likely others for balance)
        # We sort by count ASCENDING to get the smallest ones first.
        # But we don't want "1 comment" posts, so let's filter for meaningful data (>15 comments)
        
        platform_posts = post_stats[
            (post_stats['platform'] == platform) & 
            (post_stats['count'] > 15)
        ].sort_values('count', ascending=True)
        
        selected_posts = platform_posts.head(limit)
        posts_to_keep.extend(selected_posts['post_id'].tolist())
    
    # Final filter: Only rows that are Protected OR are in our hyper-lean Autros list
    mask_to_keep = (df['source_name'].isin(top_protected)) | (df['post_id'].isin(posts_to_keep))
    df = df[mask_to_keep]

    # 4. SAVE THE DATASET
    df.to_csv(CSV_PATH, index=False)
    
    # 5. VERIFY RESULTS
    autros_df = df[df['source_name'] == 'Autros']
    print("\n--- ✅ DEMO ACCOUNT 'AUTROS' LIGHT READY ---")
    print(f"Total Comments: {len(autros_df)}")
    print(f"Total Posts: {autros_df['post_id'].nunique()}")
    print("\nPlatform Balance:")
    print(autros_df.groupby('platform').agg({'post_id': 'nunique', 'comment_id': 'count'}))
    print("\n'Autros' is now lean, mean, and perfectly suited for a lighting-fast demo!")

if __name__ == "__main__":
    refine_autros_demo()
