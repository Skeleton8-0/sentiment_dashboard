import yake
import re
from collections import Counter

def extract_keywords(text, top_n=5, language="en"):
    """Extract keywords using YAKE algorithm"""
    try:
        kw_extractor = yake.KeywordExtractor(lan=language, n=1, top=top_n)
        keywords = kw_extractor.extract_keywords(text)
        return [kw for kw, score in keywords]
    except Exception as e:
        # Fallback to simple frequency-based extraction
        return extract_keywords_simple(text, top_n)

def extract_keywords_simple(text, max_keywords=5):
    """Fallback simple keyword extraction using frequency analysis"""
    # Remove punctuation and convert to lowercase
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those'
    }
    
    # Split into words and filter
    words = [word for word in clean_text.split() if word not in stop_words and len(word) > 2]
    
    # Count frequency and return top keywords
    word_counts = Counter(words)
    return [word for word, count in word_counts.most_common(max_keywords)]

def explain_sentiment(result):
    """
    Takes the output from analyze_sentiment() and returns a readable explanation.
    """
    if isinstance(result, dict) and "error" in result:
        return "Sentiment could not be analyzed due to an API error."
    
    if not result or not isinstance(result, list):
        return "No sentiment data available."

    top = result[0]  # The most confident label
    label = top["label"]
    score = top["score"]
    return f"The model is {round(score * 100, 1)}% confident that this text is {label.lower()}."
