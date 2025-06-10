import streamlit as st

st.set_page_config(page_title="Sentiment Analysis Dashboard")
st.title("📊 Sentiment Analysis Dashboard")

text_input = st.text_area("Enter your text for sentiment analysis")

if st.button("Analyze"):
    st.write("🔍 Analyzing sentiment...")
    st.success("This is where results will appear.")
