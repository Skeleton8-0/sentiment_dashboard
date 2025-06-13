import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO # Import BytesIO
import base64
import json
from datetime import datetime
import time
from fpdf import FPDF
import os

# --- Mock/Fallback for components. This section is crucial because your actual components
# --- were not provided, and the previous setup had issues with imports.
# --- In a real application, ensure your 'components' and 'utils' directories
# --- exist and contain the actual code for these functions.

# Fallback for data_visualization.py functions
def compute_sentiment_distribution(results):
    """
    Computes the distribution and percentage breakdown of sentiments.
    Adjusted to handle 'positive', 'negative', 'neutral' labels from results.
    """
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0} # Use capitalized for display consistency
    total = 0

    for r in results:
        sentiment_label = r.get("sentiment", "Neutral") # Default to Neutral if not found
        confidence_score = r.get("confidence", 0.0)

        # Apply confidence threshold logic if sentiment has a score attribute
        if isinstance(sentiment_label, list) and sentiment_label:
            top_sentiment = sentiment_label[0]
            if top_sentiment.get('score', 0.0) < 0.6:
                label_to_count = "Neutral"
            else:
                label_to_count = top_sentiment.get('label', 'Neutral').capitalize()
        else: # Simple string sentiment like 'positive' or 'neutral'
            label_to_count = sentiment_label.capitalize()

        if label_to_count in counts:
            counts[label_to_count] += 1
            total += 1
        else: # Handle cases where a new sentiment label might appear
            counts[label_to_count] = counts.get(label_to_count, 0) + 1
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
        sentiment_label = r.get("sentiment", "Neutral")
        confidence_score = r.get("confidence", 0.0)
        keywords = r.get("keywords", [])

        # Reapply confidence threshold logic for dataframe
        final_sentiment_label = sentiment_label
        if isinstance(sentiment_label, list) and sentiment_label:
            top_sentiment = sentiment_label[0]
            if top_sentiment.get('score', 0.0) < 0.6:
                final_sentiment_label = "Neutral"
            else:
                final_sentiment_label = top_sentiment.get('label', 'Neutral')
            confidence_score = top_sentiment.get('score', 0.0)
        else: # Simple string sentiment like 'positive' or 'neutral'
            final_sentiment_label = sentiment_label

        rows.append({
            "Text": r.get("text", "N/A"),
            "Sentiment": final_sentiment_label.capitalize(), # Capitalize for display
            "Confidence": round(confidence_score * 100, 2),
            "Keywords": ", ".join(keywords) if keywords else "N/A"
        })
    return pd.DataFrame(rows)

def plot_sentiment_distribution_bar(counts):
    df = pd.DataFrame(list(counts.items()), columns=["Sentiment", "Count"])
    fig = px.bar(df, x="Sentiment", y="Count", color="Sentiment",
                 color_discrete_map={"Positive": "green", "Neutral": "gray", "Negative": "red"},
                 title="Sentiment Distribution (Bar Chart)")
    return fig

def plot_sentiment_distribution_pie(counts):
    df = pd.DataFrame(list(counts.items()), columns=["Sentiment", "Count"])
    fig = px.pie(
        df,
        names="Sentiment",
        values="Count",
        title="Sentiment Distribution (Pie Chart)",
        color="Sentiment",
        color_discrete_map={
            "Positive": "green",
            "Neutral": "gray",
            "Negative": "red"
        }
    )
    return fig

# Fallback for api_client.py functions
def batch_analyze_sentiment_with_keywords(texts):
    """
    Mock function to simulate API call for sentiment and keyword analysis.
    This replaces your actual API client for this self-contained demo.
    """
    mock_results = []
    for i, text in enumerate(texts):
        sentiment = "neutral"
        confidence = 0.5
        keywords = []

        lower_text = text.lower()
        if "love" in lower_text or "great" in lower_text or "happy" in lower_text:
            sentiment = "positive"
            confidence = min(0.95, 0.7 + lower_text.count('!') * 0.05 + len(text)/1000)
            if "love" in lower_text: keywords.append("love")
            if "great" in lower_text: keywords.append("great")
        elif "hate" in lower_text or "bad" in lower_text or "terrible" in lower_text:
            sentiment = "negative"
            confidence = min(0.95, 0.7 + lower_text.count('!') * 0.05 + len(text)/1000)
            if "hate" in lower_text: keywords.append("hate")
            if "bad" in lower_text: keywords.append("bad")

        # Simulate a more complex sentiment object structure for compute_sentiment_distribution
        mock_results.append({
            "text": text,
            "sentiment": [{"label": sentiment, "score": confidence}], # API often returns list of sentiments
            "confidence": confidence, # Also include top-level for simpler access if needed
            "keywords": keywords if keywords else ["general"]
        })
    return mock_results

