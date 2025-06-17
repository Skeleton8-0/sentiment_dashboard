import pandas as pd
import json
from datetime import datetime

def export_to_json(data, filename=None):
    """Export sentiment data to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_analysis_{timestamp}.json"
    
    if isinstance(data, pd.DataFrame):
        json_data = data.to_dict('records')
    else:
        json_data = data
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return filename

def create_json_download_data(data):
    """Create JSON data for download button"""
    if isinstance(data, pd.DataFrame):
        return data.to_json(orient='records', indent=2)
    else:
        return json.dumps(data, indent=2)