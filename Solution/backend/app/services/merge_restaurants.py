import pandas as pd

def merge_restaurant_names(csv_path):
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Mapping table for merging based on user request
    merges = {
        # Group: Casbah
        "Casbah Istanbul القصبة اسطنبول": "Casbah Istanbul",
        "قصبة اسطنبول": "Casbah Istanbul",
        
        # Group: American Burger
        "American Burger Factory": "American Burger",
        "American Burger said hamdine": "American Burger",
        
        # Group: Sultan
        "@sultan_corniche": "@sultan",
        "Sultan Restaurants": "@sultan",
        
        # Group: Brother TS
        "brother.ts": "@brother.tselbiar",
        
        # Group: Budz
        "budz.dz": "@budz",
        
        # Group: Cezam
        "restaurant.cezam": "@cezam",
        
        # Group: Diyarbakir
        "diyarbakir_restaurant_": "@diyarbakir",
        
        # Group: Kartaj
        "@kartaj_oran": "@kartaj",
        
        # Group: Mega Pizza
        "@mega_pizza_annaba": "@mega_pizza",
        "mega_pizza_elbiar": "@mega_pizza",
        
        # Group: My Pizza
        "@my_pizza_oran": "@my_pizza",
        
        # Group: Seven Times
        "@seven.times.luxury": "@seven.times",
        
        # Group: Sinai
        "sinai.dz": "@sinai",
        
        # Group: El Marssem
        "elmarssem.dz": "@el_marssem",
        
        # Group: Casa Bella
        "@casabelladraria": "Restaurant Casa Bella - Draria",
        
        # Group: Others from List 1
        "@restaurant_mani": "@restaurant_marisco",
        "@restaurant_wahrani": "@restaurant_marisco",
        "@taylot": "@taylor",
        "@le_carre_restaurant": "@oscar_restaurant",
        "@leonard_restauran": "@oscar_restaurant",
        "@restaurant.el.rit": "@restaurant.primo",
        "@le_petit_chalet": "Le Petit Chalet",
        "lepetitchaletoran": "Le Petit Chalet",
        "@triple_": "Triple R Restaurant",
        "triple.r.restaurant": "Triple R Restaurant",
        "@le.rooftop.annaba": "Le Rooftop Annaba",
        "@roofttop_anaba": "Le Rooftop Annaba"
    }
    
    # Special case from User List 1: @mega_pizza | @my_pizza
    # Since they are in the same list but also in List 2, I will follow the user's specific request
    # even if they seem different.
    merges["@mega_pizza"] = "@my_pizza" 
    
    count = 0
    for old_name, new_name in merges.items():
        mask = df['source_name'] == old_name
        if mask.any():
            rows_affected = mask.sum()
            df.loc[mask, 'source_name'] = new_name
            print(f"Merged '{old_name}' -> '{new_name}' ({rows_affected} rows)")
            count += 1
            
    if count > 0:
        df.to_csv(csv_path, index=False)
        print(f"\nDone! Successfully merged {count} restaurant name variations.")
        print(f"Post IDs and Comment IDs remain untouched and unique.")
    else:
        print("No matches found for merging.")

if __name__ == "__main__":
    CSV_PATH = "/Users/mery/GitHub/UnthAI/Solution/backend/data/master_data.csv"
    merge_restaurant_names(CSV_PATH)
