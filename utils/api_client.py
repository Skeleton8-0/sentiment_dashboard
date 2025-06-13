import os
import requests
import time
import streamlit as st
from dotenv import load_dotenv
from utils.text_processing import extract_keywords

load_dotenv()  # Loads the .env file

API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

def analyze_sentiment(text):
    """Analyze sentiment for a single text using HuggingFace API"""
    payload = {"inputs": text}
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()[0]
            # Replace label codes with meaningful labels
            for item in result:
                item["label"] = LABEL_MAP.get(item["label"], item["label"])
            return sorted(result, key=lambda x: x["score"], reverse=True)
        else:
            return {"error": f"API error {response.status_code}: {response.text}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def batch_analyze_sentiment_with_keywords(text_list, delay=1, progress_callback=None):
    """Analyze sentiment and extract keywords for a list of texts"""
    results = []
    
    for i, text in enumerate(text_list):
        try:
            sentiment_result = analyze_sentiment(text)
            keywords = extract_keywords(text)
            
            results.append({
                "text": text,
                "sentiment": sentiment_result,
                "keywords": keywords
            })
            
        except Exception as e:
            results.append({
                "text": text,
                "error": str(e)
            })
        
        # Update progress if callback provided
        if progress_callback:
            progress_callback(i + 1, len(text_list))
        
        # Add delay between requests to avoid rate limiting
        if i < len(text_list) - 1:  # Don't delay after the last request
            time.sleep(delay)
    
    return results