# Fallback for utils.text_processing.explain_sentiment
def explain_sentiment(sentiment_data):
    """
    Mock function to explain sentiment. Assumes sentiment_data can be a list or a string.
    """
    if isinstance(sentiment_data, list) and sentiment_data:
        label = sentiment_data[0].get('label', 'unknown')
        score = sentiment_data[0].get('score', 0.0)
    elif isinstance(sentiment_data, str):
        label = sentiment_data
        score = 0.0 # Placeholder score
    else:
        return "Unknown sentiment."

    if label.lower() == "positive":
        return f"Positive 😊 (Confidence: {score:.2f})"
    elif label.lower() == "negative":
        return f"Negative 😞 (Confidence: {score:.2f})"
    elif label.lower() == "neutral":
        return f"Neutral 😐 (Confidence: {score:.2f})"
    else:
        return f"Sentiment: {label.capitalize()} (Confidence: {score:.2f})"

# --- Export Functions (Integrated and adapted for Streamlit downloads) ---

# PDF Export Class and Function - CORRECTED FOR BYTESIO AND FONT CHECKS
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()

        # --- Define paths for both REGULAR and BOLD fonts ---
        # THIS HAS BEEN CHANGED TO 'fonts' (plural) TO MATCH YOUR DIRECTORY STRUCTURE
        # Use os.path.normpath to handle path separators consistently across OS
        base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "fonts", "ttf"))
        regular_font_path = os.path.join(base_path, "DejaVuSans.ttf")
        bold_font_path = os.path.join(base_path, "DejaVuSans-Bold.ttf")

        # --- Add the REGULAR font style ---
        if os.path.exists(regular_font_path):
            self.add_font("DejaVu", "", regular_font_path, uni=True)
        else:
            st.error(f"Error: Regular font file not found. Looked for '{regular_font_path}'. Please ensure 'DejaVuSans.ttf' is in 'fonts/ttf/' relative to app.py. PDF text might default to a basic font.")
            self.set_font('Arial', '', 10) # Fallback to a built-in font

        # --- Add the BOLD font style ---
        if os.path.exists(bold_font_path):
            self.add_font("DejaVu", "B", bold_font_path, uni=True)
        else:
            st.error(f"Error: Bold font file not found. Looked for '{bold_font_path}'. Please ensure 'DejaVuSans-Bold.ttf' is in 'fonts/ttf/' relative to app.py. PDF title and bold text will not be bold.")


        # --- Set the title font to the newly added BOLD style ---
        # Check if the bold font was successfully added before trying to use it
        if "DejaVu" in self.fonts and "B" in self.fonts["DejaVu"]:
            self.set_font("DejaVu", 'B', 16)
        else:
            self.set_font('Arial', 'B', 16) # Fallback to Arial Bold

        self.cell(0, 10, 'Sentiment Analysis Report', 0, 1, 'C')
        self.ln(10)
        
        # Set body font back to regular after the title.
        if "DejaVu" in self.fonts and "" in self.fonts["DejaVu"]:
            self.set_font("DejaVu", size=10)
        else:
            self.set_font('Arial', size=10)


