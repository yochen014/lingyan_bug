import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import re

class FacebookScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.base_url = "https://www.facebook.com"

    async def search(self, keyword, days_limit=7):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Using hashtag search can sometimes bypass the strict login wall of the main search
            # But the main search is: https://www.facebook.com/search/posts/?q={keyword}
            search_url = f"{self.base_url}/search/posts/?q={keyword}"
            await page.goto(search_url)
            
            # Wait for any post container. FB uses complex nested structures.
            # role="article" is common for posts.
            try:
                await page.wait_for_selector('div[role="article"]', timeout=15000)
            except:
                print(f"Facebook: No posts found or login required for keyword: {keyword}")
                # Try fallback to hashtag
                await page.goto(f"{self.base_url}/hashtag/{keyword}")
                try:
                    await page.wait_for_selector('div[role="article"]', timeout=10000)
                except:
                    await browser.close()
                    return []
            
            results = []
            seen_content = set()
            start_date = datetime.now() - timedelta(days=days_limit)
            
            # Scroll a few times
            for _ in range(3):
                articles = await page.query_selector_all('div[role="article"]')
                for article in articles:
                    try:
                        # Account Name: often in an <a> with aria-label or just text
                        # We look for links that don't have certain sub-words
                        user_el = await article.query_selector('h2 span a, h3 span a, strong a')
                        username = await user_el.text_content() if user_el else "Unknown User"
                        
                        # Content: usually in div[dir="auto"]
                        content_el = await article.query_selector('div[dir="auto"]')
                        content = await content_el.text_content() if content_el else ""
                        
                        if not content or content in seen_content:
                            continue
                        seen_content.add(content)
                        
                        # Time: often an <a> with aria-label like "3 hours ago", "Yesterday", "April 5"
                        # Or a <span id="..."> link.
                        # This is the hardest part without full DOM parsing.
                        time_el = await article.query_selector('a[role="link"] span[id], a[aria-label][role="link"]')
                        time_text = await time_el.get_attribute('aria-label') if time_el else ""
                        if not time_text:
                            # Fallback to text content if aria-label is empty
                            time_text = await time_el.text_content() if time_el else "Unknown time"
                        
                        # Post URL
                        url_el = await article.query_selector('a[href*="/posts/"], a[href*="/permalink/"]')
                        url = await url_el.get_attribute('href') if url_el else ""
                        if url and url.startswith('/'):
                            url = self.base_url + url
                        
                        results.append({
                            'platform': 'Facebook',
                            'account': username,
                            'time': time_text, # Keep as string for FB due to varied formats
                            'content': content,
                            'url': url
                        })
                    except:
                        continue
                
                await page.keyboard.press("PageDown")
                await asyncio.sleep(2)
                
            await browser.close()
            return results

if __name__ == "__main__":
    scraper = FacebookScraper(headless=True)
    async def run_test():
        results = await scraper.search("AIGC", days_limit=7)
        for r in results:
            print(f"[{r['time']}] {r['account']}: {r['content'][:100]}...")
            print(f"URL: {r['url']}")
            print("-" * 20)
            
    # asyncio.run(run_test())
