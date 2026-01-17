import pandas as pd
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import os

# --- Configuration ---
MODEL_NAME = "UBC-NLP/MARBERT"
MODEL_SAVE_PATH = "03_annotation/marbert_unthai_bootstrapped.pt"
DEVICE = torch.device('cpu') # System stability: forcing CPU
INPUT_FILE = "03_annotation/annotation_part_1.csv"
OUTPUT_FILE = "03_annotation/annotation_part_1_ai.csv"
CATEGORIES = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
# INTENTS = ['None', 'appreciation', 'complaint', 'inquiry', 'recommendation'] # No longer needed for binary
# INTENT_LABELS = {intent: i for i, intent in enumerate(INTENTS)} # No longer needed for binary
# INTENT_LABELS[''] = 0 # No longer needed for binary
# INTENT_LABELS['nan'] = 0 # No longer needed for binary
MAX_LEN = 64
BATCH_SIZE = 2
EPOCHS = 1
LEARNING_RATE = 2e-5

# --- Label Mapping ---
# 1 -> Appreciation (Goal)
# Everything else -> Not Appreciation (0)
def prepare_labels(df):
    labels = []
    for _, row in df.iterrows():
        # Ensure 'out_of_scope' is handled correctly for boolean/string values
        oos_val = 1.0 if str(row['out_of_scope']).lower() == 'true' else 0.0
        l = [oos_val]
        for cat in CATEGORIES:
            val = str(row[cat]).lower() if pd.notna(row[cat]) else ""
            # Binary: 1 if Appreciation, else 0
            if val == 'appreciation':
                l.append(1)
            else:
                l.append(0)
        labels.append(l)
    return labels

def oversample_data(train_texts, train_labels):
    oversampled_texts = []
    oversampled_labels = []
    for text, labels in zip(train_texts, train_labels):
        oversampled_texts.append(text)
        oversampled_labels.append(labels)
        
        # If ANY category has an appreciation (label 1), boost it!
        # This helps the model see enough positive examples.
        if any(labels[i+1] == 1 for i in range(6)):
            for _ in range(3): # 4x total boost for appreciations (1 original + 3 copies)
                oversampled_texts.append(text)
                oversampled_labels.append(labels)
    
    return oversampled_texts, oversampled_labels

# --- Dataset Definition ---
class AnnotationDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        inputs = self.tokenizer.encode_plus(
            text, None, add_special_tokens=True, max_length=self.max_len,
            padding='max_length', truncation=True, return_token_type_ids=True
        )
        return {
            'input_ids': torch.tensor(inputs['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(inputs['attention_mask'], dtype=torch.long),
            'labels': torch.tensor(self.labels[item], dtype=torch.float)
        }

# --- Multi-Task Model ---
class MultiTaskMARBERT(nn.Module):
    def __init__(self, model_name):
        super(MultiTaskMARBERT, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        
        # 1 binary head for out_of_scope
        self.oos_head = nn.Linear(768, 1) # Binary Logits
        
        # 6 classification heads for each topic
        # Each topic has 2 classes (0: Not Appreciation, 1: Appreciation)
        self.topic_heads = nn.ModuleList([nn.Linear(768, 2) for _ in range(6)])

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1] # [CLS] token
        x = self.dropout(pooled_output)
        
        oos_logits = self.oos_head(x)
        topic_logits = [head(x) for head in self.topic_heads]
        return oos_logits, topic_logits

# --- Training / Inference Logic ---
def run():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    df = pd.read_csv(INPUT_FILE)
    
    # Filter for labeled data
    labeled_mask = df['out_of_scope'].notna() & (df['out_of_scope'].astype(str) != "")
    train_df = df[labeled_mask].copy()

    # Prepare Labels using the new prepare_labels function
    train_labels = prepare_labels(train_df)
    train_texts = train_df['comment_text'].values.tolist()
    
    # --- Oversampling ---
    train_texts, train_labels = oversample_data(train_texts, train_labels)
    
    print(f"📊 Training on {len(train_texts)} samples (after binary oversampling).")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds = AnnotationDataset(train_texts, train_labels, tokenizer, MAX_LEN)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

    device = DEVICE
    print(f"Using device: {device}")
    
    model = MultiTaskMARBERT(MODEL_NAME).to(device)
    
    # Criteria
    oos_criterion = nn.BCEWithLogitsLoss()
    topic_criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    model.train()
    for epoch in range(EPOCHS):
        epoch_loss = 0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
        for batch in pbar:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            oos_logits, topic_logits = model(input_ids, attention_mask)

            # OOS Loss
            loss = oos_criterion(oos_logits.view(-1), labels[:, 0])
            
            # Topic Losses
            for i in range(len(topic_logits)):
                # CrossEntropy expects Long tensor for indices (0 or 1)
                loss += topic_criterion(topic_logits[i], labels[:, i+1].long())
            
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            pbar.set_postfix({'loss': f"{loss.item():.4f}"})
        
        print(f"Epoch {epoch+1} Loss: {epoch_loss/len(train_loader):.4f}")

    # --- Step 4: Save ---
    print(f"💾 Saving binary model weights to {MODEL_SAVE_PATH}...")
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print("✅ Model saved.")

    # --- Step 5: Inference ---
    print("Running Binary Inference on full dataset...")
    model.eval()
    all_preds = []
    
    # Predict on the same input file
    full_ds = AnnotationDataset(df['comment_text'].tolist(), [[0]*7]*len(df), tokenizer, MAX_LEN)
    full_loader = DataLoader(full_ds, batch_size=BATCH_SIZE)

    with torch.no_grad():
        for batch in tqdm(full_loader, desc="Predicting"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            oos_logits, topic_logits = model(input_ids, attention_mask)
            
            oos_probs = torch.sigmoid(oos_logits).cpu().numpy()
            
            for i in range(len(oos_probs)):
                row_pred = {
                    'comment_id': df.iloc[len(all_preds)]['comment_id'],
                    'ai_out_of_scope': bool(oos_probs[i] > 0.5)
                }
                for j, cat in enumerate(CATEGORIES):
                    # argmax for binary classification (0: None, 1: Appreciation)
                    pred_class = torch.argmax(topic_logits[j][i]).item()
                    row_pred[f'ai_{cat}'] = 'appreciation' if pred_class == 1 else 'None'
                all_preds.append(row_pred)

    pd.DataFrame(all_preds).to_csv(OUTPUT_FILE, index=False)
    print(f"✨ Binary predictions saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
