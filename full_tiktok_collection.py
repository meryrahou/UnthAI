import random
import pandas as pd
import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth

# Configuration
HASHTAGS = [
    # # Originals
    # "restaurationalgerienne", "restaurantsalgeriens", "restaurantalgerien",
    # "dzfastfood", "fastfooddz", "restaurantalger", "restaurantalgerie",
    # "fastfoodalgeria", "algeriafastfood",
    # User requested
    # "streetfooddz", "dzstreetfood", "fastfoodoran", "oranfastfood", "algerfastfood", 
    # "algerfastgood", "fastgooddz", 
    # "fastfoodannaba", "annabafastfood", "annabarestaurant",
    # "dzfastgood", 
    # "wahranrestaurant",
    "restaurantwahran", "oranrestaurant", "restaurantoran",
    "hydrarestaurant", "restauranthydra", "sidiyahiarestaurant", "restaurantsidiyahia",
    "tacosalger", "algertacos", "dzrestaurant", "restaurantdz", "koubafastfood",
    "fastfoodkouba", "valhydrarestaurant", "restaurantvalhydra", "koubarestaurant",
    "restaurantkouba", "crepealger", "algercrepe", "fastfoodcheraga", "pizaaalgeria",
    "sidiabdellahfastfood", "fastfoodsidiabdellah", "foodtokdz", "dzfoodtok",
    "coffeeshopdz", "dzcoffeshop", "poissanalgerie", "restaurant_algerie", "restaurant_alger",
    # Underscore versions
    "street_food_dz", "dz_street_food", "fast_food_oran", "oran_fast_food", "alger_fast_food",
    "alger_fast_good", "fast_good_dz", "fast_food_annaba", "annaba_fast_food", "annaba_restaurant",
    "restaurant_annaba", "dz_fast_good", "wahran_restaurant", "restaurant_wahran", "oran_restaurant",
    "restaurant_oran", "hydra_restaurant", "restaurant_hydra", "sidiyahia_restaurant", "restaurant_sidiyahia",
    "tacos_alger", "alger_tacos", "dz_restaurant", "restaurant_dz", "kouba_fast_food",
    "fast_food_kouba", "valhydra_restaurant", "restaurant_valhydra", "kouba_restaurant", "restaurant_kouba",
    "crepe_alger", "alger_crepe", "fast_food_cheraga", "pizaa_algeria", "sidiabdellah_fast_food",
    "fast_food_sidiabdellah", "food_tok_dz", "dz_food_tok", "coffee_shop_dz", "dz_coffee_shop"
]
# Deduplicate hashtags
HASHTAGS = list(dict.fromkeys(HASHTAGS))

VIDEOS_PER_HASHTAG = 40
DATASET_FILE = "tiktok_dataset_single.csv"
SCRAPED_VIDEOS_FILE = "scraped_video_ids.txt"

def load_scraped_videos():
    scraped = set()
    if os.path.exists(SCRAPED_VIDEOS_FILE):
        with open(SCRAPED_VIDEOS_FILE, "r") as f:
            scraped.update(line.strip() for line in f if line.strip())
    # Cross-check with CSV for absolute safety
    if os.path.exists(DATASET_FILE):
        try:
            df = pd.read_csv(DATASET_FILE, usecols=['video_id'])
            scraped.update(df['video_id'].astype(str).unique().tolist())
        except Exception as e:
            print(f"      [Dedupe] Note checking CSV: {e}")
    return scraped

def save_scraped_video(video_id):
    with open(SCRAPED_VIDEOS_FILE, "a") as f:
        f.write(f"{video_id}\n")

def save_comments(comments):
    if not comments:
        return
    df = pd.DataFrame(comments)
    header = not os.path.exists(DATASET_FILE)
    df.to_csv(DATASET_FILE, mode='a', index=False, header=header)
    print(f"      [CSV] Appended {len(comments)} comments.")

def discover_video_urls(page, hashtag):
    print(f"\n--- Discovering videos for #{hashtag} ---")
    url = f"https://www.tiktok.com/tag/{hashtag}"
    page.goto(url)
    page.wait_for_timeout(random.randint(5000, 8000))
    
    video_urls = set()
    scroll_attempts = 0
    
    while len(video_urls) < VIDEOS_PER_HASHTAG and scroll_attempts < 15:
        # Extract links
        links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a'))
                .map(a => a.href)
                .filter(href => href.includes('/video/'))
        }''')
        for link in links:
            video_urls.add(link)
        
        if len(video_urls) >= VIDEOS_PER_HASHTAG:
            break
            
        print(f"    Found {len(video_urls)} URLs so far...")
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(2000)
        scroll_attempts += 1
        
    final_urls = list(video_urls)[:VIDEOS_PER_HASHTAG]
    print(f"    Finished. Total collected for #{hashtag}: {len(final_urls)}")
    return final_urls

def scrape_video_comments(page, video_url, hashtag):
    video_id = video_url.split('/')[-1].split('?')[0]
    print(f"    -> Processing video: {video_url}")
    
    seen_cids = set()
    
    # Interceptor
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
                                "hashtag": hashtag
                            })
                    if new_batch:
                        save_comments(new_batch)
            except: pass

    page.on("response", handle_response)
    
    try:
        page.goto(video_url)
        page.wait_for_timeout(random.randint(4000, 6000))
        
        if "Captcha" in page.title():
            print("      [!] Captcha detected! Please solve it.")
            page.wait_for_timeout(60000)

        # Intelligent Scroll
        last_count = 0
        no_new_scrolls = 0
        for i in range(50):
            page.mouse.move(1000, 400)
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(800)
            
            if i % 10 == 0:
                try:
                    load_more = page.locator('p:has-text("View more"), p:has-text("Load more")')
                    if load_more.count() > 0:
                        load_more.first.click(timeout=1000)
                except: pass

            curr_count = len(seen_cids)
            if curr_count > last_count:
                last_count = curr_count
                no_new_scrolls = 0
            else:
                no_new_scrolls += 1
            
            if no_new_scrolls >= 8: # Stop if no new comments in 8 scrolls
                break
                
        print(f"      Finished video. Total: {len(seen_cids)}")
        save_scraped_video(video_id)
        
    except Exception as e:
        print(f"      [!] Error: {e}")
    finally:
        page.remove_listener("response", handle_response)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        
        for hashtag in HASHTAGS:
            video_urls = discover_video_urls(page, hashtag)
            
            for url in video_urls:
                # Reload scraped videos each time to be absolutely sure
                scraped_videos = load_scraped_videos()
                
                vid = url.split('/')[-1].split('?')[0]
                if vid in scraped_videos:
                    print(f"    Skipping already scraped video: {vid}")
                    continue
                
                scrape_video_comments(page, url, hashtag)
                page.wait_for_timeout(random.randint(2000, 4000))
                
        browser.close()
        print("\nAll hashtags and discovered videos have been processed.")

if __name__ == "__main__":
    main()
