from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import json
from app.services.data_manager import refresh_restaurant_data, get_processed_path

# --- Configuration ---
CSV_PATH = "/Users/mery/GitHub/UnthAI/Solution/backend/data/master_data.csv"
SECRET_KEY = "unthai_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="UnthAI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Loading (Legacy - Commented Out) ---
# PROCESSED_CSV_PATH = "/Users/mery/GitHub/UnthAI/Solution/backend/processed_san_benito.csv"
# try:
#     df_res = pd.read_csv(PROCESSED_CSV_PATH)
#     df_res = df_res.fillna("")
#     # Pre-calculate data bounds
#     if not df_res.empty:
#         df_res['date_dt_all'] = pd.to_datetime(df_res['date'], utc=True)
#         DATA_MIN = df_res['date_dt_all'].min().strftime('%Y-%m-%d')
#         DATA_MAX = df_res['date_dt_all'].max().strftime('%Y-%m-%d')
#     else:
#         DATA_MIN, DATA_MAX = "2026-01-01", "2026-01-30"
# except Exception as e:
#     print(f"Error loading processed CSV: {e}")
#     df_res = pd.DataFrame()
#     DATA_MIN, DATA_MAX = "2026-01-01", "2026-01-30"

# --- Dynamic Data Store ---
data_cache = {}

def get_restaurant_df(restaurant_name: str):
    if restaurant_name in data_cache:
        return data_cache[restaurant_name]
    
    path = get_processed_path(restaurant_name)
    if not os.path.exists(path):
        success = refresh_restaurant_data(restaurant_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"No data found for {restaurant_name}")
            
    df = pd.read_csv(path)
    df = df.fillna("")
    # Fix: Use 'mixed' format to handle 'Z' suffix and other variations
    df['date_dt_all'] = pd.to_datetime(df['date'], format='mixed', utc=True, errors='coerce')
    df = df.dropna(subset=['date_dt_all'])
    
    data_cache[restaurant_name] = df
    return df

# --- Auth Logic ---
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    restaurant_name: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        restaurant_name: str = payload.get("restaurant_name")
        if username is None or restaurant_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return {"username": username, "restaurant_name": restaurant_name}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Allow login with any restaurant name as long as password is correct
    if form_data.password == "1234":
        restaurant_name = form_data.username # We use username field for restaurant name
        
        # Verify it exists in master data before giving token
        df_master = pd.read_csv(CSV_PATH)
        if restaurant_name.lower() not in df_master['source_name'].str.lower().unique():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurant '{restaurant_name}' not found in our database.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token = create_access_token(data={
            "sub": f"{restaurant_name}@unthai.dz", 
            "restaurant_name": restaurant_name
        })
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. (Try 'unthai2026')",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- API Endpoints ---

@app.get("/api/user/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["restaurant_name"],
        "email": current_user["username"],
        "restaurant_name": current_user["restaurant_name"]
    }

