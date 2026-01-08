import pandas as pd
import os

FILE_PATH = "tiktok_final_dataset.csv"

# Mapping of [old_name] -> [new_name]
MERGE_MAP = {
    "@askimfood1": "@askim_food",
    "@cote.doran": "@cote_oran",
    "@loversgrill94": "@lovers_grill",
    "@pontdehydra": "@pont_hydra",
    "@quick_bitedz": "@quick_bite",
    "@seven_time": "@seven.times",
    "@seven_times_luxury": "@seven.times.luxury",
    "@thaisty.dz": "@thaisty_dz",
    "@cintra_restaurant": "@cintra",
    "@santorino_restaurant": "@santorino",
    "@helea": "@helena"
}

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    print(f"Loaded {FILE_PATH} with {len(df)} rows.")

    updates_count = 0
    for old_name, new_name in MERGE_MAP.items():
        # Count how many rows will be changed
        mask = df['source_name'] == old_name
        affected = mask.sum()
        if affected > 0:
            df.loc[mask, 'source_name'] = new_name
            print(f"Merged '{old_name}' -> '{new_name}' ({affected} rows updated)")
            updates_count += affected

    if updates_count > 0:
        df.to_csv(FILE_PATH, index=False)
        print(f"\nSuccessfully updated {updates_count} rows in {FILE_PATH}.")
    else:
        print("No changes needed (names already merged or not found).")
else:
    print(f"Error: {FILE_PATH} not found.")
