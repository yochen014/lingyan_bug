import asyncio
import argparse
from scraper_ptt import PTTScraper
from scraper_threads import ThreadsScraper
from scraper_facebook import FacebookScraper
from exporter import DataExporter
from datetime import datetime

async def main():
    parser = argparse.ArgumentParser(description="Social Media Keyword Scraper")
    parser.add_argument("keyword", help="Keyword to search for")
    parser.add_argument("--days", type=int, default=7, help="Days to look back (default: 7)")
    parser.add_argument("--platforms", nargs="+", default=["threads", "ptt", "facebook"], 
                        help="Platforms to scrape (options: threads ptt facebook)")
    parser.add_argument("--format", choices=["csv", "xlsx"], default="csv", help="Output format")
    
    args = parser.parse_args()
    
    print(f"--- Starting Scrape for '{args.keyword}' (Last {args.days} days) ---")
    
    all_results = []
    
    # 1. PTT
    if "ptt" in args.platforms:
        print("[PTT] Searching...")
        ptt = PTTScraper()
        # Common boards to search
        boards = ["Gossiping", "Stock", "C_Chat"]
        for board in boards:
            print(f"  - Searching board: {board}")
            board_results = ptt.search(board, args.keyword, days_limit=args.days)
            for r in board_results:
                # Standardize rows for export
                all_results.append({
                    'platform': 'PTT',
                    'time': r['time'],
                    'account': f"{r['author']} ({r['board']})",
                    'content': r['content'],
                    'url': r['url']
                })
                # Add comments as rows as well (optional, but requested "表格的那種")
                for c in r['comments']:
                    all_results.append({
                        'platform': 'PTT (Comment)',
                        'time': c['time'],
                        'account': c['user'],
                        'content': f"({c['type']}) {c['content']}",
                        'url': r['url']
                    })
        print(f"[PTT] Found {len(all_results)} entries (including comments).")

    # 2. Threads
    if "threads" in args.platforms:
        print("[Threads] Searching...")
        threads = ThreadsScraper(headless=True)
        threads_posts = await threads.search(args.keyword, days_limit=args.days)
        for r in threads_posts:
            all_results.append({
                'platform': 'Threads',
                'time': r['time'],
                'account': r['username'],
                'content': r['content'],
                'url': r['url']
            })
        print(f"[Threads] Found {len(threads_posts)} posts.")

    # 3. Facebook
    if "facebook" in args.platforms:
        print("[Facebook] Searching...")
        fb = FacebookScraper(headless=True)
        fb_posts = await fb.search(args.keyword, days_limit=args.days)
        for r in fb_posts:
            all_results.append({
                'platform': 'Facebook',
                'time': r['time'],
                'account': r['account'],
                'content': r['content'],
                'url': r['url']
            })
        print(f"[Facebook] Found {len(fb_posts)} posts.")

    # Data Export
    if all_results:
        print(f"--- Total entries found: {len(all_results)} ---")
        exporter = DataExporter()
        filepath = exporter.export(all_results, filename_prefix=f"results_{args.keyword}", format=args.format)
        if filepath:
            print(f"Done! Check the output directory: {filepath}")
    else:
        print("No results found across any platform.")

if __name__ == "__main__":
    asyncio.run(main())
