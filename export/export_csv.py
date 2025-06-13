import pandas as pd
import streamlit as st
from datetime import datetime
import os

def export_to_csv(data, filename=None):
    """Export sentiment data to CSV file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_analysis_{timestamp}.csv"
    
    # Ensure data directory exists
    os.makedirs("data/exports", exist_ok=True)
    filepath = f"data/exports/{filename}"
    
    if isinstance(data, dict):
        # Single result
        df = pd.DataFrame([data])
    else:
        df = data
    
    df.to_csv(filepath, index=False)
    return filepath

def create_csv_download_link(data):
    """Create CSV data for download button"""
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data
    
    csv = df.to_csv(index=False)
    return csv