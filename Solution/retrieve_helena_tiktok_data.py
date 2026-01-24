import random
import pandas as pd
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth

# Configuration
TARGET_PROFILE = "https://www.tiktok.com/@helena_restaurant"
NUM_VIDEOS = 10
OUTPUT_FILE = "Solution/backend/data/new_helena_data.csv"
RESTAURANT_NAME = "Helena"

def save_comments(comments):
    if not comments:
        return
    df = pd.DataFrame(comments)
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    header = not os.path.exists(OUTPUT_FILE)
    df.to_csv(OUTPUT_FILE, mode='a', index=False, header=header)
    print(f"      [CSV] Appended {len(comments)} comments to {OUTPUT_FILE}.")

def scrape_video_comments(page, video_url):
    video_id = video_url.split('/')[-1].split('?')[0]
    print(f"    -> Processing video: {video_url}")
    
    seen_cids = set()
    collected_batch = []
    
    # Interceptor
    def handle_response(response):
        if "/api/comment/list/" in response.url:
            try:
                data = response.json()
                if "comments" in data and data["comments"]:
                    for c in data["comments"]:
                        cid = c.get("cid")
                        if cid and cid not in seen_cids:
                            seen_cids.add(cid)
                            collected_batch.append({
                                "comment_id": cid,
                                "platform": "tiktok",
                                "source_name": c.get("user", {}).get("nickname", "unknown"),
                                "comment_text": c.get("text", "").replace("\n", " "),
                                "date": datetime.now().isoformat(),
                                "likesCount": c.get("digg_count", 0),
                                "video_id": video_id,
                                "video_url": video_url,
                                "restaurant": RESTAURANT_NAME
                            })
            except: pass

    page.on("response", handle_response)
    
    try:
        page.goto(video_url)
        page.wait_for_timeout(random.randint(4000, 6000))
        
        # Intelligent Scroll to trigger comment loading
        last_count = 0
        no_new_scrolls = 0
        for i in range(20): # Scrape a decent amount per video
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1000)
            
            curr_count = len(seen_cids)
            if curr_count > last_count:
                last_count = curr_count
                no_new_scrolls = 0
            else:
                no_new_scrolls += 1
            
            if no_new_scrolls >= 5:
                break
                
        if collected_batch:
            save_comments(collected_batch)
        print(f"      Finished video. Total collected: {len(seen_cids)}")
        
    except Exception as e:
        print(f"      [!] Error: {e}")
    finally:
        page.remove_listener("response", handle_response)

def main():
    print(f"--- 🚀 Starting Scraper for {RESTAURANT_NAME} ---")
    with sync_playwright() as p:
        # Launching with headless=False so user can see and interact
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        
        print(f"Opening profile: {TARGET_PROFILE}")
        page.goto(TARGET_PROFILE)
        
        print("\n[!] Opening TikTok. Please solve any 'I'm not a robot' check or Captcha in the browser window.")
        print("[!] Once you've solved it and can see the page content, come back here and press ENTER.")
        input(">>> Press ENTER here after you have solved the captcha and are on the profile page...")

        print(f"--- Processing profile: {page.url} ---")
        
        # Extract video links
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(3000)
        
        video_urls = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a'))
                .map(a => a.href)
                .filter(href => href.includes('/video/') && !href.includes('/photo/'))
        }''')
        
        unique_urls = []
        seen_urls = set()
        for url in video_urls:
            base_url = url.split('?')[0]
            if base_url not in seen_urls:
                seen_urls.add(base_url)
                unique_urls.append(base_url)
        
        final_urls = unique_urls[:NUM_VIDEOS]
        
        if not final_urls:
            print("[!] No videos found! Did the page load correctly?")
            browser.close()
            return

        print(f"Found {len(final_urls)} videos to process.")
        
        for url in final_urls:
            scrape_video_comments(page, url)
            page.wait_for_timeout(random.randint(2000, 4000))
            
        browser.close()
        print(f"\nCompleted! Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
