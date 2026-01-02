from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth
import asyncio

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        # specific video URL that was found
        url = "https://www.tiktok.com/@jaminska57/video/7524073451666148630"
        print(f"Navigating to video: {url}...")
        await page.goto(url)
        await page.wait_for_timeout(10000)
        
        # Scroll to ensure comments load
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(2000)
        
        print("Dumping comment HTML structure...")
        
        # Try to find comment elements using the strategies from the main script
        # Strategy 1: standard data-e2e
        comments_elements = await page.locator('[data-e2e="comment-level-1"]').all()
        
        if not comments_elements:
             # Strategy 2: Class name based (DivCommentItemWrapper)
            comments_elements = await page.locator('div[class*="DivCommentItemWrapper"]').all()

        if not comments_elements:
             # Strategy 3: DivCommentListContainer children
            container = page.locator('div[class*="DivCommentListContainer"]')
            if await container.count() > 0:
                comments_elements = await container.locator('> div').all()

        print(f"Found {len(comments_elements)} candidates.")
        
        if comments_elements:
            # Print outer HTML of first 2 comments
            for i in range(min(2, len(comments_elements))):
                html = await comments_elements[i].evaluate("el => el.outerHTML")
                print(f"\n--- Comment {i} HTML ---\n{html}\n----------------------\n")
        else:
            print("No comments found to inspect.")
        
        # Check for specific elements
        content = await page.content()
        if "captcha" in content.lower():
            print("Detected captcha!")
        else:
            print("No simple captcha text detected.")
            
        # Try to find video elements
        videos = await page.locator('div[data-e2e="search_video-item"]').count()
        print(f"Found {videos} videos/items (selector might be wrong, checking generic divs)")
        
        # Take a screenshot to verify (saved to current dir)
        await page.screenshot(path="debug_screenshot.png")
        print("Screenshot saved to debug_screenshot.png")
        
        # Save HTML
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
        print("HTML saved to debug_page.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
