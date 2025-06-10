# export/export_json.py
import pandas as pd

def export_to_json(data: pd.DataFrame, filename="sentiment_results.json"):
    data.to_json(filename, orient='records', lines=True)
    return filename
