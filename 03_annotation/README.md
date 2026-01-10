# 📂 03_Annotation: Manual Labeling Phase

This folder contains the datasets and tools for manual sentiment and topic annotation. 

## 🚀 Getting Started

To launch the interactive annotation tool, follow these steps:

### 1. Prerequisites
Ensure you have the required Python packages installed. From the root of the project, run:
```bash
source venv/bin/activate
pip install fastapi uvicorn pandas python-multipart
```

### 2. Launch the tool
Run the following command, replacing `annotation_part_X.csv` with your file:
```bash
python3 03_annotation/04_annotation_tool.py annotation_part_2.csv
```
*If no argument is provided, it defaults to `annotation_part_1.csv`.*

### 3. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** to start labeling.

---

## 🛠 Tool Features
- **Auto-Save**: Labels are saved directly to the CSV as soon as you click "Save & Next".
- **Resumption**: The tool automatically starts at the first unlabelled comment when restarted.
- **Progress Tracking**: A progress bar at the top shows how many comments you've completed.
- **Out of Scope Logic**: If you select `None` for every category, the system automatically marks the comment as `out_of_scope = True`.

## 📂 File Summary
- `annotation_part_1.csv` ... `annotation_part_4.csv`: Individual subsets for team members.
- `04_annotation_tool.py`: The FastAPI-based annotation interface.
- `01_apply_annotation_schema.py`: Utility to initialize required columns.
- `02_update_schema_v2.py`: Script to update or correct schema issues.
- `03_split_dataset.py`: Utility to re-partition the main dataset if needed.
