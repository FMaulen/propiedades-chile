# 🏠 Chilean Property Prices — RM Analysis

![Python](https://img.shields.io/badge/Python-3.9-3776AB.svg?style=flat&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458.svg?style=flat&logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow.svg?style=flat)


Exploratory data analysis and data cleaning of the real estate market in Chile's Metropolitan Region (RM), using property listings obtained via web scraping (2023). The project's end goal is to build a predictive model for property prices in UF.

---

## 📁 Project Structure

```
├── data/
│   ├── raw/
│   │   ├── 2023-03-08 Precios Casas RM.csv
│   │   └── 2023-07-18 Propiedades Web Scrape.csv
│   └── processed/
│       └── casas_chile_limpio.csv
├── notebooks/
│   └── EDA_Analysis.ipynb
├── src/
│   └── preprocessing.py
└── README.md
```

---

## 📊 Dataset

| Feature | Detail |
|---|---|
| Source | Kaggle Web scraping of RM real estate portals |
| Period | March – July 2023 |
| Records | ~9,291 properties |
| Variables | Price UF, Built Area, Total Area, Dorms, Baths, Parking, Comuna, Realtor |

---

## 🔬 Current Scope

### 1. Optimized Data Loading
- Chunk-based reading with `chunksize=1000` to optimize memory usage
- Explicit `dtype` definitions (`float32`, `Int8`) reducing RAM footprint by ~60%
- Before/after memory comparison logged at runtime

### 2. Audit & Validation
- Dataset checksum via `pd.util.hash_pandas_object` to detect source file changes
- Null and duplicate counts
- Column-by-column schema validation against expected types

### 3. Exploratory Data Analysis
- Numeric variable distributions with histograms and KDE
- Null analysis by column with percentage breakdown
- Correlation matrix with heatmap

### 4. Data Cleaning
- Duplicate removal
- Outlier detection and filtering using the IQR method
- Justified decision not to impute `Parking` (31% nulls) or `Realtor` (12% nulls) — see design decisions below

### 5. Analysis & Visualizations
- Average price per comuna (barh)
- Average UF/m² per comuna
- Average parking spots per comuna
- Price pivot table: comuna × number of bedrooms
- Below-threshold property detection with configurable factor (per-comuna mean × factor)

### 6. Sklearn Preprocessing Pipeline
- `ColumnTransformer` with `StandardScaler` for numeric features and `OneHotEncoder` for `Comuna`
- Chained `Pipeline` ready to plug in a predictive model

---

## ⚙️ Installation

```bash
git clone https://github.com/FMaulen/propiedades-chile.git
cd propiedades-chile
pip install -r requirements.txt
```

**Main dependencies:**
```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
seaborn>=0.12
matplotlib>=3.7
scipy>=1.10
```

---

## 🗺️ Roadmap

### ✅ Phase 1 — EDA & Cleaning (current)
- [x] Optimized loading with chunking and dtypes
- [x] Audit and schema validation
- [x] Full exploratory data analysis
- [x] Outlier removal with IQR

### 🔄 Phase 2 — Predictive Modeling (upcoming)
- [ ] Feature selection via correlation analysis and feature importance
- [ ] Baseline model training (`LinearRegression`)
- [ ] Model comparison (`RandomForest`)

---

## 📌 Key Design Decisions

**Why not impute Parking and Realtor?**
Imputing `Parking` with the mean would introduce bias in comunas where parking significantly impacts price. `Realtor` is a categorical variable with no valid statistical basis for estimation. Both are excluded from the modeling pipeline.

**Why chunking?**
The main dataset exceeds 9,000 rows with multiple float columns. Reading in chunks with optimized dtypes reduces memory usage by ~60% compared to a standard load with default types.

**Why a per-comuna threshold for cheap properties?**
A global mean threshold would misclassify properties in expensive comunas as normal when they are actually cheap relative to their area. Computing the threshold per comuna (mean × factor) makes the comparison locally meaningful.

---

## 👤 Author

Developed as an academic data analysis project — Instituto Profesional Duoc UC, 2026.
