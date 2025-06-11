from utils.api_client import batch_analyze_sentiment_with_keywords
from components.data_visualization import display_text_analysis, plot_sentiment_bar

texts = [
    "I love this product! It's excellent and very useful.",
    "It was okay, nothing special but decent overall.",
    "Terrible experience, will not buy again due to poor quality."
]

results = batch_analyze_sentiment_with_keywords(texts)

# Display in terminal
display_text_analysis(results)

# Optional: plot charts
plot_sentiment_bar(results)
