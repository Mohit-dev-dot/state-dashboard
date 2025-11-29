# state-dashboard
🚀 State Development Impact Analyzer

A fully interactive Streamlit-based analytics dashboard that evaluates the development performance of Indian states across economic, social, and infrastructure indicators.
The tool transforms raw state-level data into actionable insights, comparisons, and forecasting visualizations using modern data science techniques.

📌 Features
✅ 1. Executive State Summary

Auto-generated long-form summary for any chosen state

Covers economy, education, health, poverty, infrastructure, and SDGs

Uses correlation and trend analysis to highlight state strengths

✅ 2. Comparative Trend Analysis

Visualize multi-state trends across any indicator

Interactive Altair charts with hover analytics

Supports multi-year & multi-state comparison

✅ 3. Impact Analysis (Input → Outcome)

Select any input (e.g., education spending)

Select any outcome (e.g., literacy, PCI, sanitation)

Generates narrative impact analysis with real-world interpretation

Includes scatter plots + regression trend lines

✅ 4. Forecasting & Benchmarking

Linear projection of future performance

Identify top 5 states in any selected indicator

Distribution charts of indicator spread

✅ 5. State Comparison Insights

Generates top 5 crisp insights per state

Uses statistical signals + curated state profile metadata

🛠️ Tech Stack

Python 3.10+

Streamlit

Pandas, NumPy

Altair

SciPy

OpenPyXL

Custom analysis modules (impact, summary, comparison)

📁 Project Structure
state-dashboard/
│
├── app.py                     # Streamlit main app
├── long_summary.py            # Generates detailed state summary
├── impact_summary.py          # Impact analysis logic
├── comparison_points.py       # Insight generator
├── state_profiles.py          # Real-world state metadata
├── utils.py                   # Numerical helpers
│
├── data/
│   └── Project.xlsx           # Core dataset
│
├── requirements.txt
└── README.md

📊 Dataset

The dashboard uses an Excel dataset containing yearly state-level numbers for:

Per Capita Income

GSDP

Poverty Rate

Literacy Rate

Education / Health / Agriculture / Industry / Services expenditure

Urbanization

Electrification

Sanitation

Piped Water

HDI

SDG Index

IMR

Life Expectancy

Skill Coverage

Unemployment

Housing Units

Add or update your dataset inside:

data/Project.xlsx

▶️ Run Locally
1. Clone the repo
git clone https://github.com/Mohit-dev-dot/state-dashboard
cd state-dashboard

2. Install dependencies
pip install -r requirements.txt

3. Run the app
streamlit run app.py

🌐 Deployment (Streamlit Cloud)

Push the repository to GitHub

Go to share.streamlit.io

Connect your repo

Set app.py as the entry file

Make sure data/Project.xlsx exists in the /data folder
