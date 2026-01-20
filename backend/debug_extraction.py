"""
Debug script to test URL extraction and see what text is actually being captured.
"""

import sys
sys.path.insert(0, '/home/chirayu/All Files/Projects/Python Projects/RAG-News-Tool/backend')

from services.url_fetcher import URLFetcherService

# Test URL from the user's question
test_url = "https://coinbazaar.in/blog/silvers-long-cycles-lessons-from-the-1980-2011-spikes/"

print("Testing URL extraction...\n")

fetcher = URLFetcherService(timeout=15)
result = fetcher.fetch(test_url)

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
    if "$199" in text or "199" in text:
        print("\n✅ Found '$199' or '199' in extracted text")
        # Show context around it
        if "$199" in text:
            idx = text.find("$199")
            print(f"\nContext around '$199':")
            print(text[max(0, idx-200):idx+200])
    else:
        print("\n❌ Did NOT find '$199' or '199' in extracted text")
    
    if "$72" in text or "72" in text:
        print("\n✅ Found '$72' or '72' in extracted text")
        # Show context around it
        if "$72" in text:
            idx = text.find("$72")
            print(f"\nContext around '$72':")
            print(text[max(0, idx-200):idx+200])
    else:
        print("\n❌ Did NOT find '$72' or '72' in extracted text")
    
    # Check for keywords
    keywords = ["1980", "2011", "silver", "inflation-adjusted", "equivalent"]
    print(f"\n{'='*80}")
    print("KEYWORD CHECK")
    print(f"{'='*80}")
    for keyword in keywords:
        if keyword in text.lower():
            print(f"✅ Found '{keyword}'")
        else:
            print(f"❌ Missing '{keyword}'")
    
    # Save full text to file for inspection
    with open('/tmp/extracted_text.txt', 'w') as f:
        f.write(text)
    print(f"\n\nFull extracted text saved to: /tmp/extracted_text.txt")
    print(f"You can view it with: cat /tmp/extracted_text.txt")
else:
    print(f"\nFailed to extract content: {result.get('error')}")
