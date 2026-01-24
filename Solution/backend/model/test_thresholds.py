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

def test_thresholds():
    print("--- 🚀 Loading Model & Data ---")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Load Tokenizer and Model
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, 
            num_labels=len(label_columns),
            problem_type="multi_label_classification"
        )
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # Fetch 5 comments
    try:
        df = pd.read_csv(DATA_PATH)
        sample_comments = df['comment_text'].dropna().sample(5, random_state=42).tolist()
        print(f"✅ Retrieved {len(sample_comments)} comments.\n")
    except Exception as e:
        print(f"❌ Error reading dataset: {e}")
        return

    # Tokenize
    encoding = tokenizer(
        sample_comments,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors='pt'
    ).to(device)

    # Get raw probabilities
    with torch.no_grad():
        outputs = model(input_ids=encoding['input_ids'], attention_mask=encoding['attention_mask'])
        probs = torch.sigmoid(outputs.logits).cpu().numpy()

    # Test different thresholds
    thresholds = [0.5, 0.6, 0.7, 0.8]
    
    print("=" * 100)
    print("THRESHOLD COMPARISON")
    print("=" * 100)
    
    for comment_idx, comment in enumerate(sample_comments):
        print(f"\n📝 Comment {comment_idx+1}: {comment[:80]}...")
        print("-" * 100)
        
        for threshold in thresholds:
            preds = (probs[comment_idx] >= threshold).astype(int)
            predicted_labels = [label_columns[j] for j, val in enumerate(preds) if val == 1]
            
            if not predicted_labels:
                print(f"  Threshold {threshold}: [No predictions]")
            else:
                print(f"  Threshold {threshold}: {', '.join(predicted_labels[:5])}{' ...' if len(predicted_labels) > 5 else ''} ({len(predicted_labels)} total)")
        
        # Also show top 3 by confidence
        top_3_indices = probs[comment_idx].argsort()[-3:][::-1]
        top_3_labels = [(label_columns[i], f"{probs[comment_idx][i]:.3f}") for i in top_3_indices]
        print(f"  🏆 Top 3 by confidence: {', '.join([f'{l} ({p})' for l, p in top_3_labels])}")

    print("\n" + "=" * 100)
    print("💡 RECOMMENDATION:")
    print("=" * 100)
    print("Based on the results above:")
    print("  • Threshold 0.5 = Too many predictions (over-sensitive)")
    print("  • Threshold 0.7 = Balanced (recommended for production)")
    print("  • Threshold 0.8 = Very conservative (may miss some signals)")
    print("  • Alternative: Use Top-3 approach (always pick 3 highest confidence)")

if __name__ == "__main__":
    test_thresholds()
