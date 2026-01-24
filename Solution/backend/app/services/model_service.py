import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List
import os
import json

class ModelService:
    def __init__(self, model_root: str = None):
        if model_root is None:
            # Default to backend root
            # This file is backend/app/services/model_service.py
            # So going up 3 levels to reach backend/
            self_dir = os.path.dirname(os.path.abspath(__file__))
            model_root = os.path.dirname(os.path.dirname(self_dir))
        
        self.model_path = os.path.join(model_root, "model/best_dziribert_sentimentversion2.pth")
        self.model_name = "alger-ia/dziribert"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.label_columns = [
            'food_positive', 'food_negative', 'food_neutral',
            'service_positive', 'service_negative', 'service_neutral',
            'place_positive', 'place_negative', 'place_neutral',
            'price_positive', 'price_negative', 'price_neutral',
            'delivery_positive', 'delivery_negative', 'delivery_neutral',
            'treatment_positive', 'treatment_negative', 'treatment_neutral',
            'out_of_scope_positive', 'out_of_scope_negative'
        ]
        
        print(f"--- 🚀 Initializing Model Service on {self.device} ---")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, 
                num_labels=len(self.label_columns),
                problem_type="multi_label_classification"
            )
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            print("✅ Model Service ready.")
        except Exception as e:
            print(f"❌ Error initializing Model Service: {e}")
            raise e

    def predict_batch(self, comments: List[str], threshold: float = 0.6) -> List[List[str]]:
        if not comments:
            return []
        
        valid_comments = [str(c) if c and str(c).strip() else "" for c in comments]
        
        encoding = self.tokenizer(
            valid_comments,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors='pt'
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=encoding['input_ids'], attention_mask=encoding['attention_mask'])
            probs = torch.sigmoid(outputs.logits)
            preds = (probs >= threshold).int().cpu().numpy()

        results = []
        for i in range(len(valid_comments)):
            if not valid_comments[i]:
                results.append([])
                continue
            
            predicted_labels = [self.label_columns[j] for j, val in enumerate(preds[i]) if val == 1]
            results.append(predicted_labels)
        
        return results

    def get_feeling(self, labels: List[str]) -> str:
        pos_count = sum(1 for label in labels if '_positive' in label)
        neg_count = sum(1 for label in labels if '_negative' in label)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def map_to_platform_labels(self, labels: List[str]) -> List[str]:
        """Maps BERT labels to platform specific labels like 'food_appreciation'"""
        mapped = []
        for label in labels:
            if '_positive' in label:
                mapped.append(label.replace('_positive', '_appreciation'))
            elif '_negative' in label:
                mapped.append(label.replace('_negative', '_complaint'))
            # We skip neutral labels for the final display tags unless needed
        return mapped

# Global instance for app-wide use
_model_service = None

def get_model_service():
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service
