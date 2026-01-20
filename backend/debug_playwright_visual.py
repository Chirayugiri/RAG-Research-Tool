"""
Debug what Playwright actually sees
"""

from playwright.sync_api import sync_playwright

url = "https://coinbazaar.in/blog/silvers-long-cycles-lessons-from-the-1980-2011-spikes/"

print("Testing Playwright extraction in detail...\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # NOT headless so we can see what happens
    page = browser.new_page()
    
    print("Navigating to URL...")
    page.goto(url, timeout=30000)
    
    print("Waiting for page to load...")
    page.wait_for_timeout(5000)
    
    print("Taking screenshot...")
    page.screenshot(path='/tmp/screenshot.png')
    
    print("Getting page content...")
    content = page.content()
    with open('/tmp/page_html.html', 'w') as f:
        f.write(content)
    
    print("Getting inner text...")
    text = page.evaluate('document.body.innerText')
    print(f"\nExtracted {len(text)} characters")
    print(f"First 500 chars:\n{text[:500]}")
    
    with open('/tmp/body_text.txt', 'w') as f:
        f.write(text)
    
    browser.close()

print("\n\nFiles saved:")
print("- /tmp/screenshot.png")
print("- /tmp/page_html.html") 
print("- /tmp/body_text.txt")
