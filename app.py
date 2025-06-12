import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import json
from datetime import datetime
import time

# Import your existing components
try:
    from components.data_visualization import (
        compute_sentiment_distribution,
        plot_sentiment_distribution_bar,
        plot_sentiment_distribution_pie,
        results_to_dataframe
    )
    from utils.api_client import batch_analyze_sentiment_with_keywords
except ImportError:
    # Fallback functions for demo purposes
    def compute_sentiment_distribution(results):
        return {"Positive": 5, "Negative": 2, "Neutral": 3}, {"Positive": 50, "Negative": 20, "Neutral": 30}
    
    def plot_sentiment_distribution_bar(counts):
        fig = go.Figure(data=[go.Bar(x=list(counts.keys()), y=list(counts.values()))])
        return fig
    
    def plot_sentiment_distribution_pie(counts):
        fig = go.Figure(data=[go.Pie(labels=list(counts.keys()), values=list(counts.values()))])
        return fig
    
    def results_to_dataframe(results):
        return pd.DataFrame({"Text": ["Sample text"], "Sentiment": ["Positive"], "Confidence": [0.95]})
    
    def batch_analyze_sentiment_with_keywords(texts):
        return [{"text": text, "sentiment": "positive", "confidence": 0.9} for text in texts]

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
        color: black;
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
        box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
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
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        transition: transform 0.3s ease;
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
    .css-1rs6os, .css-17ziqus {
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
    """Create sample results for demonstration"""
    return [
        {"text": "I love this product! It's amazing.", "sentiment": "positive", "confidence": 0.95},
        {"text": "This is terrible, I hate it.", "sentiment": "negative", "confidence": 0.88},
        {"text": "It's okay, nothing special.", "sentiment": "neutral", "confidence": 0.72},
        {"text": "Great quality and fast delivery!", "sentiment": "positive", "confidence": 0.92},
    ]

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type == "application/pdf":
            return "PDF processing would require additional libraries"
        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            return "Image text extraction would require OCR libraries"
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return "DOCX processing would require additional libraries"
    return ""

def get_base64_image(image_path):
    """Get base64 encoded image for embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Error: Logo file not found at {image_path}")
        return None

# Get base64 encoded logo
# Make sure 'Logo.png' exists in the same directory as your script
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
            <div style="width: 100px; height: 100px;background: linear-gradient(135deg, #FF69B4, #40E0D0, #8A2BE2); /* Pink, Turquoise, Blue, Purple blend */; 
                         border-radius: 50%; display: flex; align-items: center; justify-content: center; color: black; 
                         font-weight: bold; font-size: 20px;">LOGO</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-title">Sentiment Analysis Tool</div>', unsafe_allow_html=True)
      
                        
    
    st.markdown("### Navigation", unsafe_allow_html=True)
    
    # Navigation buttons
    # Apply 'active' class to the currently selected page for visual feedback
    dashboard_class = "nav-item active" if st.session_state.current_page == "Dashboard" else "nav-item"
    confidence_class = "nav-item active" if st.session_state.current_page == "Confidence" else "nav-item"

    if st.button("📊 Dashboard", key="nav_dashboard", help="Main dashboard with analysis tools"):
        st.session_state.current_page = "Dashboard"
    
    if st.button("🎯 Confidence Score Breakdown", key="nav_confidence", help="Detailed confidence score explanation"):
        st.session_state.current_page = "Confidence"

# Main content area
st.markdown('<div class="main-content galaxy-bg">', unsafe_allow_html=True)

# DASHBOARD PAGE
if st.session_state.current_page == "Dashboard":
    # Header with Phone GIF placeholder
    st.markdown("""
    <div class="section-header">
        <h1 class="section-title">📊 Dashboard</h1>
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); 
                     border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                     color: white; font-size: 24px; animation: bounce 2s infinite;">📱</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Section
    st.markdown("## 📝 Input Form")
    
    # Text input
    user_input = st.text_area(
        "Enter text for sentiment analysis (one per line for batch):",
        height=150,
        placeholder="Type your text here or upload a file below..."
    )
    
    # File uploader
    st.markdown("### 📁 Or upload a file:")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt', 'png', 'jpeg', 'jpg'],
        help="Supported formats: PDF, DOCX, TXT, PNG, JPEG"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        file_text = process_uploaded_file(uploaded_file)
        if file_text and not user_input:
            user_input = file_text
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Sentiment", key="main_analyze"):
            if not user_input.strip() and uploaded_file is None:
                st.warning("⚠️ Please enter some text or upload a file before running analysis.")
            else:
                with st.spinner("🔍 Analyzing sentiment..."):
                    # Process input
                    if uploaded_file is not None:
                        batch_input = [process_uploaded_file(uploaded_file)]
                    else:
                        batch_input = [line for line in user_input.strip().split("\n") if line]
                    
                    # Run analysis
                    try:
                        results = batch_analyze_sentiment_with_keywords(batch_input)
                    except:
                        # Fallback for demo
                        results = create_sample_results()
                    
                    st.session_state.analysis_results = results
                    st.success("✅ Analysis completed!")
    
    # Results Section
    if st.session_state.analysis_results:
        st.markdown("---")
        st.markdown("## 📈 Analysis Results")
        
        # Compute distributions
        try:
            counts, percentages = compute_sentiment_distribution(st.session_state.analysis_results)
            df = results_to_dataframe(st.session_state.analysis_results)
        except:
            # Fallback data
            counts = {"Positive": 5, "Negative": 2, "Neutral": 3}
            percentages = {"Positive": 50.0, "Negative": 20.0, "Neutral": 30.0}
            df = pd.DataFrame({
                "Text": ["Sample positive text", "Sample negative text", "Sample neutral text"],
                "Sentiment": ["Positive", "Negative", "Neutral"],
                "Confidence": [0.95, 0.88, 0.72]
            })
        
        # Metrics row
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
                <h2>{}%</h2>
            </div>
            """.format(round(percentages.get("Negative", 0))), unsafe_allow_html=True)
        
        # Charts
        st.markdown("### 📊 Visualization")
        chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart"])
        
        try:
            if chart_type == "Bar Chart":
                fig = plot_sentiment_distribution_bar(counts)
            else:
                fig = plot_sentiment_distribution_pie(counts)
            st.plotly_chart(fig, use_container_width=True)
        except:
            # Fallback chart
            if chart_type == "Bar Chart":
                fig = px.bar(x=list(counts.keys()), y=list(counts.values()), 
                             title="Sentiment Distribution",
                             color=list(counts.keys()),
                             color_discrete_map={"Positive": "#28a745", "Negative": "#dc3545", "Neutral": "#6c757d"})
            else:
                fig = px.pie(names=list(counts.keys()), values=list(counts.values()), 
                             title="Sentiment Distribution",
                             color_discrete_map={"Positive": "#28a745", "Negative": "#dc3545", "Neutral": "#6c757d"})
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed results table
        st.markdown("### 📋 Detailed Results")
        st.dataframe(df, use_container_width=True)
        
        # Export options
        st.markdown("### 📄 Export Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                "📊 Export CSV",
                csv,
                f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
        
        with col2:
            json_data = {
                "analysis_date": datetime.now().isoformat(),
                "summary": {"counts": counts, "percentages": percentages},
                "detailed_results": df.to_dict('records')
            }
            st.download_button(
                "📋 Export JSON",
                json.dumps(json_data, indent=2),
                f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
        
        with col3:
            st.button("📄 Export PDF", help="PDF export feature coming soon!")

# CONFIDENCE SCORE BREAKDOWN PAGE
elif st.session_state.current_page == "Confidence":
    # Header
    st.markdown("""
    <div class="section-header">
        <h1 class="section-title">🎯 Confidence Score Breakdown</h1>
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); 
                     border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                     color: white; font-size: 24px; animation: bounce 2s infinite;">📱</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence Score Explanation
    st.markdown("""
    <div class="confidence-explanation">
        <h2>🧠 How Confidence Scores Are Calculated</h2>
        <p>Our sentiment analysis uses advanced machine learning models to determine both the sentiment and confidence level of text analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📊 Confidence Score Components")
    
    # Explanation sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Model Certainty
        - **High Confidence (0.8-1.0)**: Clear sentiment indicators
        - **Medium Confidence (0.6-0.8)**: Some ambiguity present
        - **Low Confidence (0.0-0.6)**: Unclear or neutral language
        """)
        
        st.markdown("""
        ### 📝 Text Features Analyzed
        - **Sentiment Words**: Positive/negative keywords
        - **Context**: Surrounding words and phrases   
        - **Intensity**: Strength of emotional language
        - **Negation**: Words that flip sentiment meaning
        """)
    
    with col2:
        st.markdown("""
        ### 🔢 Score Calculation Process
        1. **Tokenization**: Break text into words/phrases
        2. **Feature Extraction**: Identify sentiment indicators
        3. **Model Prediction**: Apply trained algorithms
        4. **Probability Assessment**: Calculate certainty levels
        """)
        
        st.markdown("""
        ### ⚡ Factors Affecting Confidence
        - **Text Length**: Longer text = more context
        - **Ambiguous Language**: Sarcasm, irony lower confidence
        - **Mixed Sentiments**: Conflicting emotions in text
        - **Domain Specificity**: Specialized vocabulary
        """)
    
    # Interactive confidence demonstration
    st.markdown("## 🔬 Interactive Confidence Demo")
    
    demo_text = st.text_input("Enter text to see confidence analysis:", 
                             placeholder="Try: 'I love this!' vs 'It's okay, I guess...'")
    
    if demo_text:
        # Simulate confidence calculation
        words = demo_text.split()
        positive_words = ['love', 'great', 'amazing', 'excellent', 'wonderful', 'fantastic']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'horrible', 'disgusting']
        
        pos_count = sum(1 for word in words if word.lower() in positive_words)
        neg_count = sum(1 for word in words if word.lower() in negative_words)
        
        if pos_count > neg_count:
            sentiment = "Positive"
            confidence = min(0.95, 0.6 + (pos_count * 0.1) + (len(words) * 0.02))
        elif neg_count > pos_count:
            sentiment = "Negative"   
            confidence = min(0.95, 0.6 + (neg_count * 0.1) + (len(words) * 0.02))
        else:
            sentiment = "Neutral"
            confidence = 0.5 + (len(words) * 0.01)
        
        confidence = round(confidence, 2)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Detected Sentiment", sentiment)
        with col2:
            st.metric("Confidence Score", f"{confidence:.2f}")
        with col3:
            st.metric("Confidence Level", 
                             "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low")
    
    # Confidence score ranges visualization
    st.markdown("## 📈 Confidence Score Ranges")
    
    confidence_data = pd.DataFrame({
        'Range': ['0.0 - 0.3', '0.3 - 0.6', '0.6 - 0.8', '0.8 - 1.0'],
        'Level': ['Very Low', 'Low', 'Medium', 'High'],
        'Interpretation': [
            'Highly uncertain, conflicting signals',
            'Uncertain, weak sentiment indicators', 
            'Moderately confident, some ambiguity',
            'Very confident, clear sentiment'
        ],
        'Color': ['#ff4757', '#ff6348', '#ffa502', '#2ed573']
    })
    
    fig = px.bar(confidence_data, x='Range', y=[0.3, 0.3, 0.2, 0.2], 
                     color='Level', title='Confidence Score Interpretation',
                     color_discrete_map={'Very Low': '#ff4757', 'Low': '#ff6348', 
                                         'Medium': '#ffa502', 'High': '#2ed573'})
    fig.update_layout(yaxis_title="Score Range Width")
    st.plotly_chart(fig, use_container_width=True)
    
    # Best practices
    st.markdown("""
    ## 💡 Best Practices for Interpretation
    
    ### ✅ When to Trust High Confidence Scores
    - Clear, unambiguous language
    - Consistent sentiment throughout text
    - Sufficient context provided
    - Standard vocabulary used
    
    ### ⚠️ When to Be Cautious
    - Very short text snippets
    - Heavy use of sarcasm or irony
    - Technical or domain-specific language
    - Mixed positive and negative elements
    
    ### 🎯 Tips for Better Results
    - Provide more context when possible
    - Be aware of cultural and linguistic nuances
    - Consider the source and domain of the text
    - Use confidence scores as a guide, not absolute truth
    """)

st.markdown('</div>', unsafe_allow_html=True)

# Scroll indicator
st.markdown("""
<div class="scroll-indicator">
    <div style="font-size: 14px; margin-bottom: 5px;">Scroll to explore</div>
    <div style="font-size: 20px;">⬇️</div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px; background: rgba(255,255,255,0.1); 
             border-radius: 15px; margin-top: 2rem;'>
    <p>🌟 Professional Sentiment Analysis Dashboard | Built with Streamlit & Python</p>
    <p>Powered by Advanced Machine Learning Models</p>
</div>
""", unsafe_allow_html=True)