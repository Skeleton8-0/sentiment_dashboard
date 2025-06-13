from fpdf import FPDF

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Sentiment Analysis Report', 0, 1, 'C')
        self.ln(10)
        self.set_font('Arial', size=10)

def export_to_pdf(df):
    pdf = PDF()

    # Define column widths and row height
    col_widths = {'Text': 90, 'Sentiment': 30, 'Confidence': 25, 'Keywords': 45}
    row_height = 6

    # Header row
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 10)
    for col in ['Text', 'Sentiment', 'Confidence', 'Keywords']:
        pdf.cell(col_widths[col], row_height, col, 1, 0, 'C', 1)
    pdf.ln()

    # Data rows
    pdf.set_font('Arial', size=8)
    for _, row in df.iterrows():
        start_y = pdf.get_y()
        start_x = pdf.get_x()

        # Text column (multi-cell)
        pdf.multi_cell(col_widths['Text'], row_height, str(row['Text']), 1, 'L', 0)

        # Height of multi_cell content
        text_height = pdf.get_y() - start_y

        # Set position for next columns
        pdf.set_xy(start_x + col_widths['Text'], start_y)

        # Other columns
        pdf.cell(col_widths['Sentiment'], text_height, str(row['Sentiment']), 1, 0, 'C', 0)
        pdf.cell(col_widths['Confidence'], text_height, f"{row['Confidence']:.0f}%", 1, 0, 'C', 0)
        pdf.cell(col_widths['Keywords'], text_height, str(row['Keywords']), 1, 0, 'L', 0)

        # Move to next line
        pdf.set_xy(start_x, start_y + text_height)

    # Export PDF to string and encode it for Streamlit download
    pdf_output = pdf.output(dest='S').encode('latin1')  # Convert to bytes
    return pdf_output
