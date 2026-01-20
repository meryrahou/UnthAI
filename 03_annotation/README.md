# 📂 03_Annotation: AI-Assisted Sentiment Phase

This folder contains the tools for high-speed sentiment annotation using a 3-way MARBERT model (Appreciation, Complaint, or None).

## 🚀 Getting Started (Multi-User Workflow)

If you are a new annotator starting with a fresh partition (e.g., `annotation_part_2.csv`), follow these steps:

### 1. Model Reconstruction
The model weights are split into parts to fit on GitHub. You must merge them before the first run:
```bash
cd 03_annotation
cat marbert_unthai_bootstrapped.pt.part_* > marbert_unthai_bootstrapped.pt
```

### 2. Generate AI Predictions
Before starting the tool, run the AI to pre-label your specific partition. This makes the annotation process 10x faster.
```bash
# Run from the root of the project
python3 03_annotation/06_train_inference.py --input 03_annotation/annotation_part_2.csv --predict_only
```
*This generates `03_annotation/annotation_part_2_ai.csv`.*

### 3. Launch the Annotation Tool
Use the launcher to start your session. It will pull your partition and the matching AI suggestions automatically.
```bash
cd 03_annotation/team_toolkit
../../venv/bin/python launcher.py --master ../annotation_part_2.csv
```

### 4. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** to start labeling.

---

## 🛠 Optimized Workflow Features
- **Rainbow Suggestions**: The tool highlights the AI's prediction.
- **Turbo Shortcuts**:
    - **`S`**: Accept all AI suggestions and save immediately.
    - **`D`**: Save current labels and move to next.
    - **`K`**: Skip (ignores the comment for the rest of the session).
- **Auto-Sync**: Your manual labels are written directly back to your CSV file (`annotation_part_X.csv`).

## 📂 File Summary
- `marbert_unthai_bootstrapped.pt`: Reconstructed model weights.
- `06_train_inference.py`: Retrainer / Predictor script.
- `team_toolkit/launcher.py`: Main entry point for starting sessions.
- `team_toolkit/annotation_tool.py`: Web interface logic.
