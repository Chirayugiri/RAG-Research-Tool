"""
Simple Playwright test with detailed logging
"""

from playwright.sync_api import sync_playwright
import time

url = "https://coinbazaar.in/blog/silvers-long-cycles-lessons-from-the-1980-2011-spikes/"

print("Testing Playwright extraction...\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    print("1. Navigating to URL...")
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    print("   ✓ Page loaded")
    
    print("\n2. Waiting 5 seconds for JavaScript...")
    time.sleep(5)
    
    print("\n3. Checking page title...")
    title = page.title()
    print(f"   Title: {title}")
    
    print("\n4. Getting body text...")
    text = page.evaluate('document.body.innerText')
    print(f"   Extracted: {len(text)} characters")
    
    if len(text) > 0:
        print(f"\n5. First 1000 characters:\n{text[:1000]}")
        
        # Check for keywords
        keywords = ["1980", "2011", "$199", "$72", "silver"]
        print(f"\n6. Checking keywords:")
        for kw in keywords:
            if kw.lower() in text.lower():
                print(f"   ✓ Found: {kw}")
            else:
                print(f"   ✗ Missing: {kw}")
    
    browser.close()
