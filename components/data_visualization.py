import pandas as pd
import plotly.express as px

def compute_sentiment_distribution(results):
    """
    Computes the distribution and percentage breakdown of sentiments,
    including neutral if present in the API response.
    """
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    total = 0

    for r in results:
        if "sentiment" in r and isinstance(r['sentiment'], list):
            sentiments = r['sentiment']
            top = sentiments[0]

            # Optional: Treat low confidence as neutral
            if top['score'] < 0.6:
                label = "neutral"
            else:
                label = top['label']

            if label in counts:
                counts[label] += 1
                total += 1
        elif "error" in r:
            # Count errors as neutral for now
            counts["neutral"] += 1
            total += 1

    if total == 0:
        return counts, {}

    percentages = {k: round((v / total) * 100, 2) for k, v in counts.items()}
    return counts, percentages

def results_to_dataframe(results):
    """
    Convert raw results to a DataFrame for charting/export.
    Uses confidence threshold to mark low-confidence as 'neutral'.
    """
    rows = []
    for r in results:
        if "sentiment" in r and isinstance(r['sentiment'], list):
            sentiments = r["sentiment"]
            top = sentiments[0]

            if top["score"] < 0.6:
                label = "neutral"
            else:
                label = top["label"]

            rows.append({
                "text": r["text"][:100] + "..." if len(r["text"]) > 100 else r["text"],
                "sentiment": label.title(),
                "confidence": f"{round(top['score'] * 100, 2)}%",
                "keywords": ", ".join(r.get("keywords", []))
            })
        else:
            # Handle error cases
            rows.append({
                "text": r["text"][:100] + "..." if len(r["text"]) > 100 else r["text"],
                "sentiment": "Error",
                "confidence": "N/A",
                "keywords": "N/A"
            })
    
    return pd.DataFrame(rows)

def plot_sentiment_distribution_bar(counts):
    """Create bar chart for sentiment distribution"""
    df = pd.DataFrame(list(counts.items()), columns=["Sentiment", "Count"])
    fig = px.bar(
        df, 
        x="Sentiment", 
        y="Count", 
        color="Sentiment",
        color_discrete_map={
            "positive": "#28a745", 
            "neutral": "#ffc107", 
            "negative": "#dc3545"
        },
        title="Sentiment Distribution"
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_sentiment_distribution_pie(counts):
    """Create pie chart for sentiment distribution"""
    df = pd.DataFrame(list(counts.items()), columns=["Sentiment", "Count"])
    fig = px.pie(
        df,
        names="Sentiment",
        values="Count",
        title="Sentiment Distribution",
        color="Sentiment",
        color_discrete_map={
            "positive": "#28a745",
            "neutral": "#ffc107",
            "negative": "#dc3545"
        }
    )
    return fig