import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel

class DziriBERT_ABSA(nn.Module):
    def __init__(self, model_name, num_topics, num_intents):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.topic_classifiers = nn.ModuleList([
            nn.Linear(768, num_intents) for _ in range(num_topics)
        ])

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # Check if model has a pooler
        if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
            pooled_output = outputs.pooler_output
        else:
            pooled_output = outputs.last_hidden_state[:, 0, :]
        logits = torch.stack([clf(pooled_output) for clf in self.topic_classifiers], dim=1)
        return {"logits": logits}

device = "cpu"
model_name = "alger-ia/dziribert"
num_topics = 6
num_intents = 5

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = DziriBERT_ABSA(model_name, num_topics, num_intents)
model.load_state_dict(torch.load("Solution/backend/model/dziribert_absa-2.pt", map_location=device))
model.eval()

INTENT_MAP = {
    0: "appreciation",
    1: "complaint",
    2: "recommendation",
    3: "inquiry",
    4: "none"
}

test_comments = [
    "bnina bzaf",           # food appreciation -> should be food: 0
    "machi bnina",          # food complaint -> should be food: 1
    "service bati2",        # service complaint -> should be service: 1
    "ya3tikoum saha",       # general appreciation
    "ghali bzaf",           # price complaint -> should be price: 1
    "win jaya?",             # inquiry location -> should be place: 3
    "zidoulna f l'menu"     # food recommendation -> should be food: 2
]

with torch.no_grad():
    for comment in test_comments:
        inputs = tokenizer(comment, truncation=True, padding="max_length", max_length=128, return_tensors="pt")
        outputs = model(inputs["input_ids"], inputs["attention_mask"])
        logits = outputs["logits"][0] 
        probs = torch.sigmoid(logits)
        
        print(f"\nComment: {comment}")
        for i, topic in enumerate(['food', 'service', 'place', 'delivery', 'price', 'treatment']):
            top_idx = probs[i].argmax().item()
            intent = INTENT_MAP.get(top_idx, "unknown")
            print(f"  {topic}: {intent} ({probs[i][top_idx]:.4f})")
