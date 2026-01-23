# UnthAI Solutions - Sentiment Analysis Dashboard

This folder contains the complete UnthAI solution, consisting of a **FastAPI backend** and a **Vite + React frontend**.

## 🚀 Quick Launch

### 1. Backend Setup
The backend serves the sentiment data and handles AI-based insights.

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (if not already present)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the server
# Use PYTHONPATH=. so the app can find the internal modules
PYTHONPATH=. ./venv/bin/python app/main.py
```

**One-liner (macOS/Linux):**
```bash
cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt && PYTHONPATH=. ./venv/bin/python app/main.py
```

### 2. Frontend Setup
The frontend provides a premium dashboard to visualize the sentiment trends.

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Launch the development server
npm run dev
```

**One-liner:**
```bash
cd frontend && npm install && npm run dev
```

The dashboard will be available at `http://localhost:5173`.

---

## 🔑 Authentication
To access the dashboard, use the following credentials:

- **Restaurant Name**: Any valid name from `backend/data/names.txt` (e.g., `Restaurant San Benito`, `American Burger`, `KFC`).
- **Password**: `1234`

---

## 📂 Project Structure

- **`backend/`**: FastAPI application.
  - **`app/main.py`**: API entry point and routes.
  - **`app/services/data_manager.py`**: Handles CSV processing and filtering.
  - **`data/`**: Contains the master dataset (`master_data.csv`) and cached processed files.
- **`frontend/`**: React application built with Vite.
  - **`src/pages/`**: Contains the dashboard, post analysis, and trend explorer pages.
  - **`src/components/`**: Reusable UI components.

---

## 🛠 Features
- **Trend Explorer**: Dynamic word cloud with sentiment-based coloring.
- **Post Analysis**: Deep dive into specific social media posts and their comment sections.
- **AI Insights**: Automated strategy recommendations based on customer feedback.
- **Filtering**: Date-based filtering for all metrics.
