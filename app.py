import streamlit as st
from utils.api_client import batch_analyze_sentiment_with_keywords
from utils.text_processing import explain_sentiment
from components.data_visualization import (
    compute_sentiment_distribution,
    plot_sentiment_distribution_bar,
    plot_sentiment_distribution_pie,
    results_to_dataframe
)
from export.export_csv import create_csv_download_link
from export.export_json import export_to_json
from export.export_pdf import export_to_pdf

from io import StringIO
import docx2txt
import fitz  # PyMuPDF
import os
import tempfile

# --- Page Config & Header ---
st.set_page_config(page_title="Senti-Bru", layout="wide")

st.markdown(
    """
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 700;
            color: #4A90E2;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">💬 Senti-Bru</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload your texts or enter them manually to get real-time sentiment analysis, keyword extraction, and downloadable insights.</div>', unsafe_allow_html=True)
st.markdown("---")

# Check for API key
if not os.getenv('HUGGINGFACE_API_KEY'):
    st.error("🔑 HuggingFace API key not found! Please set HUGGINGFACE_API_KEY in your .env file.")
    st.stop()

# --- Input Section ---
st.markdown("### 📝 Input Your Text")
st.markdown("Choose to either manually enter your text or upload a file (`.txt`, `.pdf`, `.docx`).")

tab1, tab2 = st.tabs(["✍️ Manual Entry", "📁 Upload File"])

texts = []

# --- Manual Entry ---
with tab1:
    user_input = st.text_area(
        "Enter one comment per line:",
        height=200,
        placeholder="e.g. I love this product!\nThe experience was frustrating..."
    )
    if user_input:
        texts = [line.strip() for line in user_input.splitlines() if line.strip()]
        st.info(f"📊 Ready to analyze {len(texts)} texts")

# --- File Upload ---
with tab2:
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "docx"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()
        content = ""

        try:
            if file_type == "txt":
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                content = stringio.read()

            elif file_type == "docx":
                content = docx2txt.process(uploaded_file)

            elif file_type == "pdf":
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page in pdf:
                    content += page.get_text()
                pdf.close()

            if content:
                texts = [line.strip() for line in content.splitlines() if line.strip()]
                st.success(f"✅ Extracted {len(texts)} lines of text from {uploaded_file.name}")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

# --- Analysis Settings ---
if texts:
    st.markdown("### ⚙️ Analysis Settings")
    delay = st.slider("Delay between API calls (seconds)", 0.5, 3.0, 1.0, 0.5)
    st.info(f"⏱️ Estimated analysis time: {len(texts) * delay:.1f} seconds")

# --- Analyze Button ---
analyze = st.button("✨ How does it feel?", type="primary", disabled=not texts)

if analyze and texts:
    with st.spinner("🔍 Analyzing sentiment and extracting keywords..."):
        # Add progress tracking
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

    # --- Results Section ---
    st.markdown("## 📝 Analysis Results")

    # --- Sentiment Summary Blocks ---
    counts, percentages = compute_sentiment_distribution(results)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Texts Analyzed", len(results))
    col2.metric("Positive %", f"{percentages.get('positive', 0):.1f}%")
    col3.metric("Neutral %", f"{percentages.get('neutral', 0):.1f}%")
    col4.metric("Negative %", f"{percentages.get('negative', 0):.1f}%")

    st.markdown("---")

    # --- Visualization ---
    st.markdown("### 📊 Visualization")
    viz_col1, viz_col2 = st.columns(2)
    with viz_col1:
        st.plotly_chart(plot_sentiment_distribution_bar(counts), use_container_width=True)
    with viz_col2:
        st.plotly_chart(plot_sentiment_distribution_pie(counts), use_container_width=True)

    st.markdown("---")

    # --- Detailed Results Table ---
    st.markdown("### 📋 Detailed Results")
    df = results_to_dataframe(results)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # --- Export Options ---
    st.markdown("### 📤 Export Results")
    col_csv, col_json, col_pdf = st.columns(3)

    with col_csv:
        csv_data = create_csv_download_link(df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="sentiment_results.csv",
            mime="text/csv"
        )
    
    with col_json:
        json_data = df.to_json(orient="records", indent=2)
        st.download_button(
            label="⬇️ Download JSON", 
            data=json_data,
            file_name="sentiment_results.json",
            mime="application/json"
        )
    
    with col_pdf:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                pdf_filename = export_to_pdf(df, tmp_file.name)
                with open(pdf_filename, "rb") as f:
                    pdf_data = f.read()
                
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_data,
                    file_name="sentiment_results.pdf",
                    mime="application/pdf"
                )
                
                # Clean up temp file
                os.unlink(pdf_filename)
        except Exception as e:
            st.error(f"PDF export error: {str(e)}")

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
    
    if texts:
        st.markdown(f"**Current session:** {len(texts)} texts ready")

    elif not texts and not analyze:
        st.info("👆 Please enter some text or upload a file to get started!")