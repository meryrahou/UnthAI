import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict
import os
import json
import re

class DziriBERT_ABSA(nn.Module):
    """
    Custom architecture for multi-topic multi-intent classification.
    Matches the DziribertABSA implementation in sic_multihead.ipynb exactly.
    """
    def __init__(self, model_name, num_topics, num_intents):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        hidden_size = self.bert.config.hidden_size

        # One head per topic
        self.topic_classifiers = nn.ModuleList([
            nn.Linear(hidden_size, num_intents) for _ in range(num_topics)
        ])

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # ⚠️ CRITICAL: Must use the direct [CLS] token (last_hidden_state[:, 0]) 
        # NOT pooler_output, to match notebook training logic.
        pooled = outputs.last_hidden_state[:, 0]

        # Logits per topic
        topic_logits = []
        for classifier in self.topic_classifiers:
            topic_logits.append(classifier(pooled))  # (batch, num_intents)

        logits = torch.stack(topic_logits, dim=1)  # (batch, num_topics, num_intents)
        return {"logits": logits}

class ModelService:
    def __init__(self, model_root: str = None):
        if model_root is None:
            self_dir = os.path.dirname(os.path.abspath(__file__))
            model_root = os.path.dirname(os.path.dirname(self_dir))
        
        self.model_path = os.path.join(model_root, "model/dziribert_absa-2.pt")
        self.model_name = "alger-ia/dziribert"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Exact order from sic_multihead.ipynb
        self.TOPICS = ["food", "service", "place", "delivery", "price", "treatment"]
        # Exact mapping from sic_multihead.ipynb
        self.ID2INTENT = {
            0: "appreciation",
            1: "complaint",
            2: "inquiry",
            3: "recommendation",
            4: "none"
        }
        self.INTENTS = list(self.ID2INTENT.values())
        
        print(f"--- 🚀 Initializing ABSA Model Service on {self.device} ---")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = DziriBERT_ABSA(self.model_name, len(self.TOPICS), len(self.INTENTS))
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            print("✅ ABSA Model Service ready (Notebook Optimized).")
        except Exception as e:
            print(f"❌ Error initializing ABSA Model Service: {e}")
            raise e

    def predict_batch(self, comments: List[str], threshold: float = 0.5) -> List[List[str]]:
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
            logits = outputs["logits"] # (batch, num_topics, num_intents)
            probabilities = torch.sigmoid(logits)
            
            # Binary predictions using multi-hot logic from notebook
            batch_preds = (probabilities >= threshold).int().cpu().numpy()

        results = []
        for i in range(len(valid_comments)):
            if not valid_comments[i]:
                results.append([])
                continue
            
            comment_labels = []
            has_intent = False
            
            for t_idx, topic in enumerate(self.TOPICS):
                topic_intents = []
                for j in range(len(self.INTENTS)):
                    if batch_preds[i, t_idx, j] == 1:
                        intent_name = self.ID2INTENT[j]
                        if intent_name != "none":
                            topic_intents.append(intent_name)
                            # Dashboard compatible format: e.g. "food_appreciation"
                            comment_labels.append(f"{topic}_{intent_name}")
                            has_intent = True
            
            # Manual Flag: Only out_of_scope if NOTHING was detected (all pillars 'none')
            if not has_intent:
                comment_labels.append("out_of_scope")
                
            results.append(comment_labels)
        
        return results

    def get_feeling(self, labels: List[str]) -> str:
        pos_count = sum(1 for label in labels if 'appreciation' in label)
        neg_count = sum(1 for label in labels if 'complaint' in label)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def map_to_platform_labels(self, labels: List[str]) -> List[str]:
        # LABELS are already in correct platform format: pillar_intent
        return labels

_model_service = None

def get_model_service():
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service