@app.get("/api/dashboard/summary")
async def get_dashboard_summary(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    if df_user.empty:
        return {"error": "No data available"}

    d_df = df_user.copy()
    
    # Robust date conversion with mixed format support
    d_df['date_dt'] = pd.to_datetime(d_df['date'], format='mixed', utc=True, errors='coerce')
    d_df = d_df.dropna(subset=['date_dt'])
    
    if d_df.empty:
        return {"error": "No valid dates found in data"}

    if start_date and end_date and start_date != "" and end_date != "":
        try:
            s_dt = pd.to_datetime(start_date, utc=True)
            e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
            d_df = d_df[(d_df['date_dt'] >= s_dt) & (d_df['date_dt'] < e_dt)]
        except Exception as e:
            print(f"Filter error: {e}")
    else:
        if 'date_dt_all' in df_user.columns:
            start_date = df_user['date_dt_all'].min().strftime('%Y-%m-%d')
            end_date = df_user['date_dt_all'].max().strftime('%Y-%m-%d')
        else:
             start_date = d_df['date_dt'].min().strftime('%Y-%m-%d')
             end_date = d_df['date_dt'].max().strftime('%Y-%m-%d')

    total_comments = len(d_df)
    
    # Calculate sentiment distribution based on filtered data (d_df)
    pos_count = len(d_df[d_df['feeling'] == 'positive'])
    neg_count = len(d_df[d_df['feeling'] == 'negative'])
    neu_count = len(d_df[d_df['feeling'] == 'neutral'])
    
    sentiment_distribution = [
        {"name": "Appreciation", "value": pos_count, "color": "#10b981"},
        {"name": "Complaint", "value": neg_count, "color": "#ef4444"},
        {"name": "Neutral", "value": neu_count, "color": "#94a3b8"},
    ]
    
    # Use d_df for category performance
    categories = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
    recommendation_total = 0
    cat_mentions = {}
    cat_complaints = {}
    category_data = []
    
    for cat in categories:
        app_c = len(d_df[d_df[cat].astype(str).str.lower() == 'appreciation'])
        com_c = len(d_df[d_df[cat].astype(str).str.lower() == 'complaint'])
        rec_c = len(d_df[d_df[cat].astype(str).str.lower() == 'recommendation'])
        inq_c = len(d_df[d_df[cat].astype(str).str.lower() == 'inquiry'])
        
        recommendation_total += rec_c
        mentions = app_c + com_c + rec_c + inq_c
        cat_mentions[cat] = mentions
        cat_complaints[cat] = com_c
        
        if mentions > 0:
            category_data.append({
                "name": cat.capitalize(),
                "apprec": app_c,
                "compl": com_c,
                "rec": rec_c,
                "inq": inq_c
            })

    # Find Top Pillar & Complaint
    most_discussed_cat = max(cat_mentions, key=cat_mentions.get) if cat_mentions else "None"
    top_complaint_cat = max(cat_complaints, key=cat_complaints.get) if cat_complaints else "None"
    
    # Brand Health Index: Ratio of positives to total polarized feedback
    # This gives a much more representative score than (Pos-Neg)/Total
    total_polarized = pos_count + neg_count
    brand_health = int((pos_count / total_polarized) * 100) if total_polarized > 0 else 0

    # Dynamic Sentiment History (Grouped by Day)
    history = []
    if not d_df.empty:
        try:
            # Group by day and count feelings
            d_df['day'] = d_df['date_dt'].dt.strftime('%b %d')
            daily = d_df.groupby(['day', 'feeling']).size().unstack(fill_value=0)
            
            # Sort by actual date to keep timeline correct
            unique_days = d_df.sort_values('date_dt')['day'].unique()
            
            for day in unique_days:
                if day in daily.index:
                    row = daily.loc[day]
                    tot = row.sum()
                    history.append({
                        "name": day,
                        "pos": int((row.get('positive', 0) / tot) * 100) if tot > 0 else 0,
                        "neu": int((row.get('neutral', 0) / tot) * 100) if tot > 0 else 0,
                        "neg": int((row.get('negative', 0) / tot) * 100) if tot > 0 else 0
                    })
        except Exception as e:
            print(f"History calc error: {e}")
            history = [{"name": "No Data", "pos": 0, "neu": 0, "neg": 0}]

    if not history:
        history = [{"name": "Default", "pos": 70, "neu": 20, "neg": 10}]

    return {
        "startDate": start_date,
        "endDate": end_date,
        "kpis": [
            {"label": "Total Reviews", "value": f"{total_comments}", "trend": "Filtered", "status": "up", "id": "total"},
            {"label": "Brand Health", "value": f"{brand_health}%", "trend": "Sentiment", "status": "up", "id": "health"},
            {"label": "Most Discussed", "value": most_discussed_cat.capitalize(), "trend": "Popular", "status": "info", "id": "pillar"},
            {"label": "Top Complaint", "value": top_complaint_cat.capitalize(), "trend": "Attention", "status": "down", "id": "complaint"},
        ],
        "sentiment_distribution": sentiment_distribution,
        "category_data": category_data,
        "recommendation_count": recommendation_total,
        "sentiment_history": history[:40], # Increased limit to show much more of the timeline
        "platform_dist": [
            {"name": "TikTok", "value": len(d_df[d_df['platform'].str.lower() == 'tiktok'])},
            {"name": "Instagram", "value": len(d_df[d_df['platform'].str.lower() == 'instagram'])},
            {"name": "Facebook", "value": len(d_df[d_df['platform'].str.lower() == 'facebook'])},
            {"name": "Google Maps", "value": len(d_df[d_df['platform'].str.lower() == 'google maps'])},
        ],
        "insights": [
             {"text": f"Found <strong>{pos_count} Appreciations</strong> and <strong>{recommendation_total} Recommendations</strong>.", "status": "success"},
             {"text": f"Your most discussed pillar is <strong>{most_discussed_cat.capitalize()}</strong>.", "status": "info"},
             {"text": f"Top Complaint source: <strong>{top_complaint_cat.capitalize()}</strong>.", "status": "warning"}
        ]
    }

@app.get("/api/posts")
async def get_posts(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    
    d_df = df_user.copy()
    if 'date_dt' not in d_df.columns:
         d_df['date_dt'] = pd.to_datetime(d_df['date'], format='mixed', utc=True, errors='coerce')
    
    if start_date and end_date and start_date != "" and end_date != "":
        try:
            s_dt = pd.to_datetime(start_date, utc=True)
            e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
            d_df = d_df[(d_df['date_dt'] >= s_dt) & (d_df['date_dt'] < e_dt)]
        except Exception as e:
            print(f"Filter error in posts: {e}")

    # Group by post_id to get unique posts
    post_ids = d_df['post_id'].unique().tolist()
    posts = []
    categories = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
    
    for pid in post_ids:
        # Always use the FULL history to determine the true post date
        p_df_full = df_user[df_user['post_id'] == pid]
        if p_df_full.empty: continue

        platform = p_df_full['platform'].iloc[0]
        try:
            # Calculate the immutable creation date of the post
            if 'date_dt' not in p_df_full.columns:
                 p_df_full = p_df_full.copy()
                 p_df_full['date_dt'] = pd.to_datetime(p_df_full['date'], format='mixed', utc=True)
            
            creation_date_dt = p_df_full['date_dt'].min()
            earliest_date = creation_date_dt.strftime('%b %d, %Y')
            
            # STRICT FILTER: If the post was created outside the selected range, HIDE IT.
            if start_date and end_date and start_date != "" and end_date != "":
                s_dt = pd.to_datetime(start_date, utc=True)
                e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
                if not (s_dt <= creation_date_dt < e_dt):
                    continue

        except Exception as e:
            # If date parsing fails, we assume it's valid to show (or handle differently)
            # But usually we fallback to safe defaults
            creation_date_dt = None
            earliest_date = "N/A"

        # Now determine which comments to analyze. 
        # For "Post Analysis", usually we show the full post stats unless specifically requested otherwise?
        # IMPORTANT: The user wanted "stats for this period" in dashboard, but here they seem focused on "Post Lists".
        # Let's show the FULL stats for the post so the "Analyzing X interactions" matches the actual post content.
        p_df = p_df_full 

        pos_count = len(p_df[p_df['feeling'] == 'positive'])
        neg_count = len(p_df[p_df['feeling'] == 'negative'])
        neu_count = len(p_df[p_df['feeling'] == 'neutral'])
        total_p = len(p_df)
        
        cat_performance = []
        for cat in categories:
            app_c = len(p_df[p_df[cat].astype(str).str.lower() == 'appreciation'])
            com_c = len(p_df[p_df[cat].astype(str).str.lower() == 'complaint'])
            rec_c = len(p_df[p_df[cat].astype(str).str.lower() == 'recommendation'])
            inq_c = len(p_df[p_df[cat].astype(str).str.lower() == 'inquiry'])
            
            total_cat = app_c + com_c + rec_c + inq_c
            if total_cat > 0:
                score = int(((app_c - com_c) / total_cat) * 50 + 50)
                cat_performance.append({
                    "name": cat.capitalize(), 
                    "score": score,
                    "volume": total_cat,
                    "critical": com_c > app_c
                })
        
        posts.append({
            "id": int(pid),
            "platform": "googlemaps" if "maps" in platform.lower() else platform.lower().replace(" ", ""),
            "author": f"Post {int(pid)} from {platform}",
            "date": earliest_date,
            "content": f"Analyzing {total_p} recent interactions.",
            "commentCount": total_p,
            "likes": int(p_df['likesCount'].sum()),
            "sentiment": {
                "pos": int((pos_count / total_p) * 100) if total_p > 0 else 0,
                "neu": int((neu_count / total_p) * 100) if total_p > 0 else 0,
                "neg": int((neg_count / total_p) * 100) if total_p > 0 else 0
            },
            "categories": cat_performance
        })
    
    return posts

@app.get("/api/posts/{post_id}/comments")
async def get_post_comments(post_id: int, current_user: dict = Depends(get_current_user)):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    
    # Filter by the physical post_id column
    c_df = df_user[df_user['post_id'] == post_id].head(1000)
    if c_df.empty: return []
    
    comments = []
    cols = df_user.columns
    for _, row in c_df.iterrows():
        try:
            preds_str = row.get('model_prediction', '[]')
            preds = json.loads(preds_str) if isinstance(preds_str, str) else []
        except:
            preds = []
            
        main_cat = "General"
        # Check model predictions first
        if preds and len(preds) > 0:
            main_cat = str(preds[0]).split('_')[0].capitalize()
        
        # Determine sentiment type
        c_type = "neutral"
        if str(row.get('out_of_scope', '')).lower() in ['true', '1', 'yes']:
            c_type = "out_of_scope"
        elif any("recommendation" in str(p).lower() for p in preds): 
            c_type = "recommendation"
        elif any("inquiry" in str(p).lower() for p in preds): 
            c_type = "inquiry"
        elif str(row.get('feeling', '')).lower() == 'positive': 
            c_type = "appreciation"
        elif str(row.get('feeling', '')).lower() == 'negative': 
            c_type = "complaint"
        
        # Fallback/Refine both category and type from raw columns
        for cat_col in ['food', 'service', 'place', 'delivery', 'price', 'treatment']:
            val = str(row.get(cat_col, '')).lower()
            if val != "":
                # If we were at "General", fix the category
                if main_cat == "General":
                    main_cat = cat_col.capitalize()
                
                # If it's a special type, prioritize it over general feeling
                if val == 'recommendation': 
                    c_type = "recommendation"
                elif val == 'inquiry': 
                    c_type = "inquiry"

        comments.append({
            "text": str(row.get('comment_text', 'No content')),
            "type": c_type,
            "category": main_cat,
            "time": str(row.get('date', 'Recent'))[:10],
            "likesCount": int(row['likesCount']) if 'likesCount' in cols and pd.notnull(row['likesCount']) else 0,
            "predictions": preds
        })
    
    return comments

@app.get("/api/trends")
async def get_trends(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    
    # Filter by date
    d_df = df_user.copy()
    if 'date_dt' not in d_df.columns:
         d_df['date_dt'] = pd.to_datetime(d_df['date'], format='mixed', utc=True, errors='coerce')

    if start_date and end_date and start_date != "" and end_date != "":
        try:
            s_dt = pd.to_datetime(start_date, utc=True)
            e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
            d_df = d_df[(d_df['date_dt'] >= s_dt) & (d_df['date_dt'] < e_dt)]
        except:
            pass
    
    # Filter out out_of_scope comments
    d_df = d_df[d_df['out_of_scope'].astype(str).str.lower() != 'true']
    
    # Simple Word Frequency Logic
    text_data = " ".join(d_df['comment_text'].astype(str).tolist()).lower()
    
    import re
    from collections import Counter
    
    # Update regex to support Arabic script explicitly
    words = re.findall(r'[\w\u0600-\u06FF]+', text_data)
    
    # Custom Stopword List (English, French, basic Arabic/Chat)
    stopwords = {
        'the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'for', 'with', 'on', 'was', 'very',
        'le', 'la', 'les', 'et', 'de', 'du', 'des', 'un', 'une', 'est', 'c', 'ce', 'que', 'qui', 
        'pas', 'tres', 'très', 'bon', 'bien', 'avec', 'pour', 'dans', 'sur', 'au', 'aux',
        'fi', 'ala', 'men', 'ana', 'enta', 'houwa', 'hiya', '3la', 'kima', 'el', 'li', 'rah', 'rak',
        'top', 'good', 'best', 'magnifique', 'excellent', 'restaurant', 'food', 'service', 'place'
    }
    
    # Filter stopwords and short words
    filtered_words = [w for w in words if w not in stopwords and len(w) > 2 and not w.isdigit()]
    
    count = Counter(filtered_words)
    common = count.most_common(60)
    
    return [{"text": word, "value": freq} for word, freq in common]

@app.get("/api/ai/insights")
async def get_ai_insights(current_user: dict = Depends(get_current_user)):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    pos_len = len(df_user[df_user['feeling'] == 'positive'])
    return [
        {
            "id": 1,
            "type": "strategy",
            "title": "Leverage High Appreciation",
            "content": f"You have a strong base of {pos_len} positive reviews. Highlight these on your social media to attract new customers.",
            "impact": "High"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
