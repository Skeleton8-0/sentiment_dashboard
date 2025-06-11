import streamlit as st
from components.data_visualization import (
    compute_sentiment_distribution,
    plot_sentiment_distribution_bar,
    plot_sentiment_distribution_pie,
    results_to_dataframe
)
from utils.api_client import batch_analyze_sentiment_with_keywords
import pprint

st.set_page_config(page_title="Sentiment Analysis Visualizer", layout="wide")
st.title("📊 Sentiment Analysis Visualizer")

# Initialize session state for results and chart type
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Bar Chart"

# User input
user_input = st.text_area("Enter text for sentiment analysis (or one per line for batch):")

# Run sentiment analysis button
if st.button("🔍 Analyze Sentiment"):
    if not user_input.strip():
        st.warning("Please enter some text before running analysis.")
    else:
        # Process user input
        batch_input = [line for line in user_input.strip().split("\n") if line]
        results = batch_analyze_sentiment_with_keywords(batch_input)

        # DEBUG: Print raw sentiment results to terminal
        print("=== DEBUG: API Raw Results ===")
        pprint.pprint(results)

        # Store in session state
        st.session_state.analysis_results = results

# Display charts if analysis has been done
if st.session_state.analysis_results:
    st.subheader("📈 Sentiment Distribution")

    counts, percentages = compute_sentiment_distribution(st.session_state.analysis_results)
    df = results_to_dataframe(st.session_state.analysis_results)

    # Dropdown to choose chart type
    chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart"], index=["Bar Chart", "Pie Chart"].index(st.session_state.chart_type))
    st.session_state.chart_type = chart_type

    # Show selected chart
    if chart_type == "Bar Chart":
        fig = plot_sentiment_distribution_bar(counts)
    else:
        fig = plot_sentiment_distribution_pie(counts)
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Sentiment Counts:**")
    st.write(counts)

    st.markdown("**Sentiment Percentages:**")
    st.write(percentages)

    st.subheader("📋 Detailed Sentiment Table")
    st.dataframe(df, use_container_width=True)
