import streamlit as st
from utils.api_client import batch_analyze_sentiment_with_keywords
from utils.text_processing import explain_sentiment
from components.data_visualization import (
    compute_sentiment_distribution,
    plot_sentiment_distribution_bar,
    plot_sentiment_distribution_pie,
    results_to_dataframe
)
from export.export_csv import export_to_csv
from export.export_json import export_to_json
from export.export_pdf import export_to_pdf

st.set_page_config(page_title="AI Sentiment Dashboard", layout="wide")
st.title("💬 AI-Powered Sentiment Analyzer")
st.markdown("""
Welcome to the **AI Sentiment Dashboard**! Upload your texts or enter them manually,
and get real-time sentiment analysis along with keyword extraction, interactive charts,
and data export options.
""")

# --- Input Section ---
st.sidebar.header("🛠️ Input Options")
input_mode = st.sidebar.radio("Choose how to provide your text data:", ["Manual entry", "Upload .txt file"])

texts = []
if input_mode == "Manual entry":
    user_input = st.text_area("✍️ Enter one comment per line:", height=200)
    if user_input:
        texts = [line.strip() for line in user_input.splitlines() if line.strip()]
else:
    uploaded_file = st.sidebar.file_uploader("📄 Upload a .txt file", type=["txt"])
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        texts = [line.strip() for line in content.splitlines() if line.strip()]

# --- Analysis Button ---
if texts:
    if st.button("🚀 Analyze Texts"):
        with st.spinner("Analyzing sentiments and extracting keywords..."):
            results = batch_analyze_sentiment_with_keywords(texts)

            # --- Display Results ---
            st.subheader("🔍 Detailed Results")
            for res in results:
                with st.expander(f"💬 {res['text'][:80]}..."):
                    st.markdown(f"**Sentiment:** {explain_sentiment(res['sentiment'])}")
                    st.markdown(f"**Keywords:** `{', '.join(res['keywords'])}`")

            # --- Charts ---
            st.subheader("📊 Sentiment Overview")
            counts, percentages = compute_sentiment_distribution(results)
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_sentiment_distribution_bar(counts), use_container_width=True)
            with col2:
                st.plotly_chart(plot_sentiment_distribution_pie(counts), use_container_width=True)

            # --- Export Options ---
            st.subheader("📤 Export Results")
            df = results_to_dataframe(results)
            col_csv, col_json, col_pdf = st.columns(3)

            with col_csv:
                st.download_button(
                    "⬇️ Download CSV", export_to_csv(df), file_name="sentiment_results.csv", mime="text/csv")
            with col_json:
                st.download_button(
                    "⬇️ Download JSON", df.to_json(orient="records"), file_name="sentiment_results.json", mime="application/json")
            with col_pdf:
                pdf_path = export_to_pdf(df)
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=pdf_path, mime="application/pdf")
else:
    st.info("Please enter some text above or upload a file to begin analysis.")
