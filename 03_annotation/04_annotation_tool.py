from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import pandas as pd
import os
import uvicorn

app = FastAPI()

import argparse
import sys

# Setup CLI arguments
parser = argparse.ArgumentParser(description="UnthAI Annotation Tool")
parser.add_argument(
    "file",
    nargs="?",
    default="annotation_part_1.csv",
    help="Name of the CSV file to annotate (inside 03_annotation/)"
)
parser.add_argument(
    "--active-only",
    action="store_true",
    help="Only show comments where AI predicted at least one non-None intent"
)
parser.add_argument(
    "--master",
    help="Master CSV file to sync with immediately"
)
args = parser.parse_args()

# Get the filename or full path from argument
PART_NAME = args.file

# If a full path is provided, use it as is
if os.path.isabs(PART_NAME):
    PART_FILE = PART_NAME
else:
    # Otherwise, assume it’s in the same folder as this script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PART_FILE = os.path.join(SCRIPT_DIR, PART_NAME)

# Sanity check
if not os.path.exists(PART_FILE):
    print(f"Error: File {PART_FILE} not found!")
    sys.exit(1)

print(f"Using CSV file: {PART_FILE}")

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

df = pd.read_csv(PART_FILE, keep_default_na=False)
# Ensure columns exist and handle NaNs
for col in CATEGORY_MAP.keys():
    if col not in df.columns: df[col] = ""
    df[col] = df[col].astype(str)
if 'out_of_scope' not in df.columns: df['out_of_scope'] = ""
df['out_of_scope'] = df['out_of_scope'].astype(str)

# --- AI Logic ---
AI_FILE = PART_FILE.replace(".csv", "_ai.csv")
ai_data = {}
if os.path.exists(AI_FILE):
    try:
        ai_df_raw = pd.read_csv(AI_FILE, keep_default_na=False)
        ai_df_raw['comment_id'] = ai_df_raw['comment_id'].astype(int)
        ai_data = ai_df_raw.set_index('comment_id').to_dict('index')
        print(f"✅ Loaded {len(ai_data)} AI suggestions from {AI_FILE}")
    except Exception as e:
        print(f"⚠️ Could not load AI file: {e}")

skipped_indices = set()

def get_stats():
    # A row is labeled if out_of_scope is True or False
    labeled_mask = df['out_of_scope'].isin(['True', 'False'])
    total_labeled = labeled_mask.sum()
    total_rows = len(df)
    percent = round((total_labeled / total_rows) * 100, 1) if total_rows > 0 else 0
    return total_labeled, total_rows, percent

