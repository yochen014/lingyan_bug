import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

class PTTScraper:
    def __init__(self):
        self.base_url = "https://www.ptt.cc"
        self.session = requests.Session()
        # Set over18 cookie
        self.session.cookies.set('over18', '1')

    def search(self, board, keyword, days_limit=7):
        """
        Search for posts in a specific board with a keyword and time limit.
        """
        results = []
        search_url = f"{self.base_url}/bbs/{board}/search?q={keyword}"
        
        current_date = datetime.now()
        start_date = current_date - timedelta(days=days_limit)
        
        page = 1
        while True:
            url = f"{search_url}&page={page}"
            response = self.session.get(url)
            if response.status_code != 200:
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            re_entries = soup.select('.r-ent')
            
            if not re_entries:
                break
            
            found_older = False
            for entry in re_entries:
                title_el = entry.select_one('.title a')
                if not title_el:
                    continue
                    
                title = title_el.text.strip()
                link = self.base_url + title_el['href']
                author = entry.select_one('.author').text.strip()
                date_str = entry.select_one('.date').text.strip() # Format: M/DD (e.g. 4/06)
                
                # PTT search results only provide M/DD. We need to handle the year.
                # If M/DD is ahead of current month, it's likely last year (though rare in recent search)
                month, day = map(int, date_str.split('/'))
                year = current_date.year
                if month > current_date.month:
                    year -= 1
                
                post_date = datetime(year, month, day)
                
                if post_date < start_date:
                    found_older = True
                    continue
                
                # Fetch post content and comments
                post_data = self.get_post_details(link)
                if post_data:
                    results.append({
                        'platform': 'PTT',
                        'board': board,
                        'title': title,
                        'author': author,
                        'time': post_data['time'],
                        'content': post_data['content'],
                        'url': link,
                        'comments': post_data['comments']
                    })
            
            if found_older or page > 5: # Limit to 5 pages for search for now
                break
            page += 1
            
        return results

    def get_post_details(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.select_one('#main-content')
        if not main_content:
            return None
            
        # Extract metadata
        metas = main_content.select('.article-metaline')
        post_time = ""
        for meta in metas:
            tag = meta.select_one('.article-meta-tag').text
            val = meta.select_one('.article-meta-value').text
            if tag == '時間':
                post_time = val # e.g. Mon Apr  6 15:00:00 2026
        
        # Clean content: remove metadata, push blocks, etc.
        for tag in main_content.select('.article-metaline, .article-metaline-right, .push'):
            tag.decompose()
        
        content = main_content.text.strip()
        
        # Re-fetch for comments since we decomposed them
        soup_comments = BeautifulSoup(response.text, 'html.parser')
        pushes = soup_comments.select('.push')
        comments = []
        for p in pushes:
            tag = p.select_one('.push-tag').text.strip()
            userid = p.select_one('.push-userid').text.strip()
            content_push = p.select_one('.push-content').text.strip(': ')
            time_push = p.select_one('.push-ipdatetime').text.strip()
            comments.append({
                'type': tag,
                'user': userid,
                'content': content_push,
                'time': time_push
            })
            
        return {
            'time': post_time,
            'content': content,
            'comments': comments
        }

if __name__ == "__main__":
    scraper = PTTScraper()
    # Test with a known board and keyword
    results = scraper.search("Gossiping", "AIGC", days_limit=1)
    for r in results:
        print(f"[{r['time']}] {r['author']}: {r['title']}")
        print(f"Content length: {len(r['content'])}")
        print(f"Comments count: {len(r['comments'])}")
        print("-" * 20)
