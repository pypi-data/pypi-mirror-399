import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from playwright.async_api import async_playwright
from tweakio_browser_playwright.adapter import PlaywrightAdapter

async def main():
    print("Starting Browser Adapter POC Test...")
    async with async_playwright() as p:
        # User side initialization (Concept)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Wrap with our new Adapter
        adapter = PlaywrightAdapter(page)
        
        # Test 1: Navigation
        print("Test 1: Navigating to example.com")
        await adapter.goto("http://example.com")
        
        # Test 2: Get URL
        url = await adapter.get_url()
        print(f"Current URL: {url}")
        assert "example.com" in url
        
        # Test 3: Get Text (Verify h1)
        # Using abstract method from interface
        print("Test 3: Reading content")
        h1_text = await adapter.get_text("h1")
        print(f"H1 content: {h1_text}")
        assert "Example Domain" in h1_text
        
        # Test 4: Lifecycle - Reload
        print("Test 4: Reloading page")
        await adapter.reload()
        print("Reload successful")
        
        await browser.close()
        print("Test Passed: Browser Adapter works correctly.")

if __name__ == "__main__":
    asyncio.run(main())
