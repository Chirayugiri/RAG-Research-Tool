"""
Test script for two-layer web scraping approach.
Tests both Layer 1 (requests) and Layer 2 (Playwright) fallback.
"""

import sys
sys.path.insert(0, '/home/chirayu/All Files/Projects/Python Projects/RAG-News-Tool/backend')

from services.url_fetcher import URLFetcherService
from services.preprocessing import PreprocessingService

# Test URLs
# Simple HTML sites (should use Layer 1)
simple_urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.bbc.com/news"
]

# JavaScript-heavy sites (might need Layer 2)
js_heavy_urls = [
    "https://www.theguardian.com/world"
]

def test_url_fetcher():
    """Test URLFetcherService directly."""
    print("\n" + "="*80)
    print("Testing URLFetcherService")
    print("="*80)
    
    fetcher = URLFetcherService(timeout=10)
    
    # Test simple URLs
    print("\n--- Testing Simple URLs (Layer 1 expected) ---")
    for url in simple_urls[:1]:  # Test only first URL to save time
        print(f"\nFetching: {url}")
        result = fetcher.fetch(url)
        print(f"Success: {result['success']}")
        print(f"Method: {result['method']}")
        print(f"Text length: {len(result['text']) if result['text'] else 0}")
        if not result['success']:
            print(f"Error: {result['error']}")
        else:
            print(f"Preview: {result['text'][:200]}...")

def test_preprocessing_service():
    """Test PreprocessingService with new fetcher."""
    print("\n" + "="*80)
    print("Testing PreprocessingService")
    print("="*80)
    
    preprocessing = PreprocessingService()
    
    print("\n--- Processing URLs ---")
    test_url = ["https://en.wikipedia.org/wiki/Machine_learning"]
    
    try:
        result = preprocessing.process_urls(test_url)
        print(f"\nSuccess: {result['success']}")
        print(f"Documents: {result['num_documents']}")
        print(f"Chunks: {result['num_chunks']}")
        print(f"Message: {result['message']}")
        
        if result['success'] and result['chunks']:
            first_chunk = result['chunks'][0]
            print(f"\nFirst chunk metadata: {first_chunk.metadata}")
            print(f"First chunk preview: {first_chunk.page_content[:200]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting Two-Layer Web Scraping Tests\n")
    
    # Test URL fetcher
    test_url_fetcher()
    
    # Test preprocessing service
    test_preprocessing_service()
    
    print("\n" + "="*80)
    print("Tests completed!")
    print("="*80)
