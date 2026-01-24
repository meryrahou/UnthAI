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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
# Use relative path as default or get from env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(BASE_DIR, "../data/FinalDataset.csv")

CSV_PATH = os.getenv("CSV_PATH", DEFAULT_CSV_PATH)
SECRET_KEY = os.getenv("SECRET_KEY", "unthai_super_secret_key")
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

from app.services.model_service import get_model_service

@app.on_event("startup")
async def startup_event():
    try:
        get_model_service()
    except Exception as e:
        print(f"Warning: Model could not be pre-loaded: {e}")

# --- Data Loading ---

# Track which restaurants are currently being processed by the BERT model
active_processing = set()

def get_restaurant_df(restaurant_name: str):
    # Check if a heavy model process is currently running for this restaurant
    if restaurant_name in active_processing:
        return None  # Signal that data is not ready yet
        
    # Removed in-memory cache to ensure dashboard always reflects latest disk data
    
    path = get_processed_path(restaurant_name)
    if not os.path.exists(path):
        # We don't trigger auto-refresh here to avoid blocking simple GET requests
        # Instead, we rely on the /api/process-data trigger
        return pd.DataFrame()
            
    df = pd.read_csv(path)
    df = df.fillna("")
    # Fix: Use 'mixed' format to handle 'Z' suffix and other variations
    df['date_dt_all'] = pd.to_datetime(df['date'], format='mixed', utc=True, errors='coerce')
    df = df.dropna(subset=['date_dt_all'])
    
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
    if df_user is None:
        raise HTTPException(status_code=202, detail="AI Analysis in progress...")
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
        {"name": "Positive", "value": pos_count, "color": "#10b981"},
        {"name": "Negative", "value": neg_count, "color": "#ef4444"},
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
        "pos_count": pos_count,
        "neg_count": neg_count,
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

