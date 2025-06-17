from fpdf import FPDF
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import os
import base64
from io import BytesIO

class SentimentPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Senti-Bru Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_bar_chart_for_pdf(counts):
    """Create bar chart and save as image for PDF"""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    
    sentiments = list(counts.keys())
    values = list(counts.values())
    colors = {'positive': '#28a745', 'neutral': '#ffc107', 'negative': '#dc3545'}
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(sentiments, values, color=[colors.get(s, '#cccccc') for s in sentiments])
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title('Sentiment Distribution - Bar Chart', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Sentiment', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Capitalize sentiment labels
    ax.set_xticklabels([s.capitalize() for s in sentiments])
    
    plt.tight_layout()
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, dpi=300, bbox_inches='tight')
    plt.close()
    
    return temp_file.name

def create_pie_chart_for_pdf(counts):
    """Create pie chart and save as image for PDF"""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    
    sentiments = list(counts.keys())
    values = list(counts.values())
    colors = ['#28a745' if s == 'positive' else '#ffc107' if s == 'neutral' else '#dc3545' for s in sentiments]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Create pie chart with percentages
    wedges, texts, autotexts = ax.pie(values, labels=[s.capitalize() for s in sentiments], 
                                      colors=colors, autopct='%1.1f%%', startangle=90)
    
    # Beautify the text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    for text in texts:
        text.set_fontsize(12)
        text.set_fontweight('bold')
    
    ax.set_title('Sentiment Distribution - Pie Chart', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, dpi=300, bbox_inches='tight')
    plt.close()
    
    return temp_file.name

def create_line_chart_for_pdf(df):
    """Create line chart and save as image for PDF"""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    
    # Create a copy and add index
    df_copy = df.copy()
    df_copy['Index'] = range(1, len(df_copy) + 1)
    
    # Map sentiments to numeric values for plotting
    sentiment_map = {'Positive': 2, 'Neutral': 1, 'Negative': 0}
    df_copy['sentiment_numeric'] = df_copy['sentiment'].map(sentiment_map)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create line plot
    ax.plot(df_copy['Index'], df_copy['sentiment_numeric'], 
            marker='o', linewidth=2, markersize=6, color='#007bff')
    
    # Customize the plot
    ax.set_title('Sentiment Trend Over Inputs', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Text Number', fontsize=12)
    ax.set_ylabel('Sentiment', fontsize=12)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Negative', 'Neutral', 'Positive'])
    ax.grid(True, alpha=0.3)
    
    # Add some styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, dpi=300, bbox_inches='tight')
    plt.close()
    
    return temp_file.name

def export_to_pdf(data, filename=None, counts=None):
    """Export sentiment data to PDF file with graphs"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_analysis_{timestamp}.pdf"
    
    pdf = SentimentPDF()
    pdf.add_page()
    
    # Add title and summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 10, f"Total Texts Analyzed: {len(data)}", 0, 1)
    pdf.ln(10)
    
    # Add graphs if counts provided
    if counts is not None:
        try:
            # Add Bar Chart
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "1. Bar Chart", 0, 1)
            pdf.ln(5)
            
            bar_chart_path = create_bar_chart_for_pdf(counts)
            pdf.image(bar_chart_path, x=10, y=pdf.get_y(), w=190)
            pdf.ln(120)  # Move down after image
            os.unlink(bar_chart_path)  # Clean up temp file
            
            # Add new page for pie chart
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "2. Pie Chart", 0, 1)
            pdf.ln(5)
            
            pie_chart_path = create_pie_chart_for_pdf(counts)
            pdf.image(pie_chart_path, x=10, y=pdf.get_y(), w=190)
            pdf.ln(120)  # Move down after image
            os.unlink(pie_chart_path)  # Clean up temp file
            
            # Add new page for line chart
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "3. Line Chart", 0, 1)
            pdf.ln(5)
            
            line_chart_path = create_line_chart_for_pdf(data)
            pdf.image(line_chart_path, x=10, y=pdf.get_y(), w=190)
            pdf.ln(120)  # Move down after image
            os.unlink(line_chart_path)  # Clean up temp file
            
        except Exception as e:
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, f"Error generating charts: {str(e)}", 0, 1)
            pdf.ln(5)
    
    # Add new page for data table
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. Detailed Analysis Results", 0, 1)
    pdf.ln(10)

    # Add table headers
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(10, 8, "#", 1)
    pdf.cell(80, 8, "Text", 1)
    pdf.cell(25, 8, "Sentiment", 1)
    pdf.cell(25, 8, "Confidence", 1)
    pdf.cell(50, 8, "Keywords", 1)
    pdf.ln()

    # Add data rows
    pdf.set_font("Arial", size=8)
    for index, row in data.iterrows():
        if pdf.get_y() > 250:  # Check if we need a new page
            pdf.add_page()
            # Re-add headers on new page
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(10, 8, "#", 1)
            pdf.cell(80, 8, "Text", 1)
            pdf.cell(25, 8, "Sentiment", 1)
            pdf.cell(25, 8, "Confidence", 1)
            pdf.cell(50, 8, "Keywords", 1)
            pdf.ln()
            pdf.set_font("Arial", size=8)

        # Truncate text if too long and handle Unicode properly
        text = str(row['text'])[:50] + "..." if len(str(row['text'])) > 50 else str(row['text'])
        # Clean text by removing problematic Unicode characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        keywords = str(row['keywords'])[:30] + "..." if len(str(row['keywords'])) > 30 else str(row['keywords'])
        keywords = keywords.encode('ascii', 'ignore').decode('ascii')
        
        pdf.cell(10, 8, str(index + 1), 1)
        pdf.cell(80, 8, text, 1)
        pdf.cell(25, 8, str(row['sentiment']), 1)
        pdf.cell(25, 8, str(row['confidence']), 1)
        pdf.cell(50, 8, keywords, 1)
        pdf.ln()

    pdf.output(filename)
    return filename