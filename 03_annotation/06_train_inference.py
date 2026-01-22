import pandas as pd
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import os

import argparse

# --- Configuration ---
MODEL_NAME = "UBC-NLP/MARBERT"
MODEL_SAVE_PATH = "03_annotation/marbert_unthai_bootstrapped.pt"
DEVICE = torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu') 
CATEGORIES = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
MAX_LEN = 64
BATCH_SIZE = 32
EPOCHS = 1
LEARNING_RATE = 2e-5

# --- Label Mapping ---
# 0 -> None
# 1 -> Appreciation
# 2 -> Complaint
def prepare_labels(df):
    labels = []
    for _, row in df.iterrows():
        oos_val = 1.0 if str(row['out_of_scope']).lower() == 'true' else 0.0
        l = [oos_val]
        found_active = False
        for cat in CATEGORIES:
            val = str(row[cat]).lower() if pd.notna(row[cat]) else ""
            if val == 'appreciation':
                l.append(1)
                found_active = True
            elif val == 'complaint':
                l.append(2)
                found_active = True
            else:
                l.append(0)
        labels.append((l, found_active))
    return labels

def oversample_data(train_texts, train_labels_raw):
    oversampled_texts = []
    oversampled_labels = []
    for text, (labels, found_active) in zip(train_texts, train_labels_raw):
        oversampled_texts.append(text)
        oversampled_labels.append(labels)
        
        # Boost Appreciations and Complaints
        if found_active:
            for _ in range(3): # 4x total boost
                oversampled_texts.append(text)
                oversampled_labels.append(labels)
    
    return oversampled_texts, oversampled_labels

class AnnotationDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    def __len__(self): return len(self.texts)
    def __getitem__(self, item):
        text = str(self.texts[item])
        inputs = self.tokenizer.encode_plus(text, None, add_special_tokens=True, max_length=self.max_len, padding='max_length', truncation=True, return_token_type_ids=True)
        return {'input_ids': torch.tensor(inputs['input_ids'], dtype=torch.long), 'attention_mask': torch.tensor(inputs['attention_mask'], dtype=torch.long), 'labels': torch.tensor(self.labels[item], dtype=torch.float)}

class MultiTaskMARBERT(nn.Module):
    def __init__(self, model_name):
        super(MultiTaskMARBERT, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.oos_head = nn.Linear(768, 1)
        # 3 outputs per head: 0=None, 1=Appreciation, 2=Complaint
        self.topic_heads = nn.ModuleList([nn.Linear(768, 3) for _ in range(6)])

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        x = self.dropout(pooled_output)
        return self.oos_head(x), [head(x) for head in self.topic_heads]

def run(input_file, output_file, skip_train=False):
    if not os.path.exists(input_file): 
        print(f"❌ Error: {input_file} not found.")
        return
    
    df = pd.read_csv(input_file)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = MultiTaskMARBERT(MODEL_NAME).to(DEVICE)

    if not skip_train:
        labeled_mask = df['out_of_scope'].isin(['True', 'False', True, False])
        train_df = df[labeled_mask].copy()
        
        if len(train_df) > 0:
            train_labels_raw = prepare_labels(train_df)
            train_texts = train_df['comment_text'].values.tolist()
            train_texts, train_labels = oversample_data(train_texts, train_labels_raw)
            
            print(f"📊 Training on {len(train_texts)} samples (3-way Sentiment Rework).")
            train_ds = AnnotationDataset(train_texts, train_labels, tokenizer, MAX_LEN)
            train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
            
            oos_criterion, topic_criterion = nn.BCEWithLogitsLoss(), nn.CrossEntropyLoss()
            optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

            model.train()
            for batch in tqdm(train_loader, desc="Training"):
                optimizer.zero_grad()
                oos_logits, topic_logits = model(batch['input_ids'].to(DEVICE), batch['attention_mask'].to(DEVICE))
                loss = oos_criterion(oos_logits.view(-1), batch['labels'][:, 0].to(DEVICE))
                for i in range(len(topic_logits)):
                    loss += topic_criterion(topic_logits[i], batch['labels'][:, i+1].to(DEVICE).long())
                loss.backward(); optimizer.step()

            print(f"💾 Saving weights to {MODEL_SAVE_PATH}...")
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
        else:
            print("⚠️ No labeled data found to train on. Using existing/base weights.")

    if os.path.exists(MODEL_SAVE_PATH):
        print(f"📥 Loading weights from {MODEL_SAVE_PATH}...")
        model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=DEVICE))

    print(f"🚀 Running Inference on {input_file}...")
    model.eval()
    all_preds = []
    full_ds = AnnotationDataset(df['comment_text'].tolist(), [[0]*7]*len(df), tokenizer, MAX_LEN)
    full_loader = DataLoader(full_ds, batch_size=BATCH_SIZE)

    with torch.no_grad():
        for i, batch in enumerate(tqdm(full_loader, desc="Predicting")):
            oos_logits, topic_logits = model(batch['input_ids'].to(DEVICE), batch['attention_mask'].to(DEVICE))
            oos_probs = torch.sigmoid(oos_logits).cpu().numpy()
            for k in range(len(oos_probs)):
                idx = i*BATCH_SIZE + k
                if idx >= len(df): break
                row_pred = {'comment_id': df.iloc[idx]['comment_id'], 'ai_out_of_scope': bool(oos_probs[k] > 0.5)}
                for j, cat in enumerate(CATEGORIES):
                    pred_class = torch.argmax(topic_logits[j][k]).item()
                    mapping = {0: 'None', 1: 'appreciation', 2: 'complaint'}
                    row_pred[f'ai_{cat}'] = mapping.get(pred_class, 'None')
                all_preds.append(row_pred)

    pd.DataFrame(all_preds).to_csv(output_file, index=False)
    print(f"✨ 3-way predictions saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="03_annotation/annotation_part_1.csv", help="Input Master CSV")
    parser.add_argument("--output", help="Output AI JSON/CSV")
    parser.add_argument("--predict_only", action="store_true", help="Skip training and just run inference")
    args = parser.parse_args()

    # Default output logic
    if not args.output:
        args.output = args.input.replace(".csv", "_ai.csv")

    run(args.input, args.output, skip_train=args.predict_only)