@app.get("/api/process-data/stats")
async def get_process_stats(current_user: dict = Depends(get_current_user)):
    """Fast endpoint to get raw counts (platforms, posts, comments) from master CSV"""
    name = current_user["restaurant_name"]
    try:
        df_master = pd.read_csv(CSV_PATH)
        df_res = df_master[df_master['source_name'].str.lower() == name.lower()]
        
        if df_res.empty:
            return {"platforms": 0, "posts": 0, "comments": 0, "breakdown": {}}
            
        platforms = df_res['platform'].nunique()
        posts = df_res['post_id'].nunique()
        comments = len(df_res)
        platform_counts = df_res['platform'].value_counts().to_dict()
        
        return {
            "platforms": int(platforms),
            "posts": int(posts),
            "comments": int(comments),
            "breakdown": platform_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-data")
async def process_data_endpoint(current_user: dict = Depends(get_current_user)):
    name = current_user["restaurant_name"]
    
    if name in active_processing:
        return {"status": "processing", "message": "Already processing"}
        
    try:
        active_processing.add(name)
        success = refresh_restaurant_data(name)
        
        if success:
            # Release lock immediately after model finishes so get_restaurant_df can read it
            if name in active_processing:
                active_processing.remove(name)
            
            # Fetch summary stats
            df = get_restaurant_df(name)
            if df is None:
                return {"status": "warning", "message": "Data still being finalized"}

            platforms = df['platform'].nunique()
            posts = df['post_id'].nunique()
            comments = len(df)
            platform_counts = df['platform'].value_counts().to_dict()
            
            return {
                "status": "success", 
                "message": "Data processed",
                "stats": {
                    "platforms": int(platforms),
                    "posts": int(posts),
                    "comments": int(comments),
                    "breakdown": platform_counts
                }
            }
        else:
            return {"status": "warning", "message": "No data found for this restaurant"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Note: lock removal now handled inside success block to allow immediate summary fetch
        pass

@app.get("/api/posts")
async def get_posts(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    if df_user is None:
        raise HTTPException(status_code=202, detail="AI Analysis in progress...")
    
    d_df = df_user.copy()
    if 'date_dt' not in d_df.columns:
         d_df['date_dt'] = pd.to_datetime(d_df['date'], errors='coerce', utc=True)
    
    # Drop rows with invalid dates to prevent issues
    d_df = d_df.dropna(subset=['date_dt'])
    
    print(f"DEBUG: Total rows for {current_user['restaurant_name']}: {len(df_user)}")
    print(f"DEBUG: Start Date: {start_date}, End Date: {end_date}")

    if start_date and end_date and start_date != "" and end_date != "":
        try:
            s_dt = pd.to_datetime(start_date, utc=True)
            e_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)
            d_df = d_df[(d_df['date_dt'] >= s_dt) & (d_df['date_dt'] < e_dt)]
            print(f"DEBUG: Rows after date filter: {len(d_df)}")
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
            "content": total_p,
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
    if df_user is None:
        raise HTTPException(status_code=202, detail="AI Analysis in progress...")
    
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
            
        # Determine sentiment type and main category with priority
        c_type = "neutral"
        main_cat = "General"
        
        # --- NEW PRIORITY FOR FLAGGING ---
        # 1. Actionable (Inquiry / Recommendation)
        # 2. Positive (Appreciation)
        # 3. Negative (Complaint)
        
        # Data preparation
        preds_str = str(preds).lower()
        has_inq = any('inquiry' in str(p).lower() for p in preds) or "?" in str(row.get('comment_text', ''))
        has_rec = any('recommendation' in str(p).lower() for p in preds)
        has_appreciation = any('_appreciation' in str(p).lower() or '_positive' in str(p).lower() for p in preds) or str(row.get('feeling', '')).lower() == 'positive'
        has_complaint = any('_complaint' in str(p).lower() or '_negative' in str(p).lower() for p in preds)
        has_out_of_scope = any('out_of_scope' in str(p).lower() for p in preds) or str(row.get('out_of_scope', '')).lower() in ['true', '1', 'yes']

        if has_inq:
            c_type = "inquiry"
        elif has_rec:
            c_type = "recommendation"
        elif has_appreciation:
            c_type = "appreciation"
        elif has_complaint:
            c_type = "complaint"
        elif has_out_of_scope:
            c_type = "out_of_scope"

        # Determine Main Category (Link it to the flagged type if possible)
        if has_complaint and not (has_inq or has_rec or has_appreciation):
            for p in preds:
                if '_complaint' in str(p).lower() or '_negative' in str(p).lower():
                    main_cat = str(p).split('_')[0].capitalize()
                    break
        elif preds:
            main_cat = str(preds[0]).split('_')[0].capitalize()
        
        # Sync with raw columns if model predictions are missing
        for cat_col in ['food', 'service', 'place', 'delivery', 'price', 'treatment']:
            val = str(row.get(cat_col, '')).lower()
            if val == 'complaint' and c_type != 'out_of_scope':
                c_type = "complaint"
                if main_cat == "General": main_cat = cat_col.capitalize()
            elif val == 'recommendation' and c_type in ['neutral', 'appreciation']:
                c_type = "recommendation"
                if main_cat == "General": main_cat = cat_col.capitalize()
            elif val == 'inquiry' and c_type in ['neutral', 'appreciation']:
                c_type = "inquiry"
                if main_cat == "General": main_cat = cat_col.capitalize()
            elif val == 'appreciation' and c_type == 'neutral':
                c_type = "appreciation"
                if main_cat == "General": main_cat = cat_col.capitalize()

        comments.append({
            "text": str(row.get('comment_text', 'No content')),
            "type": c_type,
            "category": main_cat,
            "time": str(row.get('date', 'Recent'))[:10],
            "likesCount": int(row['likesCount']) if 'likesCount' in cols and pd.notnull(row['likesCount']) else 0,
            "predictions": preds
        })
    
    # Sort comments by likesCount descending
    comments.sort(key=lambda x: x.get('likesCount', 0), reverse=True)
    
    return comments

@app.get("/api/trends")
async def get_trends(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    if df_user is None:
        raise HTTPException(status_code=202, detail="AI Analysis in progress...")
    
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
    
    # Custom Stopword List (English, French, basic Arabic/Chat)
    stopwords = {
        'the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'for', 'with', 'on', 'was', 'very',
        'le', 'la', 'les', 'et', 'de', 'du', 'des', 'un', 'une', 'est', 'c', 'ce', 'que', 'qui', 
        'pas', 'tres', 'très', 'bon', 'bien', 'avec', 'pour', 'dans', 'sur', 'au', 'aux',
        'fi', 'ala', 'men', 'ana', 'enta', 'houwa', 'hiya', '3la', 'kima', 'el', 'li', 'rah', 'rak',
        'top', 'good', 'best', 'magnifique', 'excellent', 'restaurant', 'food', 'service', 'place'
    }
    
    import re
    from collections import Counter
    
    # Calculate sentiment per word
    word_sentiments = {} # {word: {'pos': 0, 'neg': 0, 'neu': 0}}
    all_words = []
    
    # Iterate through rows to associate words with comment feeling
    for _, row in d_df.iterrows():
        sentiment = str(row.get('feeling', 'neutral')).lower()
        if sentiment not in ['positive', 'negative', 'neutral']: sentiment = 'neutral'
        
        comment_text = str(row.get('comment_text', '')).lower()
        row_words = re.findall(r'[\w\u0600-\u06FF]+', comment_text)
        
        seen_in_row = set() # Avoid double counting sentiment for same word in one comment
        for w in row_words:
            if w in stopwords or len(w) <= 2 or w.isdigit(): continue
            
            # Add to all_words for frequency counting
            all_words.append(w)
            
            if w in seen_in_row: continue
            
            seen_in_row.add(w)
            if w not in word_sentiments:
                word_sentiments[w] = {'positive': 0, 'negative': 0, 'neutral': 0}
            word_sentiments[w][sentiment] += 1

    count = Counter(all_words)
    common = count.most_common(60)
    
    result = []
    for word, freq in common:
        sents = word_sentiments.get(word, {'positive': 0, 'negative': 0, 'neutral': 0})
        # Determine dominant sentiment
        dom_sentiment = 'neutral'
        if sents['positive'] > sents['negative'] and sents['positive'] > sents['neutral']:
            dom_sentiment = 'positive'
        elif sents['negative'] > sents['positive'] and sents['negative'] > sents['neutral']:
            dom_sentiment = 'negative'
            
        result.append({"text": word, "value": freq, "sentiment": dom_sentiment})
        
    return result

@app.get("/api/actions")
async def get_actions(trend_period: str = "monthly", current_user: dict = Depends(get_current_user)):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    if df_user is None:
        raise HTTPException(status_code=202, detail="AI Analysis in progress...")
    
    # Filter out out_of_scope
    df_user = df_user[df_user['out_of_scope'].astype(str).str.lower() != 'true']
    
    actions = []
    action_id = 1
    
    # Parse dates for trend analysis
    df_user['date_dt'] = pd.to_datetime(df_user['date'], format='mixed', utc=True, errors='coerce')
    df_user = df_user.dropna(subset=['date_dt'])
    
    now = pd.Timestamp.now(tz='UTC')
    
    # Define timeframes based on user choice
    days_map = {
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90
    }
    days = days_map.get(trend_period, 7)
    
    current_period_start = now - pd.Timedelta(days=days)
    previous_period_start = now - pd.Timedelta(days=days*2)
    
    # These variables are used for TREND detection
    this_period = df_user[df_user['date_dt'] >= current_period_start]
    last_period = df_user[(df_user['date_dt'] >= previous_period_start) & (df_user['date_dt'] < current_period_start)]
    
    # Week variables for Complaint/Recency logic (kept fixed to maintain standard 'recent' definition)
    week_ago = now - pd.Timedelta(days=7)
    two_weeks_ago = now - pd.Timedelta(days=14)
    
    # 1. COMPLAINT CLUSTERS
    complaints = df_user[df_user['feeling'] == 'negative'].copy()
    
    # Define complaint keywords to cluster
    complaint_keywords = {
        'slow service': ['slow', 'wait', 'long', 'attente', 'lent', 'tawel', 'itawel', 'itawlo', 'ثقال', 'ساعة', 'heure', 'retard', 'itawelo', 'temps d\'attente', 'attends plus d\'une heure', 'متربونديوش', 'ما يريبونديوش'],
        'cold food': ['cold', 'froid', 'froide', 'bared', 'بارد', 'ماشي سخون', 'pas chaud'],
        'rude staff': ['rude staff', 'le serveur', 'impolite', 'mal parlé', 'malhonnête', 'pas professionnel', 'pas du tout professionnel', 'mauvais accueil', 'accueil froid', 'disorganized', 'متكبر', 'arrogant', 'منفخ', 'pas de respect', 'محقور', 'متكبر'],
        'dirty place': ['dirty', 'sale', 'hygiène', 'toilettes', 'وسخ', 'cleaning', 'ventilation', 'aérer', 'نظافة', 'مهمش', 'poussière'],
        'high prices': ['expensive', 'cher', 'costly', 'prix', 'غالي', 'غالية', 'غلا', 'prices', 'abusé', 'دولار', 'euro', 'cherol', 'السعر', 'سومة', 'ثمن', 'غالي بزاف', 'les prix', 'li bri', 'tarifs'],
        'small portions': ['small', 'portion', 'petite', 'minuscule', 'sghir', 'سغير', 'صغير', 'peu', 'little', 'فارغ', 'قليل', 'ما يشبعش'],
        'taste issue': ['pas bon', 'pas de goût', 'البنة 0', 'tasteless', 'ماشي بنين', 'بلا بنة', 'salé', 'cramé', 'burnt', 'normal', '0000', 'خردة', 'ما عجبنيش', 'خسر', 'بدل الماكلة']
    }
    
    for issue, keywords in complaint_keywords.items():
        # Find all complaints matching keywords
        mask = complaints['comment_text'].str.lower().str.contains('|'.join(keywords), na=False, regex=True)
        all_matches = complaints[mask]
        
        if not all_matches.empty:
            # Group by Year-Month to separate distinct timeframes
            # We sort descending so newest actions usually get processed first (though ID order matters less)
            all_matches = all_matches.sort_values('date_dt', ascending=False)
            
            for period, issue_complaints in all_matches.groupby(all_matches['date_dt'].dt.to_period('M')):
                if len(issue_complaints) >= 3:
                    # Smarter samples: find the relevant sentence/segment
                    samples = []
                    for _, row in issue_complaints.head(5).iterrows():
                        text = str(row['comment_text'])
                        # Find which keyword was hit
                        hit = next((k for k in keywords if k in text.lower()), None)
                        if hit:
                            # Extract ultra-tight window (~40 chars total)
                            idx = text.lower().find(hit)
                            start = max(0, idx - 15)
                            end = min(len(text), idx + 25)
                            snippet = text[start:end].strip()
                            if start > 0: snippet = "..." + snippet
                            if end < len(text): snippet = snippet + "..."
                            samples.append(snippet)
                        else:
                            samples.append(text[:40] + "...")
                    
                    # Get platforms
                    platforms = issue_complaints['platform'].unique().tolist()
                    platforms = [p.capitalize() if p != 'googlemaps' else 'Maps' for p in platforms]
                    
                    # Trend calc (only relevant if this is a recent bucket)
                    this_week_count = len(issue_complaints[issue_complaints['date_dt'] >= week_ago])
                    last_week_count = len(issue_complaints[(issue_complaints['date_dt'] >= two_weeks_ago) & (issue_complaints['date_dt'] < week_ago)])
                    
                    trend = None
                    if last_week_count > 0:
                        trend = int(((this_week_count - last_week_count) / last_week_count) * 100)
                    
                    # Smarter priority: based on total volume + trend + recency
                    total_count = len(issue_complaints)
                    recent_count = len(issue_complaints[issue_complaints['date_dt'] >= (now - pd.Timedelta(days=30))])
                    
                    # Base priority on total volume in this period
                    if total_count >= 10:
                        priority = 'high'
                    elif total_count >= 5:
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    # Bump up if trending upward (only applies to current month)
                    if trend and trend >= 50:
                        priority = 'high'
                    
                    # Downgrade if no recent activity (handles old monthly buckets)
                    if recent_count == 0:
                        priority = 'low'
                    
                    # Calculate exact timeframe for this bucket
                    # Note: For strict monthly buckets, days_ago will be the start of that complaint set
                    oldest_date = issue_complaints['date_dt'].min()
                    days_ago = (now - oldest_date).days
                    
                    # Format for frontend translation
                    topic_key = {
                        'slow service': 'slowService',
                        'cold food': 'coldFood',
                        'rude staff': 'rudeStaff',
                        'dirty place': 'dirtyPlace',
                        'high prices': 'highPrices',
                        'small portions': 'smallPortions',
                        'taste issue': 'food'
                    }.get(issue, 'general')

                    actions.append({
                        'id': action_id,
                        'type': 'complaints',
                        'priority': priority,
                        'titleKey': 'complaintsTitle',
                        'topicKey': f'pillers.{topic_key}',
                        'descKey': 'xMentionsCustomers',
                        'count': len(issue_complaints),
                        'timeframeType': 'lastDays' if days_ago > 0 else 'today',
                        'timeframeDays': days_ago,
                        'platforms': platforms[:3],
                        'samples': samples,
                        'trend': trend,
                        'status': 'pending'
                    })
                    action_id += 1
    
    # 2. UNANSWERED INQUIRIES (Grouped by Theme)
    inquiries = df_user[
        (df_user['comment_text'].str.contains(r'\?', na=False, regex=True)) |
        (df_user.apply(lambda row: any('inquiry' in str(p).lower() for p in eval(str(row.get('model_prediction', '[]')))), axis=1))
    ].copy()
    
    # Prioritized processing to prevent overlap
    # We process Contact first, then remove those rows from the pool
    processed_indices = []
    
    # Order matters: Contact first to catch phone requests before they get stuck in other buckets
    ordered_themes = [
        ('Contact & Info', ['numéro', 'téléphone', 'نمرو', 'رقم', 'call', 'contact', 'whatsapp']),
        ('Price', ['price', 'prix', 'combien', 'how much', 'cost', 'menu', 'بشحال', 'السعر', 'list', 'سومة', 'قداش', 'tarif']),
        ('Hours & Opening', ['opening', 'hours', 'horaire', 'ouvert', 'open', 'time', 'ferme', 'وقت', 'ساعة', 'available', 'dispo', 'يفتح', 'thel', 'tebda', 'فتحتها']),
        ('Delivery & Prep', ['delivery', 'livraison', 'توصيل', 'order', 'prepar', 'ready', 'booking', 'réservation', 'ليفرزون', 'كاين توصيل']),
        ('Location', ['where', 'location', 'place', 'adresse', 'maps', 'وين', 'بلاصة', 'فين', 'directions', 'c est où', 'win jay', 'أين', 'بلايص'])
    ]
    
    for theme, keywords in ordered_themes:
        # Filter out already processed rows
        remaining_inquiries = inquiries.drop(processed_indices, errors='ignore')
        
        mask = remaining_inquiries['comment_text'].str.lower().str.contains('|'.join(keywords), na=False, regex=True)
        theme_inquiries = remaining_inquiries[mask]
        
        # Mark these as processed
        processed_indices.extend(theme_inquiries.index.tolist())
        
        if len(theme_inquiries) >= 2: # Lower threshold to 2 for inquiries
            platforms = theme_inquiries['platform'].unique().tolist()
            platforms = [p.capitalize() if p != 'googlemaps' else 'Maps' for p in platforms]
            
            # Simple snippets for inquiries (the question itself)
            samples = []
            for _, row in theme_inquiries.head(3).iterrows():
                text = str(row['comment_text'])
                samples.append(text[:40] + "..." if len(text) > 40 else text)

            oldest_date = theme_inquiries['date_dt'].min()
            days_ago = (now - oldest_date).days
            timeframe = f"Last {days_ago} days" if days_ago > 0 else "Today"

            topic_key = {
                'Price': 'price',
                'Hours & Opening': 'hours',
                'Delivery & Prep': 'delivery',
                'Location': 'location',
                'Contact & Info': 'general'
            }.get(theme, 'general')

            priority = 'high' if len(theme_inquiries) >= 10 else 'medium' if len(theme_inquiries) >= 5 else 'low'

            actions.append({
                'id': action_id,
                'type': 'inquiries',
                'priority': priority,
                'titleKey': 'questionsTitle',
                'topicKey': f'pillers.{topic_key}',
                'descKey': 'xQuestionsCustomers',
                'count': len(theme_inquiries),
                'timeframeType': 'lastDays' if days_ago > 0 else 'today',
                'timeframeDays': days_ago,
                'platforms': platforms[:3],
                'samples': samples,
                'trend': None,
                'status': 'pending'
            })
            action_id += 1
    
    # 3. TRENDING ISSUES (Dynamic Period)
    categories = ['food', 'service', 'place', 'delivery', 'price', 'treatment']
    
    for cat in categories:
        this_period_neg = len(this_period[this_period[cat].astype(str).str.lower() == 'complaint'])
        last_period_neg = len(last_period[last_period[cat].astype(str).str.lower() == 'complaint'])
        
        # Surface if there is ANY increase, even from 0
        if this_period_neg > last_period_neg:
            trend_pct = 0
            if last_period_neg > 0:
                trend_pct = int(((this_period_neg - last_period_neg) / last_period_neg) * 100)
            else:
                trend_pct = 100 # New issue in this period
            
            if trend_pct >= 20 or this_period_neg >= 2: 
                samples = this_period[this_period[cat].astype(str).str.lower() == 'complaint']['comment_text'].head(3).tolist()
                
                actions.append({
                    'id': action_id,
                    'type': 'trends',
                    'priority': 'high' if trend_pct >= 40 else 'medium',
                    'titleKey': 'issuesIncreasingTitle',
                    'topicKey': f'pillers.{cat}',
                    'descKey': 'increasingIssuesDesc',
                    'count': this_period_neg,
                    'timeframeType': {
                        'weekly': 'thisWeek',
                        'monthly': 'thisMonth',
                        'quarterly': 'thisQuarter'
                    }.get(trend_period, 'thisWeek'),
                    'platforms': [],
                    'samples': [s[:80] + "..." for s in samples],
                    'trend': trend_pct,
                    'status': 'pending'
                })
                action_id += 1
    
    # 4. QUICK WINS (More Broad Recommendations)
    recommendations = df_user[
        df_user.apply(lambda row: any('recommendation' in str(p).lower() for p in eval(str(row.get('model_prediction', '[]')))), axis=1)
    ].copy()
    
    if len(recommendations) >= 1:
        rec_themes = {
            'Menu Variety': ['add', 'more', 'option', 'vegan', 'vegetarian', 'choice', 'new', 'زيدو', 'كثرو', 'développer', 'varier', 'sauce', 'minuscule', 'meat', 'viande', 'poulet', 'plus de choix', 'épices'],
            'Service & Staff': ['faster', 'speed', 'wait', 'time', 'quicker', 'نظمو', 'خفو', 'rapide', 'organisation', 'serveur', 'patience', 'accueil', 'staff', 'bannir', 'متكبر'],
            'Facility & Decor': ['clean', 'space', 'decor', 'parking', 'music', 'wifi', 'نقو', 'وسع', 'climatisation', 'ventilation', 'toilette', 'مصلى', 'handicapés', 'chaises', 'table', 'propre', 'hygiène'],
            'Pricing & Info': ['prix', 'tarif', 'adresse', 'localisation', 'نعت', 'وين', 'سعر', 'سومة', 'ثمن', 'details', 'promotions', 'menu', 'carte'],
            'General Feedback': [''] # Catch all
        }

        matched_indices = set()
        for theme, keywords in rec_themes.items():
            if theme == 'General Feedback':
                # Only include what hasn't been matched yet
                theme_recs = recommendations[~recommendations.index.isin(matched_indices)]
            else:
                mask = recommendations['comment_text'].str.lower().str.contains('|'.join(keywords), na=False, regex=True)
                theme_recs = recommendations[mask]
                matched_indices.update(theme_recs.index.tolist())
            
            if len(theme_recs) >= 1:
                samples = [s[:40] + "..." for s in theme_recs['comment_text'].head(3).tolist()]
                
                topic_key = {
                    'Menu Variety': 'menuVariety',
                    'Service & Staff': 'serviceSpeed',
                    'Facility & Decor': 'facility',
                    'Pricing & Info': 'price',
                    'General Feedback': 'general'
                }.get(theme, 'general')

                actions.append({
                    'id': action_id,
                    'type': 'recommendations',
                    'priority': 'low',
                    'titleKey': 'improveTitle',
                    'topicKey': f'pillers.{topic_key}',
                    'descKey': 'suggestImprovementsDesc',
                    'count': len(theme_recs),
                    'timeframeType': 'recurring',
                    'platforms': [],
                    'samples': samples,
                    'trend': None,
                    'status': 'pending'
                })
                action_id += 1
    
    # Calculate stats
    stats = {
        'total': len(actions),
        'urgent': len([a for a in actions if a['priority'] == 'high']),
        'completed': 0  # Would track this in a real DB
    }
    
    # Sort cards by priority (high -> medium -> low)
    priority_map = {"high": 0, "medium": 1, "low": 2}
    actions.sort(key=lambda x: priority_map.get(x.get('priority', 'low'), 2))
    
    return {
        "actions": actions, 
        "stats": stats,
        "restaurant_name": current_user["restaurant_name"]
    }
@app.get("/api/ai/insights")
async def get_ai_insights(current_user: dict = Depends(get_current_user)):
    df_user = get_restaurant_df(current_user["restaurant_name"])
    if df_user is None:
        raise HTTPException(status_code=202, detail="AI Analysis in progress...")
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

class PredictRequest(BaseModel):
    comment: str

@app.post("/api/lab/predict")
async def lab_predict(request: PredictRequest, current_user: dict = Depends(get_current_user)):
    try:
        model_service = get_model_service()
        # Clean text
        import re
        clean_comment = re.sub(r'\s*\[(COMPLAINT|INQUIRY|APPRECIATION|RECOMMENDATION|OUT_OF_SCOPE)\]\s*$', '', request.comment, flags=re.IGNORECASE)
        
        # Predict with optimized threshold
        preds = model_service.predict_batch([clean_comment], threshold=0.8)[0]
        
        # Map to platform labels
        intents = model_service.map_to_platform_labels(preds)
        feeling = model_service.get_feeling(preds)
        
        # Structure the response for the "Pretty" UI
        # intents is a list like ["food_appreciation", "service_complaint"]
        formatted_intents = []
        for intent in intents:
            parts = intent.split('_')
            pillar = parts[0].capitalize()
            type_label = parts[1].capitalize() if len(parts) > 1 else "Unknown"
            formatted_intents.append({
                "pillar": pillar,
                "type": type_label,
                "raw": intent
            })

        return {
            "feeling": feeling,
            "intents": formatted_intents,
            "raw_predictions": preds
        }
    except Exception as e:
        print(f"Lab prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
