"""
URL Fetcher Service using Playwright with parallel processing.

Uses async Playwright to scrape multiple URLs concurrently for maximum efficiency.
"""

import asyncio
from typing import Dict, Any, List
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URLFetcherService:
    """Service for fetching web content using async Playwright with parallel processing."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize URL fetcher service.
        
        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and newlines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)
    
    async def _fetch_async(self, url: str, browser_instance=None) -> Dict[str, Any]:
        """
        Fetch content from URL using async Playwright.
        
        Args:
            url: URL to fetch
            browser_instance: Optional browser instance to reuse
            
        Returns:
            Dictionary with success status, text, url, method, and error (if any)
        """
        browser = None
        should_close_browser = False
        
        try:
            if browser_instance is None:
                playwright = await async_playwright().start()
                browser = await playwright.chromium.launch(
                    headless=True, 
                    args=['--disable-blink-features=AutomationControlled']
                )
                should_close_browser = True
            else:
                browser = browser_instance
            
            # Create new context for this URL
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Navigate to URL with longer timeout
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for article content to appear (try multiple selectors)
            try:
                await page.wait_for_selector('article, main, .entry-content, .post-content, body', timeout=10000)
            except:
                pass  # Continue even if selector doesn't match
            
            # Scroll to trigger lazy loading
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
            await page.wait_for_timeout(2000)
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            
            # Extract text from body with better content selection
            text_content = await page.evaluate('''() => {
                // Try to find main content container
                const selectors = ['article', 'main', '.entry-content', '.post-content', '.article-content'];
                let contentEl = null;
                
                for (const selector of selectors) {
                    contentEl = document.querySelector(selector);
                    if (contentEl) break;
                }
                
                // Fall back to body if no specific content container found
                if (!contentEl) contentEl = document.body;
                
                // Remove unwanted elements
                const unwanted = contentEl.querySelectorAll('script, style, nav, noscript, iframe, form');
                unwanted.forEach(el => el.remove());
                
                // Get text content
                return contentEl.innerText;
            }''')
            
            # Close context
            await context.close()
            
            # Close browser if we created it
            if should_close_browser and browser:
                await browser.close()
            
            clean_text = self._clean_text(text_content)
            
            if not clean_text or len(clean_text) < 100:
                return {
                    'success': False,
                    'text': '',
                    'url': url,
                    'method': 'playwright',
                    'error': 'Insufficient text content extracted'
                }
            
            # Simple success log
            print(f"\n#########\n{url} - Playwright\n#########\n")
            
            return {
                'success': True,
                'text': clean_text,
                'url': url,
                'method': 'playwright',
                'error': None
            }
            
        except PlaywrightTimeoutError:
            if should_close_browser and browser:
                await browser.close()
            return {
                'success': False,
                'text': '',
                'url': url,
                'method': 'playwright',
                'error': 'Browser timeout'
            }
        except Exception as e:
            if should_close_browser and browser:
                await browser.close()
            return {
                'success': False,
                'text': '',
                'url': url,
                'method': 'playwright',
                'error': str(e)
            }
    
    async def fetch_multiple_async(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch content from multiple URLs in parallel using async Playwright.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            List of fetch results
        """
        # Launch a single browser instance for all parallel fetches
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create tasks for all URLs
            tasks = [self._fetch_async(url, browser) for url in urls]
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Close browser
            await browser.close()
            
            # Handle any exceptions that occurred
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'text': '',
                        'url': urls[i],
                        'method': 'playwright',
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from URL (sync wrapper).
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with success status, text, url, method, and error (if any)
        """
        return asyncio.run(self._fetch_async(url))
    
    def fetch_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch content from multiple URLs in parallel (sync wrapper).
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            List of fetch results
        """
        return asyncio.run(self.fetch_multiple_async(urls))
