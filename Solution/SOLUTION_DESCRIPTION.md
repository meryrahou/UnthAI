# UnthAI Solutions: Comprehensive Solution Description

## 1. Executive Summary

**UnthAI** is a state-of-the-art Reputation Management and Sentiment Analysis platform specifically tailored for the Algerian hospitality and restaurant industry. By leveraging specialized natural language processing (NLP), UnthAI transforms thousands of messy social media comments into clear, actionable business insights.

The solution enables restaurant owners to understand their digital footprint across **TikTok, Instagram, Facebook, and Google Maps**, providing a "Brand Health" pulse that standard analytics tools miss.

---

## 2. Business Perspective

### The Problem

Restaurant owners in Algeria face a unique challenge: their customers provide feedback in a complex mix of **Algerian Darja, Arabic, French, and English**. Generic sentiment analysis tools (built for standard English or French) fail to understand the nuance, sarcasm, and specific cultural expressions used by Algerian diners.

### The Solution

UnthAI bridges this gap with:

- **Centralized Monitoring**: No more switching between apps. All feedback from all platforms is in one place.
- **Aspect-Based Analysis**: It doesn't just say a comment is "negative"; it identifies _what_ the problem is (e.g., "Food is cold" vs. "Service is slow").
- **Strategic Actionability**: Instead of just showing charts, the system generates "Action Cards"—specific tasks like "Resolve slow service complaints" or "Respond to price-related inquiries."

### Key Business KPIs

- **Brand Health Index**: A proprietary score calculated by the ratio of positive to polarized feedback.
- **Pillar Performance**: Tracking satisfaction across 6 key areas: Food, Service, Place, Delivery, Price, and Treatment.
- **Sentiment History**: Visualizing how reputation evolves over time to measure the impact of menu changes or marketing campaigns.

---

## 3. Technical Architecture

The UnthAI solution is built using a modern, scalable, and high-performance stack:

### Frontend (User Interface)

- **Framework**: React.js with Vite for ultra-fast performance.
- **Design**: A premium **Glassmorphism** aesthetic using vanilla CSS, designed to feel sophisticated and modern.
- **Data Visualization**: Recharts for interactive sentiment distributions and trend lines.
- **Localization**: Fully tri-lingual support (**English, French, Arabic**) with a custom translation engine.

### Backend (API & Logic)

- **Framework**: FastAPI (Python), chosen for its asynchronous capabilities and speed.
- **Data Processing**: Pandas for heavy CSV-based data manipulation and filtering.
- **Security**: JWT (JSON Web Tokens) for secure, role-based access.

### AI Engine (The Core)

- **Model**: **DziriBERT-ABSA**. A custom neural network architecture based on `alger-ia/dziribert`.
- **Architecture**: A multi-head classification head that processes a single comment and predicts multiple labels across 6 topics and 5 intents simultaneously.
- **Training**: Optimized for the Algerian dialect, understanding local slang and mixed-language feedback.

---

## 4. Deep Dive: How It Works

### The Data Pipeline (ETL)

1.  **Extraction**: Python-based scrapers retrieve comments and metadata from TikTok, Facebook, Instagram, and Google Maps.
2.  **Harmonization**: Scripts like `format_hicham_fb.py` and `combine_hicham_data.py` clean the raw data, standardizing dates, likes, and text formats into a `Master Dataset`.
3.  **Refining**: The `Data Manager` service isolates a specific restaurant's data for analysis.

### The AI Analysis (Inference)

When a user clicks "Process Data":

1.  The backend triggers the **BERT Model**.
2.  Each comment is analyzed for **Aspects** (Food, Service, etc.) and **Intents** (Appreciation, Complaint, Inquiry, Recommendation).
3.  The model calculates the dominant **Feeling** (Sentiment).
4.  Data is saved to a specialized `processed_<restaurant>.csv`, which serves as the "cached" intelligence for the dashboard.

### The Insight Generation

The system clusters similar complaints. If 10 people mention "wait time" or "slow," the **Action Center** identifies this as a "High Priority" cluster and generates a card for the owner to address "Slow Service."

---

## 5. Directory Structure & Components

- **`/backend/app/main.py`**: The central nervous system, handling all API routes and logic.
- **`/backend/app/services/model_service.py`**: The bridge to the PyTorch/BERT model.
- **`/backend/app/services/data_manager.py`**: Handles the transition from raw CSV to AI-enriched intelligence.
- **`/frontend/src/pages/`**:
  - `Dashboard.jsx`: High-level summary and KPIs.
  - `PostAnalysis.jsx`: Granular view of specific social media posts.
  - `Trends.jsx`: Word cloud and keyword sentiment explorer.
  - `ActionCenter.jsx`: The task management hub for reputation improvement.
- **Root Scripts (`retrieve_...`, `combine_...`)**: The engineering pipeline used to gather and prepare data before it enters the application.

---

## 6. Why This Solution Matters

UnthAI isn't just a dashboard; it's a **Decision Support System**. In the competitive Algerian restaurant market, the difference between a 3-star and a 5-star reputation is the ability to listen to every customer. UnthAI makes that listening automated, intelligent, and profitable.
