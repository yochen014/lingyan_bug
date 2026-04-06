import asyncio
from playwright.async_api import async_playwright
import re
from datetime import datetime, timedelta
import json

class ThreadsScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.base_url = "https://www.threads.net"

    async def search(self, keyword, days_limit=7):
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=self.headless)
            # Create a context that looks like a real browser
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            search_url = f"{self.base_url}/search?q={keyword}"
            await page.goto(search_url)
            
            # Wait for content to load
            try:
                await page.wait_for_selector('div[role="article"]', timeout=10000)
            except:
                print(f"No results found or page load timeout for: {keyword}")
                await browser.close()
                return []
            
            results = []
            seen_post_ids = set()
            start_date = datetime.now() - timedelta(days=days_limit)
            
            # Scroll and collect
            max_scrolls = 5
            for _ in range(max_scrolls):
                articles = await page.query_selector_all('div[role="article"]')
                
                for article in articles:
                    try:
                        # Extract username
                        user_el = await article.query_selector('a[href^="/@"]')
                        username = await user_el.text_content() if user_el else "Unknown"
                        
                        # Extract post link and timestamp
                        time_el = await article.query_selector('a[href*="/post/"]')
                        post_url = await time_el.get_attribute('href') if time_el else ""
                        time_text = await time_el.text_content() if time_el else "" # e.g. "3h", "1d", "Mar 22"
                        
                        if not post_url:
                            continue
                            
                        # Unique post ID from URL
                        post_id = post_url.split('/')[-1]
                        if post_id in seen_post_ids:
                            continue
                        seen_post_ids.add(post_id)
                        
                        # Extract content
                        content_el = await article.query_selector('div[dir="auto"]')
                        content = await content_el.text_content() if content_el else ""
                        
                        # Convert relative time to timestamp
                        post_time = self.parse_relative_time(time_text)
                        
                        if post_time < start_date:
                            continue
                        
                        results.append({
                            'platform': 'Threads',
                            'username': username,
                            'time': post_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'content': content,
                            'url': f"{self.base_url}{post_url}"
                        })
                    except Exception as e:
                        print(f"Error parsing post: {e}")
                
                # Scroll down
                await page.keyboard.press("PageDown")
                await asyncio.sleep(2)
                
                # Check if we should stop scrolling (optional: check if new results were added)
                
            await browser.close()
            return results

    def parse_relative_time(self, time_str):
        now = datetime.now()
        time_str = time_str.strip()
        
        # 3h, 5m, 10s
        if 'h' in time_str:
            h = int(re.search(r'(\d+)h', time_str).group(1))
            return now - timedelta(hours=h)
        if 'm' in time_str:
            if 'mo' in time_str: # months
                mo = int(re.search(r'(\d+)mo', time_str).group(1))
                return now - timedelta(days=mo*30)
            m = int(re.search(r'(\d+)m', time_str).group(1))
            return now - timedelta(minutes=m)
        if 'd' in time_str:
            d = int(re.search(r'(\d+)d', time_str).group(1))
            return now - timedelta(days=d)
        if 'w' in time_str:
            w = int(re.search(r'(\d+)w', time_str).group(1))
            return now - timedelta(weeks=w)
            
        # "Mar 22", "Feb 10, 2024"
        try:
            if ',' in time_str:
                return datetime.strptime(time_str, "%b %d, %Y")
            else:
                dt = datetime.strptime(time_str, "%b %d")
                return dt.replace(year=now.year)
        except:
            return now

if __name__ == "__main__":
    scraper = ThreadsScraper(headless=True)
    async def run_test():
        results = await scraper.search("AIGC", days_limit=7)
        for r in results:
            print(f"[{r['time']}] {r['username']}: {r['content'][:50]}...")
            print(f"Link: {r['url']}")
            print("-" * 20)
            
    # asyncio.run(run_test()) # Requires playwright install
