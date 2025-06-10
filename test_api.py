from utils.api_client import batch_analyze_sentiment_with_keywords

texts = [
    "I love this product! It's excellent and very useful.",
    "It was okay, nothing special but decent overall.",
    "Terrible experience, will not buy again due to poor quality."
]

results = batch_analyze_sentiment_with_keywords(texts)
for r in results:
    print(f"Text: {r['text']}\nSentiment: {r.get('sentiment')}\nKeywords: {r.get('keywords')}\nError: {r.get('error')}\n")
