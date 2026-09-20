# 🪐 Exoplanet Analytics

> A multidisciplinary portfolio project at the intersection of **space science**, **data analytics**, **SQL engineering**, and **business intelligence** — delivered as an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SQL](https://img.shields.io/badge/SQL-SQLite-orange)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Why this project?

Built as a T-shaped portfolio piece: **deep domain knowledge in exoplanet science** +
**strong quantitative/data capability** + **BI/delivery literacy**. Every dashboard number
is computed by an explicit, inspectable SQL query against a real database — the same
discipline you'd apply in a professional analytics role.

## What it demonstrates

| Skill | Where you'll see it |
|---|---|
| **SQL** (staging → cleaning → star schema → views) | `data/schema.sql`, SQL Lab page |
| **Python / pandas / ETL** | `data/etl.py`, `src/db_utils.py` |
| **Visualization & storytelling** | Plotly charts across 4 dashboard pages |
| **BI & dimensional modeling** | KPI views, semantic layer (`v_*` views) |
| **Statistics** | Distributions, mass–radius relation, ESI |
| **Deployment** | Streamlit Community Cloud, ready-to-fork |

## Live dashboard pages

1. **Home** — KPIs, discovery trend, detection-method breakdown
2. **📊 Overview** — discovery acceleration, size categories, the **radius valley**
3. **🔭 Exploration** — interactive mass–radius diagram, parameterized SQL filtering
4. **🌍 Habitability** — habitable-zone candidates, Earth Similarity Index leaderboard
5. **🧪 SQL Lab** — write & run your own SQL against the database, live

## Architecture

```
exoplanet-analytics/
├── app.py                  # Streamlit entry point (home + KPIs)
├── pages/                  # Multipage dashboard
│   ├── 1_📊_Overview.py
│   ├── 2_🔭_Exploration.py
│   ├── 3_🌍_Habitability.py
│   └── 4_🧪_SQL_Lab.py
├── src/
│   └── db_utils.py         # Cached connection + query helpers
├── data/
│   ├── etl.py              # ETL pipeline: CSV → SQLite → views
│   ├── schema.sql          # Cleaning, dimension table, analytical views
│   ├── exoplanets_raw.csv  # Source data (2,400-planet sample catalog)
│   └── exoplanets.db       # Built database (rebuild anytime with etl.py)
├── .streamlit/config.toml  # Dashboard theme
└── requirements.txt
```

**Data flow:**

```
exoplanets_raw.csv
      │  extract (pandas)
      ▼
staging_planets            ← raw landing zone, never modified
      │  transform (pure SQL, schema.sql)
      ▼
dim_planet (dimension)     ← cleaned + derived columns (size_category, ESI)
      │  semantic layer
      ▼
v_* views                  ← KPIs, trends, method share, habitability
      │
      ▼
Streamlit dashboard        ← every chart queries a view directly
```

## Quick start

```bash
git clone https://github.com/<your-username>/exoplanet-analytics.git
cd exoplanet-analytics
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Rebuild the database from raw data at any time:

```bash
python data/etl.py
```

## Deploy to Streamlit Community Cloud (free)

1. Push this repo to GitHub (include `data/exoplanets.db` — Streamlit Cloud runs
   `streamlit run app.py` directly from the repo).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → pick the
   repo, branch `main`, main file `app.py`.
3. Deploy. Done — you get a public URL like `https://<app>.streamlit.app`.

> The SQLite database is a small file (~500 KB), so committing it is fine and makes
> deployment zero-config. The ETL script remains available for reproducibility.

## Using REAL NASA data (upgrade path)

The project ships with a statistically realistic **sample catalog** so it runs offline.
To graduate it to real research data:

1. Download the composite planet table from the
   [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PSCompPars)
   as CSV.
2. Rename the relevant columns to the schema in `data/schema.sql` (or adapt the SQL).
3. Run `python data/etl.py` and redeploy.

Suggested v2 extensions:
- Replace the sample generator with an Astroquery pull of confirmed planets
- Add a Lightkurve light-curve analysis page (TESS targets)
- Add pytest tests for the SQL views
- Add a downloadable "report" button (BI deliverable)

## Method notes

- **Habitability flag:** rocky (radius < 1.8 R⊕ or mass < 10 M⊕) AND semi-major axis
  within the optimistic HZ computed from stellar temperature/radius.
- **Earth Similarity Index (simplified):** 1 − √[ ½(1−R⊕/R⊕)² + ½(1−M⊕/M⊕)² ],
  clamped to avoid giant-planet domination; computed in SQL.
- **Radius valley:** empirically observed dip at ~1.5–2.0 R⊕, visible in the Overview page.

## License

MIT — see [LICENSE](LICENSE).
