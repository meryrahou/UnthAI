import pandas as pd
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "../../data/FinalDataset.csv")
NAMES_JSON_PATH = os.path.join(BASE_DIR, "../../data/names.json")

def clean_name(name):
    if not isinstance(name, str): return name
    # Initial cleanup
    name = name.strip()
    # Remove @
    name = name.lstrip('@')
    # Replace separators with space
    name = re.sub(r'[.,;_]', ' ', name)
    # Remove "dz" at the end
    name = re.sub(r'\bdz\d*\b', '', name, flags=re.IGNORECASE)
    # Remove standalone numbers at the end
    name = re.sub(r'\s+\d+$', '', name)
    
    # Remove "Le " or "Les " at the beginning (case insensitive)
    name = re.sub(r'^(Le|Les)\s+', '', name, flags=re.IGNORECASE)
    
    # Remove "Restaurant " at the beginning or end (case insensitive)
    # and "Resturant" typo
    name = re.sub(r'^(Restaurant|Resturant)\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(Restaurant|Resturant)$', '', name, flags=re.IGNORECASE)
    
    # Standardize spaces and Title Case
    name = " ".join(name.split()).title()
    return name

def apply_custom_logic():
    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # 1. Apply generic cleaning first
    df['source_name'] = df['source_name'].apply(clean_name)
    
    # 2. Specific Manual Merges
    merges = {
        # Ambiance
        "Ambiancefood": "Ambiance Telemcen",
        # American
        "American Pizza": "American Burger",
        # Anas
        "Anes Food Maraval": "Anas Food",
        # Barbes
        "Barbes Food": "Barbes Food", # Likely already handled by Title Case
        # Check In
        "Check In 22": "Check In",
        "Check In22": "Check In",
        # Chill Food
        "Chill Food 23": "Chill Food",
        "Chill Food23": "Chill Food",
        # Meat Group
        "Meatlove": "Meat N Chill",
        "Meatnchill": "Meat N Chill",
        "Meet N Meet": "Meat N Chill",
        "Meatlove5": "Meat N Chill",
        # Snack Group
        "Snackcheesekou Ko": "Snacky Time",
        "Snacko Hm": "Snacky Time",
        "Snacky Time Kouba": "Snacky Time",
        # Hicham Cook
        "هشام كوك بيتزا": "Hicham Cook",
        "Hichem Cook Pizza": "Hicham Cook",
        "Hichamcookgrill": "Hicham Cook",
        "Hichem Cook": "Hicham Cook"
    }
    
    # Merge the bottom ~70 restaurants with low interaction volume
    # This covers all platforms (FB, IG, Tik, Maps)
    small_restaurants = [
        'Croustymood', 'Dadysburger', 'Finaboca', 'Glacito Douera', 'Gm Pizzaburger',
        'Hova Cafeteria', 'Kais Salonthe', 'Kebda Chef', 'Khdi J', 'Ladzz Algerie',
        'Latifa Oran', 'Le13Hotel3', 'Lord', 'Mishmish', 'New Land Food',
        'Obayra23', 'Petit Tunisien', 'Raouf Food', 'Unive', 'Wanderer',
        'Sandwitch Yabki', 'Victoria', 'Zeghlache Food', 'Abdouferrah23', 'Bou Ham Ham',
        'Boubousnack', 'Chicchic1997', 'Eclipses Coffee Restau', 'La Tranche', 'Lee Paradis Sur T',
        'Ofc', 'Poisson Or', 'Publideco', 'Rolls', 'Saliiiiiihofood', 'Savannah',
        'Tacomania35', 'Algerian Cuisine', 'Big Daddyfood', 'Bonga Food', 'Fastfood751',
        'La Perle Nana', 'Laterrassesidiyahia', 'Masagran', 'Ossy Anaba', 'Restaurantkingsenia',
        'So Chicken Oran', 'Three', 'Bingotlemcen', 'Braise Tacos5', 'Chikenhest',
        'Jnan L', 'La Graille6', 'La Villa Saint Tropez', 'Lets Taste It', 'Lion Oran',
        'Maraval Hotel', 'Mendousa', 'Mimoun Abdelillah', 'Minoufood1', 'Oussy House',
        'Pizzeria Med18', 'Raniabgs1', 'Redcap86', 'Steakhouse Oran', 'Wahrani',
        'Amineh351', 'Camion Rose Oran', 'Casamiacasa14', 'Chika Grill5',
        'La Napolitana', 'Caracoya'
    ]
    for res in small_restaurants:
        merges[res] = "Autros"
    
    # Apply manual merges
    df['source_name'] = df['source_name'].replace(merges)
    
    # Handle the Arabic to English merge manually just in case replace didn't catch it
    # and generic Hichem variations
    def final_refinement(name):
        # Arabic check
        if "هشام كوك" in name: return "Hicham Cook"
        # Hichem variations
        if "Hichem" in name and "Cook" in name: return "Hicham Cook"
        if name == "Hicham Cook Pizza": return "Hicham Cook"
        return name

    df['source_name'] = df['source_name'].apply(final_refinement)
    
    # 3. Final unique list and save
    unique_names = sorted(df['source_name'].unique())
    print(f"Final Count of Restaurants: {len(unique_names)}")
    
    df.to_csv(CSV_PATH, index=False)
    
    with open(NAMES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(unique_names, f, indent=4, ensure_ascii=False)
        
    print("Dataset and names.json updated successfully.")

if __name__ == "__main__":
    apply_custom_logic()
