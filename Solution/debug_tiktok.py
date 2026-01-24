from playwright.sync_api import sync_playwright
import time

def debug_profile():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tiktok.com/@american_burger_dz")
        time.sleep(10)
        print(f"URL: {page.url}")
        print(f"TITLE: {page.title()}")
        # Check for presence of video links
        links = page.locator('a[href*="/video/"]').all()
        print(f"VIDEO LINKS FOUND: {len(links)}")
        if len(links) > 0:
            for i in range(min(5, len(links))):
                print(f"LINK {i}: {links[i].get_attribute('href')}")
        
        # Take a screenshot for me to see
        page.screenshot(path="tiktok_debug.png")
        browser.close()

if __name__ == "__main__":
    debug_profile()