def export_to_pdf(df):
    pdf = PDF()

    # Add table headers
    col_widths = {'Text': 90, 'Sentiment': 30, 'Confidence': 25, 'Keywords': 45}
    row_height = 6 # Standard row height for single-line cells

    # Draw header row
    pdf.set_fill_color(200, 220, 255) # Light blue background for header
    
    # Use DejaVu Bold if available, otherwise Arial Bold
    if "DejaVu" in pdf.fonts and "B" in pdf.fonts["DejaVu"]:
        pdf.set_font("DejaVu", 'B', 10)
    else:
        pdf.set_font('Arial', 'B', 10)

    for col in ['Text', 'Sentiment', 'Confidence', 'Keywords']:
        pdf.cell(col_widths[col], row_height, col, 1, 0, 'C', 1)
    pdf.ln()

    # Draw data rows
    # Use DejaVu Regular if available, otherwise Arial Regular
    if "DejaVu" in pdf.fonts and "" in pdf.fonts["DejaVu"]:
        pdf.set_font("DejaVu", size=8)
    else:
        pdf.set_font('Arial', size=8)

    for index, row in df.iterrows():
        # Before printing, check if a new page is needed. Add a buffer for the next line.
        # Adjusting the trigger to consider estimated row height more robustly
        text_content_width = pdf.get_string_width(str(row['Text']))
        # Estimate number of lines the text will take. Add a small buffer for safety.
        num_lines_for_text = (text_content_width // col_widths['Text']) + 1.5
        estimated_row_height = max(row_height, num_lines_for_text * pdf.font_size * 1.2 / pdf.k)

        # Check if adding this row would exceed the page bottom, including a margin
        if pdf.get_y() + estimated_row_height + pdf.b_margin > pdf.page_break_trigger:
            pdf.add_page()
            # Re-add headers on new page
            if "DejaVu" in pdf.fonts and "B" in pdf.fonts["DejaVu"]:
                pdf.set_font("DejaVu", 'B', 10)
            else:
                pdf.set_font('Arial', 'B', 10)
            for col in ['Text', 'Sentiment', 'Confidence', 'Keywords']:
                pdf.cell(col_widths[col], row_height, col, 1, 0, 'C', 1)
            pdf.ln()
            if "DejaVu" in pdf.fonts and "" in pdf.fonts["DejaVu"]:
                pdf.set_font("DejaVu", size=8)
            else:
                pdf.set_font('Arial', size=8)

        start_y = pdf.get_y()
        start_x = pdf.get_x()

        # Text column (multiline if too long)
        pdf.multi_cell(col_widths['Text'], row_height, str(row['Text']), 1, 'L', 0)
        
        # Get the actual height taken by the multi_cell
        actual_text_height = pdf.get_y() - start_y

        # Reset Y to the start of the row, and set X to where the next column should be
        pdf.set_xy(start_x + col_widths['Text'], start_y)

        # Draw other cells with the max height calculated from the text column
        pdf.cell(col_widths['Sentiment'], actual_text_height, str(row['Sentiment']), 1, 0, 'C', 0)
        pdf.cell(col_widths['Confidence'], actual_text_height, f"{row['Confidence']:.0f}%", 1, 0, 'C', 0)
        pdf.cell(col_widths['Keywords'], actual_text_height, str(row['Keywords']), 1, 0, 'L', 0)

        # Move to the next line for the next row, using the actual height of the current row's tallest cell
        pdf.set_xy(start_x, start_y + actual_text_height)

    # --- KEY CHANGE: Wrap the bytearray output in BytesIO ---
    # This ensures Streamlit's download_button receives a file-like object
    pdf_output_bytes = pdf.output(dest='S')
    return BytesIO(pdf_output_bytes)

# CSV Export Function
def export_to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

# JSON Export Function
def export_to_json_bytes(df):
    return df.to_json(orient='records', indent=2).encode('utf-8')


# Page configuration
st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); /* Pink Turquoise blend for app background */
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }
    /* Sidebar styling */
    .css-1d391kg { /* This targets the overall sidebar container */
        background: linear-gradient(135deg, #FF69B4, #40E0D0, #8A2BE2); /* Pink, Turquoise, Blue, Purple blend */
        padding-top: 2rem;
    }
    .sidebar .sidebar-content { /* This targets the actual content within the sidebar */
        background: linear-gradient(135deg, #FF69B4, #40E0D0, #8A2BE2); /* Pink, Turquoise, Blue, Purple blend */
    }
    /* Logo container in sidebar */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    /* Sidebar title styling */
    .sidebar-title {
        color: black; /* Changed to black */
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    /* Navigation styling */
    .nav-item {
        background: rgba(255,255,255,0.1); /* Slightly transparent white for navigation items */
        border-radius: 10px;
        margin: 0.5rem 0;
        padding: 0.75rem 1rem;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .nav-item:hover {
        background: rgba(255,255,255,0.2);
        transform: translateX(5px);
    }
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Keep active distinct if desired */
        border: 1px solid rgba(255,255,255,0.3);
    }
    /* Main content area */
    .main-content {
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        margin: 2rem;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    /* Galaxy animation background */
    .galaxy-bg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 255, 198, 0.3) 0%, transparent 50%);
        animation: galaxyMove 20s ease-in-out infinite;
        z-index: -1;
    }
    @keyframes galaxyMove {
        0%, 100% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.1); }
    }
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
    }
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-right: 1rem;
    }
    /* Phone GIF styling */
    .phone-gif {
        width: 60px;
        height: auto;
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    /* Cards styling */
    .analysis-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
        transition: transform 0.3s ease;
    }
    .analysis-card:hover {
        transform: translateY(-5px);
    }
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-color: #667eea;
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.2);
    }
    /* Buttons styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box_shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
    }
    /* Scroll indicator */
    .scroll-indicator {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        color: black; /* Changed to black */
        text-align: center;
        animation: scrollBounce 2s infinite;
    }
    @keyframes scrollBounce {
        0%, 20%, 50%, 80%, 100% { transform: translateX(-50%) translateY(0); }
        40% { transform: translateX(-50%) translateY(-10px); }
        60% { transform: translateX(-50%) translateY(-5px); }
    }
    /* Metrics styling - CHANGED TO WHITE BACKGROUND */
    .metric-card {
        background: white; /* Changed to white */
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* Added subtle shadow */
    }
    .metric-card:hover {
        transform: scale(1.05);
    }
    /* Input area styling */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        transition: border-color 0.3s ease;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.2);
    }
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 15px;
        border: 2px dashed #667eea;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.05);
    }
    /* Confidence explanation box */
    .confidence-explanation {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 5px solid #ff6b6b;
    }
    /* Hide streamlit elements */
    .css-1rs6os, .css-17ziqus { /* This hides the Streamlit "Made with Streamlit" footer */
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "selected_results" not in st.session_state:
    st.session_state.selected_results = []
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None
if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Bar Chart"
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Helper functions
def create_sample_results():
    """Create sample results for demonstration with sentiment list structure"""
    return [
        {"text": "I love this product! It's amazing.", "sentiment": [{"label": "positive", "score": 0.95}], "confidence": 0.95, "keywords": ["product", "amazing"]},
        {"text": "This is terrible, I hate it.", "sentiment": [{"label": "negative", "score": 0.88}], "confidence": 0.88, "keywords": ["terrible", "hate"]},
        {"text": "It's okay, nothing special.", "sentiment": [{"label": "neutral", "score": 0.72}], "confidence": 0.72, "keywords": ["okay", "nothing special"]},
        {"text": "Great quality and fast delivery!", "sentiment": [{"label": "positive", "score": 0.92}], "confidence": 0.92, "keywords": ["quality", "delivery"]},
        {"text": "Could be better.", "sentiment": [{"label": "neutral", "score": 0.55}], "confidence": 0.55, "keywords": ["better"]},
    ]

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == "txt":
            return str(uploaded_file.read(), "utf-8")
        elif file_extension in ["pdf", "docx", "png", "jpeg", "jpg"]:
            st.warning(f"File type '{file_extension}' detected. Advanced processing for this type is not included in this demo.")
            return "File content for advanced formats not parsed in demo."
    return ""

def get_base64_image(image_path):
    """Get base64 encoded image for embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Error: Logo file not found at {image_path}. Please ensure 'Logo.png' is in the same directory.")
        return None

# Get base64 encoded logo
logo_base64 = get_base64_image("Logo.png")

# Sidebar Navigation
with st.sidebar:
    # Logo
    if logo_base64:
        st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" alt="Company Logo" style="width: 150px; height: auto;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-container">
            <div style="width: 100px; height: 100px;background: linear-gradient(135deg, #FF69B4, #40E0D0, #8A2BE2);
                             border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white;
                             font-weight: bold; font-size: 20px;">LOGO</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">Sentiment Analysis Tool</div>', unsafe_allow_html=True)

    st.markdown("### Navigation", unsafe_allow_html=True)

    if st.button("📊 Dashboard", key="nav_dashboard", help="Main dashboard with analysis tools"):
        st.session_state.current_page = "Dashboard"

    if st.button("🎯 Confidence Score Breakdown", key="nav_confidence", help="Detailed confidence score explanation"):
        st.session_state.current_page = "Confidence"

# Main content area
st.markdown('<div class="main-content galaxy-bg">', unsafe_allow_html=True)

# DASHBOARD PAGE
if st.session_state.current_page == "Dashboard":
    st.markdown("""
    <div class="section-header">
        <h1 class="section-title">📊 Dashboard</h1>
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                     border-radius: 10px; display: flex; align-items: center; justify-content: center;
                     color: white; font-size: 24px; animation: bounce 2s infinite;">📱</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📝 Input Form")

    user_input = st.text_area(
        "Enter text for sentiment analysis (one per line for batch):",
        height=150,
        placeholder="Type your text here or upload a file below..."
    )

    st.markdown("### 📁 Or upload a file:")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'pdf', 'docx', 'png', 'jpeg', 'jpg'],
        help="Supported formats: TXT (fully supported), PDF, DOCX, PNG, JPEG (basic file parsing for other types, advanced content extraction not included in demo)."
    )

    texts_to_analyze = []
    if uploaded_file is not None:
        file_text = process_uploaded_file(uploaded_file)
        if file_text and file_text != "File content for advanced formats not parsed in demo.":
            texts_to_analyze = [line for line in file_text.strip().split("\n") if line]
        elif user_input.strip():
            texts_to_analyze = [line for line in user_input.strip().split("\n") if line]
        else:
            st.info("Please enter text manually or upload a .txt file for full analysis in this demo.")
    elif user_input.strip():
        texts_to_analyze = [line for line in user_input.strip().split("\n") if line]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Sentiment", key="main_analyze"):
            if not texts_to_analyze:
                st.warning("⚠️ Please enter some text or upload a .txt file before running analysis.")
                st.session_state.analysis_results = None
            else:
                with st.spinner("🔍 Analyzing sentiment..."):
                    try:
                        results = batch_analyze_sentiment_with_keywords(texts_to_analyze)
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {e}. Falling back to sample results.")
                        results = create_sample_results()
                    st.session_state.analysis_results = results
                    st.success("✅ Analysis completed!")

    if st.session_state.analysis_results:
        st.markdown("---")
        st.markdown("## 📈 Analysis Results")

        counts, percentages = compute_sentiment_distribution(st.session_state.analysis_results)
        df = results_to_dataframe(st.session_state.analysis_results)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Total Analyzed</h3>
                <h2>{}</h2>
            </div>
            """.format(len(df)), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>😊 Positive</h3>
                <h2>{}%</h2>
            </div>
            """.format(round(percentages.get("Positive", 0))), unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>😐 Neutral</h3>
                <h2>{}%</h2>
            </div>
            """.format(round(percentages.get("Neutral", 0))), unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>😞 Negative</h3>
                <h2>{}%</h3>
            </div>
            """.format(round(percentages.get("Negative", 0))), unsafe_allow_html=True)

        st.markdown("### 📊 Visualization")
        chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart"])

        if chart_type == "Bar Chart":
            fig = plot_sentiment_distribution_bar(counts)
        else:
            fig = plot_sentiment_distribution_pie(counts)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Detailed Results")
        st.dataframe(df, use_container_width=True)

        st.markdown("### 📄 Export Results")
        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = export_to_csv_bytes(df)
            st.download_button(
                "📊 Export CSV",
                csv_data,
                f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )

        with col2:
            json_data = export_to_json_bytes(df)
            st.download_button(
                "📋 Export JSON",
                json_data,
                f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )

        with col3:
            pdf_data = export_to_pdf(df)
            st.download_button(
                "📄 Export PDF",
                pdf_data,
                f"sentiment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "application/pdf"
            )

