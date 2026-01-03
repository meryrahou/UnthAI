import random
import pandas as pd
import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth

# List of video URLs to scrape
VIDEO_URLS = [
    "https://www.tiktok.com/@le_dauphin_restaurant/video/7581502164351175958",
    "https://www.tiktok.com/@said.zrk/video/7538466291674369300"
]

DATASET_FILE = "tiktok_dataset_single.csv"

def save_comments(comments):
    if not comments:
        return
    df = pd.DataFrame(comments)
    # Write header only if file doesn't exist
    header = not os.path.exists(DATASET_FILE)
    df.to_csv(DATASET_FILE, mode='a', index=False, header=header)
    print(f"    Saved {len(comments)} comments to {DATASET_FILE}")

def scrape_url(page, video_url):
    print(f"\n--- Processing: {video_url} ---")
    video_id = video_url.split('/')[-1].split('?')[0]
    
    seen_cids = set()
    total_expected = 0
    
    # Try to get the total comment count from the UI
    try:
        # Give some time for the count to load
        page.wait_for_selector('[data-e2e="comment-count"]', timeout=5000)
        count_text = page.locator('[data-e2e="comment-count"]').inner_text()
        # count_text might be "2.1K", "123", etc.
        if 'K' in count_text:
            total_expected = int(float(count_text.replace('K', '')) * 1000)
        elif 'M' in count_text:
            total_expected = int(float(count_text.replace('M', '')) * 1000000)
        else:
            total_expected = int(count_text.replace(',', '').replace('.', ''))
        print(f"    [Info] Expected comments according to UI: {total_expected}")
    except:
        print("    [Info] Could not detect total comment count from UI.")

    # Network interceptor to catch the comments JSON
    def handle_response(response):
        if "/api/comment/list/" in response.url:
            try:
                data = response.json()
                if "comments" in data and data["comments"]:
                    new_batch = []
                    for c in data["comments"]:
                        cid = c.get("cid")
                        if cid and cid not in seen_cids:
                            seen_cids.add(cid)
                            new_batch.append({
                                "comment_id": cid,
                                "platform": "tiktok",
                                "source_name": c.get("user", {}).get("nickname", "unknown"),
                                "comment_text": c.get("text", "").replace("\n", " "),
                                "date": datetime.now().isoformat(),
                                "likesCount": c.get("digg_count", 0),
                                "video_id": video_id,
                                "video_url": video_url,
                                "hashtag": "direct_url"
                            })
                    
                    if new_batch:
                        save_comments(new_batch)
                        print(f"    [Interceptor] Saved {len(new_batch)} new comments. Total for this video: {len(seen_cids)}")
            except:
                pass

    page.on("response", handle_response)
    
    try:
        page.goto(video_url)
        page.wait_for_timeout(random.randint(4000, 6000))
        
        if "Captcha" in page.title():
            print("  [!] Captcha detected. Please solve it.")
            page.wait_for_timeout(60000)

        # Scrolling loop
        max_attempts_without_new = 10
        attempts_without_new = 0
        last_count = 0
        
        print("  Starting intelligent scroll loop...")
        for i in range(100): # Hard limit of 100 scrolls
            page.mouse.move(1000, 400)
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1000)
            
            # Check for 'View more' expansion
            if i % 5 == 0:
                try:
                    load_more = page.locator('p:has-text("View more"), p:has-text("Load more")')
                    if load_more.count() > 0:
                        load_more.first.click(timeout=1000)
                except: pass

            current_count = len(seen_cids)
            if current_count > last_count:
                attempts_without_new = 0
                last_count = current_count
            else:
                attempts_without_new += 1
            
            # If we haven't seen new comments in 10 scrolls, we're likely done
            if attempts_without_new >= max_attempts_without_new:
                print("    No new comments detected for several scrolls. Finishing video.")
                break
                
            if total_expected > 0 and current_count >= total_expected:
                print(f"    Reached target count of {total_expected}. Finishing video.")
                break

        print(f"--- Finished processing {video_url}. Total comments: {len(seen_cids)} ---")
        
    except Exception as e:
        print(f"  [!] Error on {video_url}: {e}")
    finally:
        # Clean up the listener for the next URL
        page.remove_listener("response", handle_response)

def main():
    with sync_playwright() as p:
        # User wants headful to solve captchas and see progress
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Apply stealth (sync version)
        stealth = Stealth()
        stealth.apply_stealth_sync(page)
        
        for url in VIDEO_URLS:
            scrape_url(page, url)
            print(f"Waiting before next URL...")
            page.wait_for_timeout(random.randint(3000, 5000))
            
        browser.close()
        print("\nAll targeted URLs have been processed synchronously.")

if __name__ == "__main__":
    main()
