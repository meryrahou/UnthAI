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
        pooled_output = outputs.pooler_output
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

test_comments = [
    "bnina bzaf",           # food appreciation
    "service bati2",        # service complaint
    "ghali bzaf",           # price complaint (or appreciation depending on context, usually complaint)
    "makan makan",          # negative general
    "win jaya?"             # inquiry location/place
]

with torch.no_grad():
    for comment in test_comments:
        inputs = tokenizer(comment, truncation=True, padding="max_length", max_length=128, return_tensors="pt")
        outputs = model(inputs["input_ids"], inputs["attention_mask"])
        logits = outputs["logits"][0] # (num_topics, num_intents)
        probs = torch.sigmoid(logits)
        
        print(f"\nComment: {comment}")
        for i, topic in enumerate(['food', 'service', 'place', 'delivery', 'price', 'treatment']):
            top_idx = probs[i].argmax().item()
            print(f"  {topic}: top_idx={top_idx}, probs={probs[i].tolist()}")
