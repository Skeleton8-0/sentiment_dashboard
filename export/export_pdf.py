from fpdf import FPDF
import pandas as pd
from datetime import datetime

class SentimentPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Senti-Bru Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def export_to_pdf(data, filename=None):
    """Export sentiment data to PDF file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_analysis_{timestamp}.pdf"
    
    pdf = SentimentPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Add summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 10, f"Total Texts Analyzed: {len(data)}", 0, 1)
    pdf.ln(5)

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