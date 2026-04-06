import pandas as pd
from datetime import datetime
import os

class DataExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export(self, data, filename_prefix="social_media_results", format="csv"):
        """
        Export data to CSV or Excel.
        data: list of dicts with common schema:
            - platform
            - time
            - account
            - content
            - url
        """
        if not data:
            print("No data to export.")
            return None
            
        df = pd.DataFrame(data)
        
        # Ensure standard ordering of columns
        cols = ['platform', 'time', 'account', 'content', 'url']
        # Filter columns that actually exist in the dataframe
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if format.lower() == "csv":
            filepath += ".csv"
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format.lower() == "xlsx":
            filepath += ".xlsx"
            df.to_excel(filepath, index=False)
        else:
            print(f"Unsupported format: {format}")
            return None
            
        print(f"Data exported successfully to: {filepath}")
        return filepath

if __name__ == "__main__":
    # Test data
    test_data = [
        {'platform': 'PTT', 'time': '2026-04-06 12:00:00', 'account': 'user1', 'content': 'Hello from PTT', 'url': 'http://ptt.cc/1'},
        {'platform': 'Threads', 'time': '2026-04-06 12:05:00', 'account': 'user2', 'content': 'Hello from Threads', 'url': 'http://threads.net/2'}
    ]
    exporter = DataExporter()
    exporter.export(test_data, format="csv")
    exporter.export(test_data, format="xlsx")
