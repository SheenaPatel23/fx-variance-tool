# FX Variance Tool

A free Streamlit app to compare budget FX rates with ECB daily/monthly FX rates, and visualise variances in FX and operating costs.

## 🚀 Features
- Uses free ECB FX rates via [Frankfurter API](https://www.frankfurter.app/) (no API key).
- Upload budget FX rates & operating costs in CSV format.
- Computes:
  - FX Rate Variance
  - Operating Cost Variance
  - Total Variance
- Interactive visuals (rate trends, cost centre variance bars, waterfall, time-series).
- Export variance table to CSV.

## 📊 Sample Data
Two sample files are included in `sample_data/`:
- `budget_rates.csv`
- `operating_costs.csv`

## 🛠️ Run Locally
```bash
git clone https://github.com/<your-username>/fx-variance-tool.git
cd fx-variance-tool
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud
1. Push this repo to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/), click **New app**.
3. Select repo + branch, set main file to `app.py`, and click Deploy.

## 📜 License
MIT
