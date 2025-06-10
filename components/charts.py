import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import seaborn as sns

def create_sentiment_bar_chart(data):
    """Create a bar chart for sentiment distribution"""
    if isinstance(data, dict):
        # Single sentiment result
        fig = go.Figure(data=[
            go.Bar(x=['Sentiment'], y=[data.get('confidence', 0)], 
                   text=[data.get('sentiment', 'Unknown')],
                   textposition='auto')
        ])
        fig.update_layout(title='Sentiment Analysis Result', 
                         yaxis_title='Confidence %')
    else:
        # Multiple results
        sentiment_counts = data['sentiment'].value_counts()
        fig = px.bar(x=sentiment_counts.index, y=sentiment_counts.values,
                    title='Sentiment Distribution',
                    labels={'x': 'Sentiment', 'y': 'Count'})
    
    return fig

def create_sentiment_pie_chart(data):
    """Create a pie chart for sentiment distribution"""
    if isinstance(data, pd.DataFrame):
        sentiment_counts = data['sentiment'].value_counts()
        fig = px.pie(values=sentiment_counts.values, 
                    names=sentiment_counts.index,
                    title='Sentiment Distribution')
    return fig

def create_confidence_histogram(data):
    """Create histogram for confidence scores"""
    if isinstance(data, pd.DataFrame) and 'confidence' in data.columns:
        fig = px.histogram(data, x='confidence', 
                          title='Confidence Score Distribution',
                          nbins=20)
        fig.update_xaxis(title='Confidence Score')
        fig.update_yaxis(title='Frequency')
    return fig