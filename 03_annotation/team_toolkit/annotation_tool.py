import os
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import argparse

# --- Constant Definitions ---
CATEGORY_MAP = {
    'price': 'Price',
    'treatment': 'Treatment (personnel)',
    'food': 'Food',
    'service': 'Service (waiting time)',
    'place': 'Place (propreté)',
    'delivery': 'Delivery'
}
INTENTS = ['None', 'Appreciation', 'Complaint', 'Inquiry', 'Recommendation']

# --- Configuration ---
parser = argparse.ArgumentParser()
parser.add_argument("file", help="The CSV file to annotate")
parser.add_argument("--master", help="Optional: master CSV file to sync with immediately")
args = parser.parse_args()

PART_NAME = args.file
PART_FILE = PART_NAME
MASTER_FILE = args.master
AI_FILE = PART_NAME.replace(".csv", "_ai.csv")

# Load Data
if not os.path.exists(PART_FILE):
    print(f"❌ Error: File {PART_FILE} not found.")
    exit()

df = pd.read_csv(PART_FILE, keep_default_na=False)

# Ensure columns exist and are string type to avoid warnings
for col in CATEGORY_MAP.keys():
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].astype(str)

if 'out_of_scope' not in df.columns:
    df['out_of_scope'] = ""
df['out_of_scope'] = df['out_of_scope'].astype(str)

# Load AI Predictions if they exist
ai_data = {}
if os.path.exists(AI_FILE):
    try:
        # keep_default_na=False prevents "None" from becoming NaN
        ai_df_raw = pd.read_csv(AI_FILE, keep_default_na=False)
        ai_df_raw['comment_id'] = ai_df_raw['comment_id'].astype(int)
        ai_data = ai_df_raw.set_index('comment_id').to_dict('index')
        print(f"✅ Loaded {len(ai_data)} AI suggestions.")
    except Exception as e:
        print(f"⚠️ Could not load AI file: {e}")

app = FastAPI()

# In-memory session state for skipped indices
skipped_indices = set()

