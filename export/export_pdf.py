# export/export_pdf.py
from fpdf import FPDF

def export_to_pdf(data, filename="sentiment_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Sentiment Report", ln=True, align="C")
    pdf.ln(10)

    for index, row in data.iterrows():
        pdf.cell(200, 10, txt=f"{index+1}. {row['text'][:50]}... -> {row['sentiment']} ({row['confidence']}%)", ln=True)

    pdf.output(filename)
    return filename
