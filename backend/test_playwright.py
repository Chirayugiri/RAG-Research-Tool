"""
Test Playwright extraction instead of requests.
"""

import sys
sys.path.insert(0, '/home/chirayu/All Files/Projects/Python Projects/RAG-News-Tool/backend')

from services.url_fetcher import URLFetcherService

# Test URL
test_url = "https://coinbazaar.in/blog/silvers-long-cycles-lessons-from-the-1980-2011-spikes/"

print("Testing with Playwright (Layer 2)...\n")

fetcher = URLFetcherService(timeout=15)
# Force using Layer 2
result = fetcher._fetch_layer2(test_url)

print(f"\n{'='*80}")
print("EXTRACTION RESULT")
print(f"{'='*80}")
print(f"Success: {result['success']}")
print(f"Method: {result['method']}")
print(f"Error: {result.get('error', 'None')}")

if result['success']:
    text = result['text']
    print(f"\nTotal characters extracted: {len(text):,}")
    
    # Search for the key information
    keywords_to_check = ["$199", "$72", "1980", "2011", "silver", "inflation-adjusted", "equivalent"]
    
    print(f"\n{'='*80}")
    print("KEYWORD CHECK")
    print(f"{'='*80}")
    for keyword in keywords_to_check:
        if keyword.lower() in text.lower():
            print(f"✅ Found '{keyword}'")
        else:
            print(f"❌ Missing '{keyword}'")
    
    # Show context around $199
    if "$199" in text:
        idx = text.find("$199")
        print(f"\n\nContext around '$199':")
        print(text[max(0, idx-300):idx+300])
    
    # Save full text
    with open('/tmp/extracted_playwright.txt', 'w') as f:
        f.write(text)
    print(f"\n\nFull extracted text saved to: /tmp/extracted_playwright.txt")
else:
    print(f"\nFailed to extract content: {result.get('error')}")
