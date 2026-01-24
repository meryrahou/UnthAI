import torch
import pandas as pd
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Paths
MODEL_PATH = "model/best_dziribert_sentimentversion2.pth"
DATA_PATH = "data/FinalDataset.csv"
MODEL_NAME = "alger-ia/dziribert"

# Label columns as defined in the training script (20 labels total)
label_columns = [
    'food_positive', 'food_negative', 'food_neutral',
    'service_positive', 'service_negative', 'service_neutral',
    'place_positive', 'place_negative', 'place_neutral',
    'price_positive', 'price_negative', 'price_neutral',
    'delivery_positive', 'delivery_negative', 'delivery_neutral',
    'treatment_positive', 'treatment_negative', 'treatment_neutral',
    'out_of_scope_positive', 'out_of_scope_negative'
]

def analyze_comments():
    print("--- 🚀 Loading Model & Data ---")
    
    # Check device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Load Tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        return

    # Load Model Structure
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, 
            num_labels=len(label_columns),
            problem_type="multi_label_classification"
        )
        
        # Load State Dict
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Fetch 5 random comments
    try:
        df = pd.read_csv(DATA_PATH)
        sample_comments = df['comment_text'].dropna().sample(5).tolist()
        print(f"Retrieved {len(sample_comments)} comments.")
    except Exception as e:
        print(f"Error reading dataset: {e}")
        return

    # Prediction Logic
    print("\n--- 🧠 Running Inference ---")
    start_time = time.time()

    encoding = tokenizer(
        sample_comments,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors='pt'
    ).to(device)

    with torch.no_grad():
        outputs = model(input_ids=encoding['input_ids'], attention_mask=encoding['attention_mask'])
        probs = torch.sigmoid(outputs.logits)
        preds = (probs >= 0.5).int().cpu().numpy()

    end_time = time.time()
    total_time = end_time - start_time

    # Display Results
    print(f"\nInference Time for 5 comments: {total_time:.4f} seconds")
    print(f"Avg time per comment: {total_time/5:.4f} seconds")
    
    print("\n--- 📝 Results ---")
    for i, comment in enumerate(sample_comments):
        print(f"\nComment: {comment}")
        predicted_labels = [label_columns[j] for j, val in enumerate(preds[i]) if val == 1]
        
        if not predicted_labels:
            print("Prediction: [Neutral / No Specific Aspect]")
        else:
            print(f"Prediction: {', '.join(predicted_labels)}")

if __name__ == "__main__":
    analyze_comments()
