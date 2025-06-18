import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import StringIO
import docx2txt
import fitz
import tempfile
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import batch_analyze_sentiment_with_keywords
from utils.text_processing import explain_sentiment
from components.data_visualization import (
    compute_sentiment_distribution,
    plot_sentiment_distribution_bar,
    plot_sentiment_distribution_pie,
    plot_sentiment_line_chart,
    results_to_dataframe
)
from export.export_csv import create_csv_download_link
from export.export_json import export_to_json
from export.export_pdf import export_to_pdf

# --- Page Config ---
st.set_page_config(page_title="Senti-Bru", layout="wide")

# --- Beautiful Custom Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        font-family: 'Inter', sans-serif;
    }
    .main-content {
        background: none;
        margin: 0;
        padding: 0 2rem;
        padding-top: 0;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0;
    }
    div.stApp > div:first-child {
        padding-top: 0 !important;
    }
    .element-container:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #333;
        margin-top: 0rem;
        margin-bottom: 0.5rem;
    }
    .section-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .logo-banner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 0.5rem;
        margin-top: 0;
        padding-top: 0;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card:hover {
        transform: scale(1.05);
        transition: 0.3s;
    }
    .stTextArea textarea {
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Information ---
with st.sidebar:
    st.markdown("## ℹ️ About Senti-Bru")
    st.markdown("""
    **Senti-Bru** is a powerful sentiment analysis tool that helps you:
    
    - 📊 Analyze text sentiment (positive, neutral, negative)
    - 🔍 Extract key words from your content
    - 📈 Visualize results with interactive charts
    - 💾 Export results in multiple formats

    **Supported file formats:**
    - `.txt` - Plain text files
    - `.pdf` - PDF documents  
    - `.docx` - Word documents

    **API:** Powered by HuggingFace's RoBERTa model
    """)

# --- Main App Container ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- Top Logo and Title ---
st.markdown('<div class="logo-banner">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("logo.png", width=180)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<h1 class="section-title">Senti-Bru</h1>', unsafe_allow_html=True)
st.markdown("<div class=\"section-subtitle\">What's your sentiment?</div>", unsafe_allow_html=True)

# --- Check for API Key ---
if not os.getenv('HUGGINGFACE_API_KEY'):
    st.error("🔑 HuggingFace API key not found! Please set HUGGINGFACE_API_KEY in your .env file.")
    st.stop()

# --- Input Section ---
st.markdown("### 📝 Enter or Upload Text")

tab1, tab2 = st.tabs(["✍️ Manual Entry", "📁 Upload File"])
texts = []

with tab1:
    user_input = st.text_area("Enter one comment per line:", height=200, key="manual_text_input")
    if user_input:
        texts = [line.strip() for line in user_input.splitlines() if line.strip()]
    
    # --- Analysis Settings ---
    if user_input:
        texts = [line.strip() for line in user_input.splitlines() if line.strip()]
        st.markdown("### ⚙️ Analysis Settings")
        delay = st.slider("Delay between API calls (seconds)", 0.5, 3.0, 1.0, 0.5, key="manual_delay_slider")
        st.info(f"⏱️ Estimated analysis time: {len(texts) * delay:.1f} seconds")
    else:
        delay = st.slider("Delay between API calls (seconds)", 0.5, 3.0, 1.0, 0.5, key="manual_delay_slider_disabled")
    
    analyze = st.button("✨ How does it feel?", type="primary", disabled=not user_input, key="manual_analyze_button")

    if analyze and user_input:
        texts = [line.strip() for line in user_input.splitlines() if line.strip()]
        with st.spinner("🔍 Analyzing sentiment and extracting keywords..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = batch_analyze_sentiment_with_keywords(
                texts, 
                delay=delay, 
                progress_callback=lambda i, total: progress_bar.progress(i / total)
            )
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")
        st.success("🎉 Analysis completed successfully!")

        counts, percentages = compute_sentiment_distribution(results)
        df = results_to_dataframe(results)

        # --- Metrics ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total</h3><h2>{len(results)}</h2>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>😊 Positive</h3><h2>{percentages.get('positive', 0):.1f}%</h2>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>😐 Neutral</h3><h2>{percentages.get('neutral', 0):.1f}%</h2>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>😞 Negative</h3><h2>{percentages.get('negative', 0):.1f}%</h2>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # --- Visualization ---
        st.markdown("### 📊 Visualization")
        viz_col1, viz_col2 = st.columns(2)
        with viz_col1:
            st.plotly_chart(plot_sentiment_distribution_bar(counts), use_container_width=True)
        with viz_col2:
            st.plotly_chart(plot_sentiment_distribution_pie(counts), use_container_width=True)

        st.markdown("#### 📈 Sentiment Trend Over Inputs")
        st.plotly_chart(plot_sentiment_line_chart(df), use_container_width=True)

        # --- Table ---
        st.markdown("### 📋 Detailed Results")
        st.dataframe(df, use_container_width=True)

        # --- Export ---
        st.markdown("### 📤 Export Results")
        col_csv, col_json, col_pdf = st.columns(3)
        with col_csv:
            st.download_button("⬇️ Download CSV", create_csv_download_link(df), "sentiment_results.csv", "text/csv", key="manual_csv_download")
        with col_json:
            json_data = df.to_json(orient="records", indent=2)
            st.download_button("⬇️ Download JSON", json_data, "sentiment_results.json", "application/json", key="manual_json_download")
        with col_pdf:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_filename = export_to_pdf(df, tmp_file.name, counts=counts)
                    with open(pdf_filename, "rb") as f:
                        pdf_data = f.read()
                    st.download_button("⬇️ Download PDF", pdf_data, "sentiment_results.pdf", "application/pdf", key="manual_pdf_download")
                    os.unlink(pdf_filename)
            except Exception as e:
                st.error(f"PDF export error: {str(e)}")

with tab2:
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx"], key="file_uploader")
    
    # Initialize texts variable
    texts = []
    
    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1].lower()
        content = ""
        try:
            if file_type == "txt":
                content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            elif file_type == "docx":
                content = docx2txt.process(uploaded_file)
            elif file_type == "pdf":
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page in pdf:
                    content += page.get_text()
                pdf.close()
            if content:
                texts = [line.strip() for line in content.splitlines() if line.strip()]
                st.success(f"✅ Extracted {len(texts)} lines from {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

    # --- Analysis Settings ---
    if uploaded_file and texts:
        st.markdown("### ⚙️ Analysis Settings")
        delay = st.slider("Delay between API calls (seconds)", 0.5, 3.0, 1.0, 0.5, key="upload_delay_slider")
        st.info(f"⏱️ Estimated analysis time: {len(texts) * delay:.1f} seconds")
    else:
        delay = st.slider("Delay between API calls (seconds)", 0.5, 3.0, 1.0, 0.5, key="upload_delay_slider_disabled")
    
    analyze = st.button("✨ How does it feel?", type="primary", disabled=not uploaded_file, key="upload_analyze_button")
    
    if analyze and texts:
        with st.spinner("🔍 Analyzing sentiment and extracting keywords..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = batch_analyze_sentiment_with_keywords(
                texts, 
                delay=delay, 
                progress_callback=lambda i, total: progress_bar.progress(i / total)
            )
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")
        st.success("🎉 Analysis completed successfully!")

        counts, percentages = compute_sentiment_distribution(results)
        df = results_to_dataframe(results)

        # --- Metrics ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total</h3><h2>{len(results)}</h2>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>😊 Positive</h3><h2>{percentages.get('positive', 0):.1f}%</h2>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>😐 Neutral</h3><h2>{percentages.get('neutral', 0):.1f}%</h2>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>😞 Negative</h3><h2>{percentages.get('negative', 0):.1f}%</h2>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # --- Visualization ---
        st.markdown("### 📊 Visualization")
        viz_col1, viz_col2 = st.columns(2)
        with viz_col1:
            st.plotly_chart(plot_sentiment_distribution_bar(counts), use_container_width=True)
        with viz_col2:
            st.plotly_chart(plot_sentiment_distribution_pie(counts), use_container_width=True)

        st.markdown("#### 📈 Sentiment Trend Over Inputs")
        st.plotly_chart(plot_sentiment_line_chart(df), use_container_width=True)

        # --- Table ---
        st.markdown("### 📋 Detailed Results")
        st.dataframe(df, use_container_width=True)

        # --- Export ---
        st.markdown("### 📤 Export Results")
        col_csv, col_json, col_pdf = st.columns(3)
        with col_csv:
            st.download_button("⬇️ Download CSV", create_csv_download_link(df), "sentiment_results.csv", "text/csv", key="upload_csv_download")
        with col_json:
            json_data = df.to_json(orient="records", indent=2)
            st.download_button("⬇️ Download JSON", json_data, "sentiment_results.json", "application/json", key="upload_json_download")
        with col_pdf:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_filename = export_to_pdf(df, tmp_file.name, counts=counts)
                    with open(pdf_filename, "rb") as f:
                        pdf_data = f.read()
                    st.download_button("⬇️ Download PDF", pdf_data, "sentiment_results.pdf", "application/pdf", key="upload_pdf_download")
                    os.unlink(pdf_filename)
            except Exception as e:
                st.error(f"PDF export error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
