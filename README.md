# 🚀 Setup Instructions (Cross-Platform)

## ✅ 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sentiment_dashboard.git
cd sentiment_dashboard
```

---

## ✅ 2. Set Up a Virtual Environment

### On Windows (Command Prompt or PowerShell)

```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## ✅ 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

This will open the app in your browser at:  
[http://localhost:8501](http://localhost:8501)

---

# 📦 Project Features (In Progress)

- ✅ Text input and file upload  
- ✅ Sentiment classification using NLP API (Hugging Face)  
- ✅ Confidence score display  
- ✅ Batch text analysis  
- ✅ Visualizations (bar chart, pie chart)  
- ✅ Export as CSV, JSON, PDF  

---

# 🧪 Dependencies Overview

| Library       | Purpose                          |
|---------------|----------------------------------|
| `streamlit`   | App UI framework                 |
| `pandas`      | Data processing                  |
| `matplotlib`  | Charting                         |
| `plotly`      | Interactive visualizations       |
| `requests`    | HTTP/API requests                |
| `transformers`| Hugging Face integration         |
| `fpdf`        | PDF export capability            |

---

# 🛠 Contribution Tips

- Use branches or pull requests when adding new features  
- Test your changes before pushing  
- Update `requirements.txt` when adding new packages:

```bash
pip freeze > requirements.txt
```
