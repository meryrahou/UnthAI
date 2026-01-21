import torch
import torch.nn as nn
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import os
import argparse

# --- Configuration ---
MODEL_NAME = "UBC-NLP/MARBERT"
# Using the primary weights in the root annotation folder
WEIGHTS_PATH = "../marbert_unthai_bootstrapped.pt"
DEVICE = torch.device('cpu') 
CATEGORIES = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
INTENTS = ['None', 'appreciation', 'complaint', 'inquiry', 'recommendation']

class MultiTaskMARBERT(nn.Module):
    def __init__(self, model_name):
        super(MultiTaskMARBERT, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.oos_head = nn.Linear(768, 1)
        # 6 topic heads, each 3 classes: 0=None, 1=appreciation, 2=complaint
        self.topic_heads = nn.ModuleList([nn.Linear(768, 3) for _ in range(6)])

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        x = self.dropout(pooled_output)
        oos_logits = self.oos_head(x)
        topic_logits = [head(x) for head in self.topic_heads]
        return oos_logits, topic_logits

class PredictionDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        encoding = self.tokenizer.encode_plus(
            text, add_special_tokens=True, max_length=self.max_len,
            padding='max_length', truncation=True, return_attention_mask=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten()
        }

def run_inference(input_file):
    if not os.path.exists(WEIGHTS_PATH):
        print(f"❌ Error: Model weights not found at {WEIGHTS_PATH}")
        return

    df = pd.read_csv(input_file)
    texts = df['comment_text'].values.tolist()
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = MultiTaskMARBERT(MODEL_NAME).to(DEVICE)
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=DEVICE, weights_only=True))
    model.eval()

    dataset = PredictionDataset(texts, tokenizer, 64)
    loader = DataLoader(dataset, batch_size=8)

    all_oos = []
    all_topic_intents = [[] for _ in range(6)]

    print(f"🤖 AI is analyzing {len(texts)} comments...")
    with torch.no_grad():
        for batch in tqdm(loader):
            ids = batch['input_ids'].to(DEVICE)
            mask = batch['attention_mask'].to(DEVICE)
            oos_logits, topic_logits = model(ids, mask)
            
            # OOS (Binary Logits)
            oos_probs = torch.sigmoid(oos_logits).cpu().flatten().tolist()
            all_oos.extend(["True" if p > 0.5 else "False" for p in oos_probs])
            
            # Topics (3-way)
            for i, head_logits in enumerate(topic_logits):
                preds = torch.argmax(head_logits, dim=1).cpu().tolist()
                # 0=None, 1=appreciation, 2=complaint
                mapping = {0: 'None', 1: 'appreciation', 2: 'complaint'}
                all_topic_intents[i].extend([mapping.get(p, 'None') for p in preds])

    ai_df = pd.DataFrame({'comment_id': df['comment_id']})
    ai_df['ai_out_of_scope'] = all_oos
    for i, cat in enumerate(CATEGORIES):
        ai_df[f'ai_{cat}'] = all_topic_intents[i]

    output_file = input_file.replace(".csv", "_ai.csv")
    ai_df.to_csv(output_file, index=False)
    print(f"✨ AI predictions saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="CSV file to run AI on")
    args = parser.parse_args()
    run_inference(args.file)
