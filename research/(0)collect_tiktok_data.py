import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth
import os
import random
from datetime import datetime

# Hashtags defined by user
HASHTAGS = [
    "restaurationalgerienne",
    "restaurantsalgeriens",
    "restaurantalgerien",
    "dzfastfood",
    "fastfooddz",
    "restaurantalger",
    "restaurantalgerie",
    "fastfoodalgeria",
    "algeriafastfood"
]

OUTPUT_FILE = "tiktok_dataset.csv"
TARGET_COUNT = 5000

# Initialize CSV if it doesn't exist
if not os.path.exists(OUTPUT_FILE):
    df_schema = pd.DataFrame(columns=[
        "comment_id", "platform", "source_name", "comment_text", 
        "date", "likesCount", "video_id", "video_url", "hashtag"
    ])
    df_schema.to_csv(OUTPUT_FILE, index=False)

def get_total_collected():
    try:
        if not os.path.exists(OUTPUT_FILE):
            return 0
        df = pd.read_csv(OUTPUT_FILE)
        return len(df)
    except:
        return 0

def get_scraped_video_ids():
    try:
        if not os.path.exists(OUTPUT_FILE):
            return set()
        df = pd.read_csv(OUTPUT_FILE)
        if 'video_id' in df.columns:
            return set(df['video_id'].dropna().astype(str).unique())
        return set()
    except:
        return set()

async def save_comments(comments_data):
    if not comments_data:
        return
    df = pd.DataFrame(comments_data)
    # Append to CSV
    df.to_csv(OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE), index=False)
    print(f"Saved {len(comments_data)} comments. Total collected: {get_total_collected()}")

async def process_video(page, video_url, hashtag):
    try:
        video_id = video_url.split('/')[-1].split('?')[0]
        # Extract author from URL: https://www.tiktok.com/@username/video/...
        url_author = "unknown"
        if '@' in video_url:
            url_author = video_url.split('@')[-1].split('/')[0]

        print(f"  Navigating to video: {video_url} (Author: {url_author})")
        
        await page.goto(video_url)
        # Give it a good initial load time
        await page.wait_for_timeout(random.randint(3000, 5000))
        
        # Check for captcha
        if "Captcha" in await page.title():
            print("  Captcha detected! Pausing for manual solve (60s)...")
            await page.wait_for_timeout(60000)

        video_comments = []
        seen_comment_texts = set()
        
        # We will scroll many times quickly to load comments, then extract once
        max_scrolls = 30
        print(f"    Scrolling {max_scrolls} times to load comments...")
        
        for i in range(max_scrolls):
            await page.mouse.move(1000, 400)
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(400) # Fast scroll
            
            # Optional: check if we hit a "View more" or "Load more" if they are visible
            if i % 10 == 0:
                view_more = page.locator('p:has-text("View more"), p:has-text("Load more")')
                if await view_more.count() > 0:
                    try:
                        await view_more.first.click()
                    except:
                        pass

        # Now extract everything visible at once
        print("    Extracting all visible comments...")
        comments_elements = await page.locator('[data-e2e="comment-level-1"]').all()
        if not comments_elements:
            comments_elements = await page.locator('div[class*="DivCommentItemWrapper"]').all()
        
        batch = []
        for el in comments_elements:
            try:
                # Text content
                text = ""
                text_el = el.locator('[data-e2e="comment-level-1-content"]')
                if await text_el.count() > 0:
                    text = await text_el.inner_text(timeout=300)
                else:
                    try:
                        text = await el.locator('span[class*="SpanCommentContent"]').inner_text(timeout=300)
                    except:
                        text = await el.locator('p').first.inner_text(timeout=300)
                
                if text:
                    text = text.strip().replace('\n', ' ')
                
                if not text or len(text) < 2:
                    continue
                
                # Author
                comment_author = url_author
                user_el = el.locator('[data-e2e="comment-user-nickname"]')
                if await user_el.count() > 0:
                    comment_author = await user_el.first.inner_text(timeout=300)

                # Likes
                likes_text = "0"
                like_el = el.locator('[data-e2e="comment-like-count"]')
                if await like_el.count() > 0:
                    likes_text = await like_el.inner_text(timeout=300)

                batch.append({
                    "comment_id": str(random.randint(1000000, 9999999)), 
                    "platform": "tiktok",
                    "source_name": comment_author,
                    "comment_text": text,
                    "date": datetime.now().isoformat(),
                    "likesCount": likes_text,
                    "video_id": video_id,
                    "video_url": video_url,
                    "hashtag": hashtag
                })
            except:
                continue
        
        if batch:
            await save_comments(batch)
            print(f"    Saved {len(batch)} comments for this video.")
        else:
            print("    No comments found for this video.")

    except Exception as e:
        print(f"  Error processing video: {e}")

async def main():
    print(f"Starting collection. Target: {TARGET_COUNT} rows.")
    
    scraped_videos = get_scraped_video_ids()
    print(f"Already have data for {len(scraped_videos)} videos.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headful to bypass detection better and watch
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        for hashtag in HASHTAGS:
            if get_total_collected() >= TARGET_COUNT:
                break
                
            url = f"https://www.tiktok.com/tag/{hashtag}"
            print(f"Processing tag: {hashtag} -> {url}")
            
            try:
                await page.goto(url)
                await page.wait_for_timeout(random.randint(5000, 8000))
                
                # Check for captcha
                if "Captcha" in await page.title():
                    print("Captcha detected! Waiting for manual solve...")
                    await page.wait_for_timeout(30000)
                
                # Scroll to load more videos
                for _ in range(5): 
                    await page.mouse.wheel(0, 1500)
                    await page.wait_for_timeout(1500)
                
                # Find video links
                links = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a'))
                        .map(a => a.href)
                        .filter(href => href.includes('/video/'))
                }''')
                
                links = list(set(links))
                print(f"Found {len(links)} videos for #{hashtag}")
                
                for video_url in links:
                    if get_total_collected() >= TARGET_COUNT:
                        break
                    
                    video_id = video_url.split('/')[-1].split('?')[0]
                    if video_id in scraped_videos:
                        # print(f"  Skipping already scraped video: {video_id}")
                        continue
                    
                    await process_video(page, video_url, hashtag)
                    scraped_videos.add(video_id)
                    await page.wait_for_timeout(random.randint(3000, 6000))
            except Exception as e:
                print(f"Error tag {hashtag}: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
