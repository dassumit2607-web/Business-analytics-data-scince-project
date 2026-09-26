# 📊 Business Sales & Profit Dashboard

An interactive analytics dashboard that turns any raw sales file into business insights — and now, ML-powered sales forecasts. Built with Python and Streamlit.

Upload a CSV or Excel sales file, and the app automatically detects your columns, cleans the data, and gives you a full interactive dashboard — no manual setup required for each new dataset.

---

## ✨ Features

- **Automatic column detection** — recognizes common business column names (e.g. "Sales", "Revenue", "Total Amount" all map to the same field) so it works on datasets it's never seen before
- **📊 Dashboard** — key metrics, monthly sales trends, category and region breakdowns
- **❓ Business Questions** — answers common business questions directly from your data
- **💡 Business Insights** — auto-generated, plain-English insights (e.g. discount vs. profit relationships)
- **🔮 Sales Forecast** — predicts future monthly sales using a regression model with seasonality, validated honestly on held-out months (reports MAE and R² before forecasting)
- **Multi-currency support**
- Interactive filters: date range, region, category

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** — web app framework
- **Pandas / NumPy** — data cleaning and manipulation
- **Matplotlib** — charts
- **scikit-learn** — sales forecasting model (Linear Regression)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Install dependencies

```bash
pip install streamlit pandas numpy matplotlib scikit-learn
```

Or, if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

### 4. Use it

Upload any sales CSV/Excel file with columns like Date, Product, Category, Sales, Profit, Region, etc. (naming doesn't have to match exactly — the app detects common variations automatically).

---

## 📁 Project Structure

```
├── app.py              # Main Streamlit application
├── cleaning.py         # Data cleaning and column standardization
├── requirements.txt    # Python dependencies
└── README.md
```

---

## ⚠️ Limitations

- The forecasting model is a simple trend + seasonality regression (Linear Regression), not a full time-series model like ARIMA or Prophet
- Forecasts are based purely on historical sales patterns — they don't account for promotions, holidays, or external market factors
- Built and tested primarily on Superstore-style retail sales data; highly irregular schemas may need manual column mapping
- Runs in-memory per session — not designed for very large (multi-GB) datasets
- No authentication or multi-user support — intended as a personal analytics tool

---

## 🔮 Future Improvements

- Compare forecasting accuracy against Random Forest / other models
- Add proper time-series methods (ARIMA, Prophet)
- Support for multiple file uploads / merging datasets
- Export dashboard results as PDF/Excel reports

---

## 👤 Author

**Sumit Das**
B.Tech Computer Science Engineering (Data Science), JIS University, Kolkata
[GitHub](https://github.com/dassumit2607-web) · [LinkedIn](https://linkedin.com/in/sumitdas-6b1466323)