elif st.session_state.current_page == "Confidence":
    st.markdown("""
    <div class="section-header">
        <h1 class="section-title">🎯 Confidence Score Breakdown</h1>
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                     border-radius: 10px; display: flex; align-items: center; justify-content: center;
                     color: white; font-size: 24px; animation: bounce 2s infinite;">📱</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="confidence-explanation">
        <h2>🧠 How Confidence Scores Are Calculated</h2>
        <p>Our sentiment analysis uses advanced machine learning models to determine both the sentiment and confidence level of text analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Confidence Score Components")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎯 Model Certainty
        - **High Confidence (0.8-1.0)**: Clear sentiment indicators
        - **Medium Confidence (0.6-0.8)**: Some ambiguity present
        - **Low Confidence (0.0-0.6)**: Unclear or neutral language (often categorized as Neutral by our system)
        """)

        st.markdown("""
        ### 📝 Text Features Analyzed
        - **Sentiment Words**: Positive/negative keywords
        - **Context**: Surrounding words and phrases
        - **Intensity**: Strength of emotional language (e.g., "very good" vs "good")
        - **Negation**: Words that flip sentiment meaning (e.g., "not good" vs "good")
        """)

    with col2:
        st.markdown("""
        ### 🔢 Score Calculation Process
        1. **Tokenization**: Break text into words/phrases
        2. **Feature Extraction**: Identify sentiment indicators
        3. **Model Prediction**: Apply trained algorithms
        4. **Probability Assessment**: Calculate certainty levels for each sentiment
        """)

        st.markdown("""
        ### ⚡ Factors Affecting Confidence
        - **Text Length**: Longer text usually provides more context for a more confident prediction.
        - **Ambiguous Language**: Sarcasm, irony, or highly subjective language can lower confidence.
        - **Mixed Sentiments**: Text expressing both positive and negative aspects can result in lower confidence for a single classification.
        - **Domain Specificity**: Analysis of highly specialized vocabulary might require domain-specific models for high confidence.
        """)

    st.markdown("## 🔬 Interactive Confidence Demo")

    demo_text = st.text_input("Enter text to see confidence analysis:",
                              placeholder="Try: 'I love this!' vs 'It's okay, I guess...' or 'The product is good, but the delivery was slow.'")

    if demo_text:
        demo_results = batch_analyze_sentiment_with_keywords([demo_text])
        if demo_results:
            first_result = demo_results[0]
            sentiment_data = first_result.get('sentiment', [{'label': 'neutral', 'score': 0.5}])[0]
            sentiment = sentiment_data.get('label', 'neutral')
            confidence = sentiment_data.get('score', 0.5)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Detected Sentiment", sentiment.capitalize())
            with col2:
                st.metric("Confidence Score", f"{confidence:.2f}")
            with col3:
                st.metric("Confidence Level",
                                "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low")
        else:
            st.info("No analysis result for the demo text. Try another input.")

    st.markdown("## 📈 Confidence Score Ranges")

    confidence_data = pd.DataFrame({
        'Range': ['0.0 - 0.3', '0.3 - 0.6', '0.6 - 0.8', '0.8 - 1.0'],
        'Level': ['Very Low', 'Low', 'Medium', 'High'],
        'Interpretation': [
            'Highly uncertain, conflicting signals, or purely factual/objective text.',
            'Uncertain, weak sentiment indicators, or very short/ambiguous text.',
            'Moderately confident, some ambiguity, or a slight lean towards a sentiment.',
            'Very confident, clear and strong sentiment expressed.'
        ],
        'Color': ['#ff4757', '#ff6348', '#ffa502', '#2ed573']
    })

    fig = go.Figure()
    for i, row in confidence_data.iterrows():
        fig.add_trace(go.Bar(
            name=row['Level'],
            x=[row['Range']],
            y=[1], # Dummy y-value for stacked bar
            marker_color=row['Color'],
            hovertemplate=f"<b>Level:</b> {row['Level']}<br><b>Range:</b> {row['Range']}<br><b>Interpretation:</b> {row['Interpretation']}<extra></extra>"
        ))

    fig.update_layout(
        barmode='stack',
        title_text='Confidence Score Levels and Interpretation',
        showlegend=True,
        xaxis_title="Confidence Score Range",
        yaxis_title="",
        yaxis_visible=False,
        yaxis_showticklabels=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)


st.markdown('</div>', unsafe_allow_html=True) # Close the main-content div
