import pandas as pd

#   Chemin vers ton fichier CSV original
input_csv = "annotation_part_1.csv"
#   Chemin du fichier final transformé
output_csv = "annotation_part_1_multilabel.csv"

#   Colonnes des topics
topics = ["food", "service", "place", "delivery", "price", "treatment"]
#   Intent possibles pour chaque topic
intents = ["appreciation", "complaint", "recommendation", "inquiry"]

#   Lire le CSV
df = pd.read_csv(input_csv)

#   Remplacer les NaN par "none" pour simplifier
df[topics] = df[topics].fillna("none")

#   Créer les colonnes binaires pour chaque topic_intent
for topic in topics:
    for intent in intents:
        col_name = f"{topic}_{intent}"
        df[col_name] = df[topic].apply(lambda x: 1 if intent in str(x).split(",") else 0)

#   Convertir out_of_scope en binaire : False → 0, True → 1
df["out_of_scope"] = df["out_of_scope"].apply(lambda x: 1 if x else 0)

#   Colonnes originales à garder
original_cols = ["final_id", "comment_text", "comment_id", "platform", "source_name", "date", "likesCount"]
#   Colonnes multi-label
multilabel_cols = [f"{t}_{i}" for t in topics for i in intents] + ["out_of_scope"]

#   Combiner les colonnes originales + nouvelles colonnes multi-label
df_final = df[original_cols + multilabel_cols]

#   Sauvegarder le CSV transformé
df_final.to_csv(output_csv, index=False)

print(f"✅ Dataset transformé enregistré dans : {output_csv}")