def get_next_index():
    # 1. Base filter: Not human labeled and not skipped in this session
    labeled_mask = df['out_of_scope'].isin(['True', 'False', True, False])
    unlabeled_mask = ~labeled_mask & ~df.index.isin(skipped_indices)
    
    # 2. Active filter (optional): AI must have predicted something
    if args.active_only:
        # Get indices of comments with at least one active AI prediction
        active_ids = []
        for c_id, preds in ai_data.items():
            is_active = any(str(preds.get(f"ai_{cat}", "")).lower() != "none" for cat in CATEGORY_MAP.keys())
            if is_active:
                active_ids.append(c_id)
        
        # Filter unlabeled by these IDs
        unlabeled_mask = unlabeled_mask & df['comment_id'].isin(active_ids)
        
    next_idx = df[unlabeled_mask].index.min()
    return next_idx if not pd.isna(next_idx) else None

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
    c_id = int(comment['comment_id'])
    print(f"👀 Now viewing Comment ID: {c_id}")
    ai_sugg = ai_data.get(c_id, {})
    
    # Pre-build sections HTML to avoid nested f-string issues
    sections_html = ""
    for cat in DISPLAY_ORDER:
        options_html = ""
        ai_val = str(ai_sugg.get(f"ai_{cat}", "")).strip().lower()
        
        for opt in OPTIONS:
            is_ai = ai_val == opt.lower()
            current_vals = df.at[index, cat].split(",") if df.at[index, cat] else []
            # Check if this option is currently selected
            is_checked = (opt in current_vals) or (not current_vals and opt == "None")
            
            options_html += f'''
                <label class="{opt.lower()} {'ai-suggested' if is_ai else ''}">
                    <input type="checkbox" name="{cat}[]" value="{opt}" {'checked' if is_checked else ''}>
                    {opt.capitalize()}
                </label>
            '''
            
        sections_html += f'''
            <div class="section">
                <h3>{CATEGORY_MAP[cat]}</h3>
                <div class="options">
                    {options_html}
                </div>
            </div>
        '''

    has_ai = "inline-block" if c_id in ai_data else "none"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UnthAI Multilabel Tool</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
            body {{ font-family: 'Inter', sans-serif; background: #0f111a; color: #e0e6ed; margin: 0; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }}
            .container {{ width: 95%; max-width: 950px; padding: 15px; }}
            
            .stats-container {{ background: #161b22; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d; }}
            .stats-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.85em; font-weight: 700; color: #bb86fc; text-transform: uppercase; }}
            .progress-bg {{ background: #30363d; height: 6px; border-radius: 3px; overflow: hidden; }}
            .progress-fill {{ background: linear-gradient(90deg, #bb86fc, #03dac6); height: 100%; transition: width 0.6s ease; }}

            .card {{ background: #161b22; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 20px; border: 1px solid #30363d; border-left: 4px solid #bb86fc; }}
            .comment-header {{ font-size: 0.8em; color: #8b949e; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
            .comment-text {{ font-size: 1.2em; line-height: 1.4; font-weight: 500; color: #ffffff; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
            .section {{ background: #0d1117; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }}
            .section h3 {{ margin-top: 0; font-size: 0.75em; color: #bb86fc; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #333; padding-bottom: 6px; margin-bottom: 10px; }}
            .options {{ display: grid; gap: 4px; }}
            label {{ display: flex; align-items: center; gap: 10px; cursor: pointer; padding: 6px 10px; border-radius: 4px; transition: all 0.2s; font-size: 0.9em; }}
            label:hover {{ background: #21262d; }}
            input[type="checkbox"] {{ accent-color: #03dac6; width: 16px; height: 16px; cursor: pointer; }}
            
            .appreciation {{ color: #00e676; }}
            .complaint {{ color: #ff5252; }}
            .inquiry {{ color: #40c4ff; }}
            .recommendation {{ color: #e040fb; }}
            .none {{ color: #8b949e; }}

            /* AI Rainbow Border */
            .ai-suggested {{
                position: relative;
                border: 2px solid transparent !important;
                background-clip: padding-box, border-box !important;
                background-origin: padding-box, border-box !important;
                background-image: linear-gradient(#0d1117, #0d1117), 
                                  linear-gradient(45deg, #ff0000, #ffea00, #00ff00, #00eaff, #ff00ff, #ff0000) !important;
                border-radius: 4px !important;
                z-index: 1;
            }}

            .footer {{ margin-top: 25px; display: flex; justify-content: space-between; align-items: center; width: 100%; }}
            button {{ background: linear-gradient(135deg, #bb86fc, #03dac6); border: none; padding: 15px 40px; border-radius: 30px; color: #000; font-weight: 800; font-size: 1.1em; cursor: pointer; box-shadow: 0 4px 15px rgba(187, 134, 252, 0.4); text-transform: uppercase; }}
            button:hover {{ transform: translateY(-2px); }}
            
            .nav-links {{ display: flex; flex-direction: column; gap: 5px; }}
            .nav-links a {{ color: #8b949e; text-decoration: none; font-size: 0.9em; }}
            .nav-links a:hover {{ color: #bb86fc; }}
            .status-badge {{ background: #21262d; padding: 4px 8px; border-radius: 4px; font-size: 0.7em; font-weight: 800; border: 1px solid #30363d; }}
            .status-labeled {{ color: #00e676; border-color: #00e676; }}
            .shortcut-hint {{ font-size: 0.75em; color: #8b949e; font-style: italic; }}
            .ai-badge {{ background: #03dac6; color: #000; font-size: 0.75em; padding: 2px 8px; border-radius: 4px; font-weight: bold; display: {has_ai}; }}
        </style>
        <script>
            function setupTool() {{
                // JS to uncheck "None" if any other intent is checked
                const sections = document.querySelectorAll('.section');
                sections.forEach(section => {{
                    const checkboxes = section.querySelectorAll('input[type="checkbox"]');
                    checkboxes.forEach(cb => {{
                        cb.addEventListener('change', () => {{
                            if (cb.value !== 'None' && cb.checked) {{
                                const noneBox = section.querySelector('input[value="None"]');
                                if (noneBox) noneBox.checked = false;
                            }} 
                            if ([...checkboxes].filter(c => c.checked && c.value !== 'None').length === 0) {{
                                const noneBox = section.querySelector('input[value="None"]');
                                if (noneBox) noneBox.checked = true;
                            }}
                        }});
                    }});
                }});

                // Shortcuts
                document.addEventListener('keydown', function(e) {{
                    const key = e.key.toLowerCase();
                    if (key === 's') {{
                        const aiLabels = document.querySelectorAll('.ai-suggested');
                        if (aiLabels.length > 0) {{
                            // Clear all first
                            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
                            
                            aiLabels.forEach(label => {{
                                const input = label.querySelector('input');
                                input.checked = true;
                                
                                // Uncheck None for this section
                                const section = input.closest('.section');
                                const noneBox = section.querySelector('input[value="None"]');
                                if (noneBox) noneBox.checked = false;
                            }});
                            // For sections with NO AI suggestion, check None
                            document.querySelectorAll('.section').forEach(section => {{
                                if (section.querySelectorAll('input[type="checkbox"]:checked').length === 0) {{
                                    const noneBox = section.querySelector('input[value="None"]');
                                    if (noneBox) noneBox.checked = true;
                                }}
                            }});
                            
                            setTimeout(() => {{ document.querySelector('form').submit(); }}, 250);
                        }} else {{
                            document.querySelector('form').submit();
                        }}
                    }}
                    if (key === 'd') {{
                        document.querySelector('form').submit();
                    }}
                    if (key === 'k') {{
                        window.location.href = '/skip?index={index}';
                    }}
                }});
            }}
            window.addEventListener('DOMContentLoaded', setupTool);
        </script>
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
                    <span># {c_id}</span>
                    <span class="status-badge {'status-labeled' if df.at[index, 'out_of_scope'] != '' else ''}">
                        {'LABELED' if df.at[index, 'out_of_scope'] != '' else 'PENDING'}
                    </span>
                    <span class="ai-badge">AI ASSISTED</span>
                </div>
                <div class="comment-text">{comment['comment_text']}</div>
            </div>
            
            <form action="/save" method="post">
                <input type="hidden" name="index" value="{index}">
                <div class="grid">
                    {sections_html}
                </div>
                
                <div class="footer">
                    <div class="nav-links">
                        <a href="/?index={index-1 if index > 0 else 0}">← Previous</a>
                        <a href="/?index={index+1}">Next →</a>
                        <a href="/skip?index={index}" style="color: #ff5252;">Skip (K)</a>
                        <div class="shortcut-hint"><b>S</b>: Accept AI + Save | <b>D</b>: Save & Next | <b>K</b>: Skip</div>
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
        vals = form_data.getlist(f"{cat}[]")  # get all checked options
        if 'None' in vals or not vals:
            df.at[index, cat] = ""  # default = None
        else:
            all_none = False
            df.at[index, cat] = ",".join(vals)  # store as comma-separated string

    df.at[index, 'out_of_scope'] = "True" if all_none else "False"
    df.to_csv(PART_FILE, index=False)
    
    c_id = df.at[index, 'comment_id']
    print(f"✅ Saved Sweep: Comment ID {c_id}")

    # --- Immediate Master Sync ---
    if args.master and os.path.exists(args.master):
        try:
            df_master = pd.read_csv(args.master, keep_default_na=False)
            # Find the row in master by comment_id
            m_mask = df_master['comment_id'].astype(str) == str(c_id)
            if m_mask.any():
                m_idx = df_master[m_mask].index[0]
                cols = ['food', 'service', 'place', 'delivery', 'price', 'treatment', 'out_of_scope']
                for col in cols:
                    df_master.at[m_idx, col] = df.at[index, col]
                df_master.to_csv(args.master, index=False)
                print(f"🔄 Synced to Master: {args.master}")
            else:
                print(f"⚠️ Comment ID {c_id} not found in master {args.master}")
        except Exception as e:
            print(f"⚠️ Sync failed: {e}")

    next_idx = get_next_index()
    return RedirectResponse(
        url=f"/?index={next_idx}" if next_idx is not None else "/?index=" + str(len(df)), 
        status_code=303
    )

@app.get("/skip")
async def skip_item(index: int):
    skipped_indices.add(index)
    print(f"⏭️ Skipped comment index {index} for this session.")
    next_idx = get_next_index()
    return RedirectResponse(
        url=f"/?index={next_idx}" if next_idx is not None else "/?index=" + str(len(df)), 
        status_code=303
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)