def get_next_index():
    labeled = df['out_of_scope'].isin(['True', 'False', True, False])
    # Filter out both labeled rows and indices skipped in this session
    unlabeled_mask = ~labeled & ~df.index.isin(skipped_indices)
    next_idx = df[unlabeled_mask].index.min()
    return next_idx if not pd.isna(next_idx) else None

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, index: int = None):
    if index is None:
        index = get_next_index()
        if index is None:
            return "🎉 Mission Accomplished! All comments are labeled. You can close this tool."

    row = df.iloc[index]
    c_id = int(row['comment_id'])
    text = row['comment_text']
    total = len(df)
    labeled_count = len(df[df['out_of_scope'].isin(['True', 'False', True, False])])
    progress = (labeled_count / total) * 100

    ai_sugg = ai_data.get(c_id, {})
    ai_oos = str(ai_sugg.get('ai_out_of_scope', '')).lower() == 'true'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UnthAI TEAM Tool</title>
        <style>
            body {{ background: #0d1117; color: #c9d1d9; font-family: -apple-system, system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; }}
            .container {{ width: 900px; background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            .progress-bar {{ width: 100%; height: 8px; background: #30363d; border-radius: 4px; margin-bottom: 20px; position: relative; overflow: hidden; }}
            .progress-fill {{ height: 100%; background: linear-gradient(90deg, #bb86fc, #03dac6); width: {progress}%; }}
            .comment-box {{ background: #0d1117; border-left: 4px solid #bb86fc; padding: 20px; margin-bottom: 25px; border-radius: 4px; font-size: 1.2em; line-height: 1.6; position: relative; }}
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
            .category {{ background: #21262d; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }}
            .category h3 {{ margin: 0 0 12px 0; font-size: 0.8em; color: #bb86fc; text-transform: uppercase; letter-spacing: 1px; }}
            .option {{ padding: 0; margin: 8px 0; cursor: pointer; border-radius: 4px; transition: background 0.2s; display: flex; align-items: stretch; }}
            .option:hover {{ background: #30363d; }}
            .option label {{ display: flex; align-items: center; width: 100%; padding: 10px 12px; cursor: pointer; font-size: 0.9em; }}
            input[type="radio"] {{ margin-right: 12px; accent-color: #03dac6; scale: 1.2; cursor: pointer; }}
            .appreciation {{ color: #00e676; }} .complaint {{ color: #ff5252; }} .inquiry {{ color: #40c4ff; }} .recommendation {{ color: #e040fb; }}
            .footer {{ margin-top: 25px; display: flex; justify-content: space-between; align-items: center; }}
            button {{ background: linear-gradient(135deg, #bb86fc, #03dac6); border: none; padding: 12px 30px; border-radius: 20px; font-weight: 800; cursor: pointer; }}
            
            /* AI Rainbow Border - High Contrast */
            .ai-suggested {{
                position: relative;
                border: 2px solid transparent !important;
                background-clip: padding-box, border-box !important;
                background-origin: padding-box, border-box !important;
                background-image: linear-gradient(#161b22, #161b22), 
                                  linear-gradient(45deg, #ff0000, #ffea00, #00ff00, #00eaff, #ff00ff, #ff0000) !important;
                border-radius: 8px !important;
                z-index: 1;
                box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
            }}
            .shortcut-hint {{ font-size: 0.7em; color: #8b949e; margin-top: 5px; font-style: italic; }}
        </style>
        <script>
            document.addEventListener('keydown', function(e) {{
                if (e.key.toLowerCase() === 's') {{
                    const suggestions = document.querySelectorAll('.ai-suggested input');
                    if (suggestions.length > 0) {{
                        suggestions.forEach(input => input.checked = true);
                        setTimeout(() => {{ document.querySelector('form').submit(); }}, 150);
                    }}
                }}
                if (e.key.toLowerCase() === 'd') {{
                    document.querySelector('form').submit();
                }}
                if (e.key.toLowerCase() === 'k') {{
                    window.location.href = '/skip?index={index}';
                }}
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <div class="progress-bar"><div class="progress-fill"></div></div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; margin-bottom: 15px;">
                <span>PART: {PART_NAME} | {labeled_count}/{total} LABELED</span>
                <span>{progress:.1f}%</span>
            </div>
            
            <div class="comment-box">
                <span style="font-size: 0.6em; color: #8b949e; position: absolute; top: 10px; left: 15px;"># {c_id}</span>
                {text}
                {f'<span style="background: #03dac6; color: #000; font-size: 0.6em; padding: 2px 5px; border-radius: 3px; position: absolute; top: 10px; right: 15px; font-weight: bold;">AI ASSISTED</span>' if ai_sugg else ''}
            </div>

            <form action="/save" method="post">
                <input type="hidden" name="index" value="{index}">
                <div class="grid">
                    {" ".join([f'''
                    <div class="category">
                        <h3>{label}</h3>
                        <div class="options">
                            {' '.join([f"""
                            <div class="option {'ai-suggested' if str(ai_sugg.get(f'ai_{cat}', '')).strip().lower() == intent.lower() else ''}">
                                <label class="{intent.lower()}">
                                    <input type="radio" name="{cat}" value="{intent}" id="{cat}_{intent}" 
                                        {"checked" if (row[cat] == intent) or (row[cat] in ["", "None", "nan"] and intent == "None") else ""}>
                                    {intent}
                                </label>
                            </div>
                            """ for intent in INTENTS])}
                        </div>
                    </div>
                    ''' for cat, label in CATEGORY_MAP.items()])}
                </div>

                <div class="footer">
                    <div class="nav-links">
                        <a href="/?index={index-1}" style="color: #8b949e; text-decoration: none;">← Previous</a> &nbsp;&nbsp;
                        <a href="/skip?index={index}" style="color: #8b949e; text-decoration: none;">Skip →</a>
                        <div class="shortcut-hint">
                            <b>S</b>: Accept AI + Save | <b>D</b>: Save & Next | <b>K</b>: Skip
                        </div>
                    </div>
                    <button type="submit">SAVE & NEXT (D)</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/save")
async def save_item(request: Request, index: int = Form(...)):
    form_data = await request.form()
    all_none = True
    for cat in CATEGORY_MAP.keys():
        val = form_data.get(cat, 'None')
        if val != 'None':
            all_none = False
            df.at[index, cat] = val
        else:
            df.at[index, cat] = "None" # Use explicit "None" string
            
    df.at[index, 'out_of_scope'] = "True" if all_none else "False"
    df.to_csv(PART_FILE, index=False)

    # --- Immediate Master Sync ---
    if MASTER_FILE and os.path.exists(MASTER_FILE):
        try:
            df_master = pd.read_csv(MASTER_FILE, keep_default_na=False)
            df_master.set_index('comment_id', inplace=True)
            
            row = df.iloc[index]
            c_id = int(row['comment_id'])
            
            # Map columns to update
            cols = ['food', 'service', 'place', 'delivery', 'price', 'treatment', 'out_of_scope']
            for col in cols:
                if c_id in df_master.index:
                    df_master.at[c_id, col] = df.at[index, col]
            
            df_master.reset_index(inplace=True)
            df_master.to_csv(MASTER_FILE, index=False)
            print(f"✅ Immediate Sync to Master: Comment {c_id}")
        except Exception as e:
            print(f"⚠️ Sync to Master failed: {e}")
    
    next_idx = get_next_index()
    return RedirectResponse(url=f"/?index={next_idx}" if next_idx is not None else "/", status_code=303)

@app.get("/skip")
async def skip_item(index: int):
    skipped_indices.add(index)
    print(f"⏭️ Skipped comment index {index} for this session.")
    next_idx = get_next_index()
    return RedirectResponse(url=f"/?index={next_idx}" if next_idx is not None else "/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
