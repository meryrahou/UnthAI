from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import pandas as pd
import os
import uvicorn

app = FastAPI()

import argparse

# Setup CLI arguments
parser = argparse.ArgumentParser(description="UnthAI Annotation Tool")
parser.add_argument("file", nargs="?", default="annotation_part_1.csv", help="Name of the CSV file to annotate (inside 03_annotation/)")
args = parser.parse_args()

# Configuration
PART_NAME = args.file
PART_FILE = os.path.join("/Users/mery/GitHub/UnthAI/03_annotation", PART_NAME)
# Mapping for UI Display vs Dataset Column
CATEGORY_MAP = {
    'price': 'Price',
    'treatment': 'Treatment (personnel)',
    'food': 'Food',
    'service': 'Service (waiting time)',
    'place': 'Place (propreté)',
    'delivery': 'Delivery'
}
DISPLAY_ORDER = ['price', 'treatment', 'food', 'service', 'place', 'delivery']
OPTIONS = ['None', 'appreciation', 'complaint', 'inquiry', 'recommendation']

# Load data - Verify file exists
if not os.path.exists(PART_FILE):
    print(f"Error: File {PART_FILE} not found!")
    exit(1)

df = pd.read_csv(PART_FILE)
# Ensure columns exist and handle NaNs
for col in CATEGORY_MAP.keys():
    if col not in df.columns: df[col] = ""
    df[col] = df[col].astype(str).replace('nan', '')
if 'out_of_scope' not in df.columns: df['out_of_scope'] = ""
df['out_of_scope'] = df['out_of_scope'].astype(str).replace('nan', '')

def get_stats():
    # A row is labeled if out_of_scope is True or False
    labeled_mask = df['out_of_scope'].isin(['True', 'False'])
    total_labeled = labeled_mask.sum()
    total_rows = len(df)
    percent = round((total_labeled / total_rows) * 100, 1) if total_rows > 0 else 0
    return total_labeled, total_rows, percent

