# Provisional 2025 CDC U.S. Natality Dashboard

An interactive exploratory business analytics dashboard built with **Streamlit**, **pandas**, and **Plotly** to examine geographic, monthly, and sex-based variations in provisional 2025 United States live births.

Designed for undergraduate business analytics students studying data quality auditing, exploratory data analysis (EDA), and interactive visualization design.

---

## 📌 Key Objectives & Pedagogical Focus

1. **Understanding Event Counts vs. Rates (The Denominator Fallacy):**
   - Figures in this dataset represent **discrete raw counts of registered live births**, *not* birth rates or fertility rates.
   - Variations across states (e.g., California vs. Vermont) are primarily driven by base population size rather than differing fertility behaviors.
2. **Provisional Public Health Data Literacy:**
   - The data originate from the [CDC WONDER Online Database](https://wonder.cdc.gov/natality.html) and represent provisional 2025 counts subject to official revision.
3. **Data Quality Auditing:**
   - The dataset has been rigorously validated:
     - Exactly **1,224 observations** ($51 \text{ geographies} \times 12 \text{ months} \times 2 \text{ sexes}$)
     - **0 missing values**
     - **0 duplicate records**
     - **3,604,640 total live births**

---

## 🚀 Running the Dashboard Locally

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Required Packages
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📂 Project Architecture

```text
cdc-births-2025-2/
├── .streamlit/
│   └── config.toml                  # Streamlit theme & layout configuration
├── data/
│   └── Provisional_Natality_2025_CDC.xlsx  # Untouched, read-only CDC natality dataset
├── utils/
│   ├── __init__.py
│   ├── data_loader.py               # Data loading, automated validation assertions, caching
│   └── charts.py                    # Plotly chart builders with accessible styling & zero baselines
├── app.py                           # Main application orchestrator & user interface
├── requirements.txt                 # Pinned dependencies
└── README.md                        # Documentation & student guide
```

---

## 📊 Features & Navigation

- **Header & Warnings:** Visible provisional notice, CDC source attribution, and pedagogical warnings distinguishing counts from rates.
- **Dynamic Sidebar Filters:** Multi-select filtering for Geographies, Months, and Infant Sex, complete with instant **"Select All"** and **"Reset Filters"** action controls and an active filter summary badge.
- **Top KPI Cards:** Instant metrics updating in real time: Total Births, Selected Geographies, Average Births per Month, Highest-Volume Geography, and Peak Month.
- **Structured Tabs:**
  - **Overview:** Monthly birth trends and female vs. male distribution.
  - **Geographic Analysis:** Interactive US state choropleth map, ranked horizontal bar charts, and top 5 vs. bottom 5 comparisons.
  - **Monthly & Sex Analysis:** 2D State-by-Month heatmap and monthly biological sex ratio tracking (~51.2% male to 48.8% female).
  - **Data Table & Download:** Searchable and sortable filtered table with one-click CSV export.
  - **About the Data:** Full data dictionary, methodology notes, and automated data audit status.

---

## 🛡️ Analytical Safeguards & Design Decisions

- **Zero Baselines:** All numerical bar and ranking charts start at $0$ to prevent deceptive visual exaggerations.
- **Accessible Colors:** High-contrast, colorblind-friendly palettes (Slate Blue for Male, Terracotta for Female).
- **Graceful Empty States:** Helpful instructional warnings when filters yield zero records instead of cryptic code exceptions.
- **Resilient Caching:** Fast startup and responsive filtering powered by `@st.cache_data`.
