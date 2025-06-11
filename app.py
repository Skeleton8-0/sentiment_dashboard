import streamlit as st
from utils.api_client import analyze_sentiment
from utils.text_processing import extract_keywords, explain_sentiment

st.title("Sentiment Analyzer with Key Phrase Extraction")

user_input = st.text_area("Enter text to analyze:")

if st.button("Analyze"):
    if user_input:
        sentiment_result = analyze_sentiment(user_input)
        explanation = explain_sentiment(sentiment_result)
        keywords = extract_keywords(user_input)

        st.subheader("Sentiment Prediction")
        st.write(sentiment_result)

        st.subheader("Explanation")
        st.write(explanation)

        st.subheader("Extracted Keywords")
        st.write(", ".join(keywords))
    else:
        st.warning("Please enter some text.")