def get_next_index():
    labeled_mask = df['out_of_scope'].isin(['True', 'False'])
    unlabeled_indices = df.index[~labeled_mask].tolist()
    return unlabeled_indices[0] if unlabeled_indices else None

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, index: int = None):
    total_labeled, total_rows, percent = get_stats()
    
    if index is None:
        index = get_next_index()
    
    if index is None or index >= len(df):
        return f"""
        <html>
        <head>
            <title>Done!</title>
            <style>
                body {{ font-family: 'Inter', sans-serif; background: #121212; color: #e0e0e0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .card {{ background: #1e1e1e; padding: 50px; border-radius: 20px; text-align: center; border: 1px solid #bb86fc; }}
                h1 {{ color: #03dac6; font-size: 3em; margin-bottom: 0.5em; }}
                p {{ font-size: 1.2em; color: #aaa; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🎉 Mission Accomplished!</h1>
                <p>All {total_rows} comments in this partition have been labeled.</p>
                <p>You can now push your changes to the repository.</p>
            </div>
        </body>
        </html>
        """
    
    comment = df.iloc[index]
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UnthAI Annotation Tool</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
            body {{ font-family: 'Inter', sans-serif; background: #0f111a; color: #e0e6ed; margin: 0; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }}
            .container {{ width: 95%; max-width: 950px; padding: 15px; }}
            
            .stats-container {{ background: #161b22; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d; }}
            .stats-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.85em; font-weight: 700; color: #bb86fc; text-transform: uppercase; }}
            .progress-bg {{ background: #30363d; height: 6px; border-radius: 3px; overflow: hidden; }}
            .progress-fill {{ background: linear-gradient(90deg, #bb86fc, #03dac6); height: 100%; transition: width 0.6s ease; }}

            .card {{ background: #161b22; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 20px; border: 1px solid #30363d; border-left: 4px solid #bb86fc; }}
            .comment-header {{ font-size: 0.8em; color: #8b949e; margin-bottom: 10px; display: flex; justify-content: space-between; }}
            .comment-text {{ font-size: 1.2em; line-height: 1.4; font-weight: 500; color: #ffffff; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
            .section {{ background: #0d1117; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }}
            .section h3 {{ margin-top: 0; font-size: 0.75em; color: #bb86fc; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #333; padding-bottom: 6px; margin-bottom: 10px; }}
            .options {{ display: grid; gap: 4px; }}
            label {{ display: flex; align-items: center; gap: 10px; cursor: pointer; padding: 6px 10px; border-radius: 4px; transition: all 0.2s; font-size: 0.9em; }}
            label:hover {{ background: #21262d; }}
            input[type="radio"] {{ accent-color: #bb86fc; width: 16px; height: 16px; }}
            
            .appreciation {{ color: #00e676; }}
            .complaint {{ color: #ff5252; }}
            .inquiry {{ color: #40c4ff; }}
            .recommendation {{ color: #e040fb; }}
            .none {{ color: #8b949e; }}

            .footer {{ margin-top: 25px; display: flex; justify-content: space-between; align-items: center; width: 100%; }}
            button {{ background: linear-gradient(135deg, #bb86fc, #03dac6); border: none; padding: 15px 40px; border-radius: 30px; color: #000; font-weight: 800; font-size: 1.1em; cursor: pointer; box-shadow: 0 4px 15px rgba(187, 134, 252, 0.4); text-transform: uppercase; }}
            button:hover {{ transform: translateY(-2px); }}
            
            .nav-links a {{ color: #8b949e; text-decoration: none; font-size: 0.9em; }}
            .nav-links a:hover {{ color: #bb86fc; }}
            .status-badge {{ background: #21262d; padding: 4px 8px; border-radius: 4px; font-size: 0.7em; font-weight: 800; border: 1px solid #30363d; }}
            .status-labeled {{ color: #00e676; border-color: #00e676; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="stats-container">
                <div class="stats-header">
                    <span>Part: {PART_NAME} | {total_labeled}/{total_rows} labeled</span>
                    <span>{percent}%</span>
                </div>
                <div class="progress-bg"><div class="progress-fill" style="width: {percent}%"></div></div>
            </div>

            <div class="card">
                <div class="comment-header">
                    <span># {comment.get('final_id', index+1)}</span>
                    <span class="status-badge {'status-labeled' if df.at[index, 'out_of_scope'] != '' else ''}">
                        {'LABELED' if df.at[index, 'out_of_scope'] != '' else 'PENDING'}
                    </span>
                </div>
                <div class="comment-text">{comment['comment_text']}</div>
            </div>
            
            <form action="/save" method="post">
                <input type="hidden" name="index" value="{index}">
                <div class="grid">
                    {"".join([f'''
                    <div class="section">
                        <h3>{CATEGORY_MAP[cat]}</h3>
                        <div class="options">
                            {"".join([f'''
                            <label class="{opt.lower()}">
                                <input type="radio" name="{cat}" value="{opt}" {'checked' if (df.at[index, cat] == opt or (df.at[index, cat] == "" and opt == "None")) else ''} required>
                                {opt.capitalize()}
                            </label>
                            ''' for opt in OPTIONS])}
                        </div>
                    </div>
                    ''' for cat in DISPLAY_ORDER])}
                </div>
                
                <div class="footer">
                    <div class="nav-links">
                        {"<a href='/?index=" + str(index-1) + "'>← Previous</a>" if index > 0 else "<span></span>"}
                        &nbsp;&nbsp;&nbsp;
                        <a href="/?index={index+1}">Skip →</a>
                    </div>
                    <button type="submit">Save & Next</button>
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
        val = form_data.get(cat)
        if val != 'None':
            all_none = False
            df.at[index, cat] = val
        else:
            df.at[index, cat] = ""
            
    df.at[index, 'out_of_scope'] = "True" if all_none else "False"
    df.to_csv(PART_FILE, index=False)
    
    # After saving, find the next unlabeled index
    next_idx = get_next_index()
    return RedirectResponse(url=f"/?index={next_idx}" if next_idx is not None else "/?index=" + str(len(df)), status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
