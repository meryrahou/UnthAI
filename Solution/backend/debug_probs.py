import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

MODEL_PATH = "model/best_dziribert_sentimentversion2.pth"
MODEL_NAME = "alger-ia/dziribert"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

label_columns = [
    'food_positive', 'food_negative', 'food_neutral',
    'service_positive', 'service_negative', 'service_neutral',
    'place_positive', 'place_negative', 'place_neutral',
    'price_positive', 'price_negative', 'price_neutral',
    'delivery_positive', 'delivery_negative', 'delivery_neutral',
    'treatment_positive', 'treatment_negative', 'treatment_neutral',
    'out_of_scope_positive', 'out_of_scope_negative'
]

def debug():
    print(f"Loading model on {DEVICE}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=len(label_columns),
        problem_type="multi_label_classification"
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()

    test_comments = [
        "للأسف جينا الأسبوع الماضي كلينا عندكم سامحلي سرفيس يعيف اللحم قدموه بارد ممكن عليها جا ناشف المكان حنا قاعدين ناكلو و هوما ينشفو و يلوحو ف المنظف…والله على ماأقول شهيد .",
        "اللي كانوا هنا كارثة كبيرة . المعاملة سيئة الماكلة ماشي بنينة و زيد حطولنا les jetables مغسولين و فيهم الرغوة",
        "البنة ماكاش و الأسعار فوق الريح"
    ]

    encoding = tokenizer(test_comments, padding=True, truncation=True, max_length=128, return_tensors='pt').to(DEVICE)
    with torch.no_grad():
        outputs = model(**encoding)
        probs = torch.sigmoid(outputs.logits).cpu().numpy()

    for i, comment in enumerate(test_comments):
        print(f"\nText: {comment}")
        top_indices = probs[i].argsort()[-5:][::-1]
        for idx in top_indices:
            print(f"  {label_columns[idx]}: {probs[i][idx]:.4f}")

if __name__ == "__main__":
    debug()
