import asyncio
import random
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth

# List of video URLs to scrape - User can add more here
VIDEO_URLS = [
    "https://www.tiktok.com/@le_dauphin_restaurant/video/7581502164351175958",
    "https://www.tiktok.com/@said.zrk/video/7538466291674369300"
]

DATASET_FILE = "tiktok_dataset_single.csv"

async def save_comments(comments):
    if not comments:
        return
    df = pd.DataFrame(comments)
    df.to_csv(DATASET_FILE, mode='a', index=False, header=not asyncio.os.path.exists(DATASET_FILE))

async def scrape_comments_from_url(page, video_url):
    try:
        video_id = video_url.split('/')[-1].split('?')[0]
        url_author = "unknown"
        if '@' in video_url:
            url_author = video_url.split('@')[-1].split('/')[0]

        print(f"--- Processing: {video_url} ---")
        await page.goto(video_url)
        await page.wait_for_timeout(random.randint(4000, 6000))
        
        # Check for captcha
        if "Captcha" in await page.title():
            print("  [!] Captcha detected! Please solve it manually in the browser window.")
            await page.wait_for_timeout(30000)

        # Deep Scroll
        max_scrolls = 50 
        print(f"  Scrolling {max_scrolls} times to load ALL comments...")
        for i in range(max_scrolls):
            await page.mouse.move(1000, 400)
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(500)
            if i % 10 == 0:
                # Try simple load more click
                load_more = page.locator('p:has-text("Load more"), p:has-text("View more")')
                if await load_more.count() > 0:
                    try: await load_more.first.click()
                    except: pass

        # Extraction
        print("  Extracting comments...")
        elements = await page.locator('[data-e2e="comment-level-1"]').all()
        if not elements:
            elements = await page.locator('div[class*="DivCommentItemWrapper"]').all()
        
        results = []
        for el in elements:
            try:
                text = ""
                text_el = el.locator('[data-e2e="comment-level-1-content"]')
                if await text_el.count() > 0:
                    text = await text_el.inner_text(timeout=500)
                else:
                    text = await el.locator('span[class*="SpanCommentContent"]').inner_text(timeout=500)
                
                if text:
                    text = text.strip().replace('\n', ' ')
                if not text or len(text) < 2:
                    continue

                author = url_author
                user_el = el.locator('[data-e2e="comment-user-nickname"]')
                if await user_el.count() > 0:
                    author = await user_el.first.inner_text(timeout=500)

                likes = "0"
                like_el = el.locator('[data-e2e="comment-like-count"]')
                if await like_el.count() > 0:
                    likes = await like_el.inner_text(timeout=500)

                results.append({
                    "comment_id": str(random.randint(1000000, 9999999)),
                    "platform": "tiktok",
                    "source_name": author,
                    "comment_text": text,
                    "date": datetime.now().isoformat(),
                    "likesCount": likes,
                    "video_id": video_id,
                    "video_url": video_url,
                    "hashtag": "direct_url"
                })
            except:
                continue
        
        if results:
            await save_comments(results)
            print(f"  [√] Successfully saved {len(results)} comments.")
        else:
            print("  [x] No comments found.")

    except Exception as e:
        print(f"  [!] Error: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_obj = Stealth()
        await stealth_obj.apply_stealth_async(page)

        for url in VIDEO_URLS:
            await scrape_comments_from_url(page, url)
            # Short break between videos
            await asyncio.sleep(random.randint(3, 7))

        await browser.close()
        print("\n--- All URLs processed. ---")

if __name__ == "__main__":
    asyncio.run(main())
