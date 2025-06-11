import yake

def extract_keywords(text, top_n=5, language="en"):
    kw_extractor = yake.KeywordExtractor(lan=language, n=1, top=top_n)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]

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
