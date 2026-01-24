from playwright.sync_api import sync_playwright
import time
import re

def find_profile():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tiktok.com/discover/american-burger-alger")
        time.sleep(10)
        content = page.content()
        handles = re.findall(r'/@[a-zA-Z0-9._-]+', content)
        print(f"FOUND_HANDLES: {list(set(handles))}")
        browser.close()

if __name__ == "__main__":
    find_profile()
