"""
Test script for Playwright-only scraping with parallel processing.
Demonstrates performance improvements from concurrent execution.
"""

import sys
import os
import time
import logging

# Ensure backend is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from services.url_fetcher import URLFetcherService

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraping_test_results.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_parallel_scraping():
    """Test parallel scraping and compare with sequential."""
    logger.info("Starting Playwright-Only Parallel Scraping Test")
    logger.info("="*80)

    # Test URLs - mix of different site types
    urls_to_test = [
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://www.bbc.com/news/world",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://www.theguardian.com/world",
        "https://react.dev",
    ]
    
    # Initialize Fetcher
    fetcher = URLFetcherService(timeout=15)
    
    # Test 1: Sequential Execution (one at a time)
    logger.info("\n" + "="*80)
    logger.info("TEST 1: SEQUENTIAL EXECUTION")
    logger.info("="*80)
    
    sequential_start = time.time()
    sequential_results = []
    
    for url in urls_to_test:
        logger.info(f"\nFetching: {url}")
        start_time = time.time()
        result = fetcher.fetch(url)
        duration = time.time() - start_time
        
        status = "SUCCESS" if result['success'] else "FAILED"
        content_len = len(result.get('text', ''))
        
        logger.info(f"Status: {status} | Length: {content_len} chars | Time: {duration:.2f}s")
        
        sequential_results.append({
            "url": url,
            "status": status,
            "length": content_len,
            "time": duration,
            "error": result.get('error')
        })
        
    sequential_total = time.time() - sequential_start
    
    # Test 2: Parallel Execution (all at once)
    logger.info("\n" + "="*80)
    logger.info("TEST 2: PARALLEL EXECUTION")
    logger.info("="*80)
    
    parallel_start = time.time()
    parallel_results_raw = fetcher.fetch_multiple(urls_to_test)
    parallel_total = time.time() - parallel_start
    
    parallel_results = []
    for i, result in enumerate(parallel_results_raw):
        status = "SUCCESS" if result['success'] else "FAILED"
        content_len = len(result.get('text', ''))
        url = urls_to_test[i]
        
        logger.info(f"\n{url}")
        logger.info(f"Status: {status} | Length: {content_len} chars")
        
        parallel_results.append({
            "url": url,
            "status": status,
            "length": content_len,
            "error": result.get('error')
        })
    
    # Performance Comparison
    logger.info("\n" + "="*80)
    logger.info("PERFORMANCE COMPARISON")
    logger.info("="*80)
    logger.info(f"Sequential Total Time: {sequential_total:.2f}s")
    logger.info(f"Parallel Total Time:   {parallel_total:.2f}s")
    logger.info(f"Time Saved:            {sequential_total - parallel_total:.2f}s")
    logger.info(f"Speed Improvement:     {sequential_total / parallel_total:.2f}x faster")
    
    # Summary Table
    logger.info("\n" + "="*80)
    logger.info("RESULTS SUMMARY")
    logger.info("="*80)
    logger.info(f"{'URL':<50} | {'Status':<8} | {'Length':<8}")
    logger.info("-"*80)
    
    for r in parallel_results:
        url_short = r['url'][:47] + '...' if len(r['url']) > 50 else r['url']
        logger.info(f"{url_short:<50} | {r['status']:<8} | {r['length']:<8}")
    
    logger.info("\n" + "="*80)
    logger.info(f"✅ Parallel processing is {sequential_total / parallel_total:.1f}x faster!")
    logger.info("="*80)

if __name__ == "__main__":
    test_parallel_scraping()
