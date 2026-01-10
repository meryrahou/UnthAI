# UnthAI - Algerian TikTok Food Sentiment Analysis

This project collects and processes TikTok comments related to the Algerian food scene for sentiment and intent analysis.

## Repository Structure

The project is organized into logical phases:

### 📂 [01_collection/](file:///Users/mery/GitHub/UnthAI/01_collection/)
*Data Acquisition & Discovery*
- `full_collection.py`: Script for discovering and scraping TikTok comments via JSON interception.
- `scraped_video_ids.txt`: Registry of processed videos to avoid duplication.
- `tiktok_dataset.csv`: Raw scraped data.

### 📂 [02_preprocessing/](file:///Users/mery/GitHub/UnthAI/02_preprocessing/)
*Data Cleaning & Pipeline*
- `01_merge_datasets.py` through `07_extract_emojis.py`: Sequential scripts for data refinement, restaurant labeling, and feature extraction.
- **`08_preprocessing_pipeline.ipynb`**: The main Jupyter notebook for text normalization, emoji mapping, and tag removal.
- `PREPROCESSING_GUIDE.md`: Detailed documentation of the NLP rules and categories.
- `dataset.csv`: The unified dataset ready for the pipeline.
- `dataset_preprocessed.csv`: The final, high-quality output for model training.

### 📂 [03_annotation/](file:///Users/mery/GitHub/UnthAI/03_annotation/)
*Manual Labeling Phase*
- `04_annotation_tool.py`: Interactive web-based annotation tool.
- `annotation_part_1.csv` ... `annotation_part_4.csv`: Partitioned datasets for team annotation.
- `01_apply_annotation_schema.py`: Utility script for schema maintenance.
- `03_split_dataset.py`: Script used for partitioning.

---

## Getting Started

1. **Collection**: Use `01_collection/full_collection.py` to gather new data.
2. **Preprocessing**: 
   - Run the scripts in `02_preprocessing/` sequentially (01 to 07).
   - Use the `08_preprocessing_pipeline.ipynb` to generate the final training set.
3. **Reference**: Consult `02_preprocessing/PREPROCESSING_GUIDE.md` for labeling logic and category definitions.

## Project Archives
Keep the following ZIP files in the root for historical reference:
- `Initial dataset - Final Dataset.zip`
- `tiktok_final_dataset.csv.zip`