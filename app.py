"""
Exoplanet Analytics — Portfolio Dashboard
=========================================
A multidisciplinary project combining:
  * Space science (exoplanet astronomy & habitability)
  * Data analytics (Python, pandas, SQL, ETL)
  * Business intelligence (KPIs, dimensional modeling, dashboards)

Data pipeline: data/etl.py  ->  staging -> SQL cleaning -> analytical views
Run locally:  streamlit run app.py
"""
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.db_utils import run_query

st.set_page_config(page_title="Exoplanet Analytics",
                   page_icon="🪐", layout="wide")

st.title("🪐 Exoplanet Analytics")
st.markdown(
    "**Where space science meets data analytics.** Explore a catalog of "
    "confirmed exoplanets: discovery trends, detection methods, the "
    "mass–radius diagram, and the hunt for potentially habitable worlds."
)
st.divider()

# ---------------- KPI row (from SQL view — the BI layer) ----------------
kpi = run_query("SELECT * FROM v_kpi_summary").iloc[0]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Confirmed Planets", f"{int(kpi['total_planets']):,}")
c2.metric("Host Stars", f"{int(kpi['host_stars']):,}")
c3.metric("Habitable-zone Candidates", f"{int(kpi['habitable_count']):,}")
c4.metric("Mean Radius", f"{kpi['mean_radius']} R⊕")
c5.metric("Nearest Planet", f"{kpi['nearest_pc']} pc")
st.caption("KPIs computed live from the `v_kpi_summary` SQL view in `data/exoplanets.db`.")

tab1, tab2 = st.tabs(["📈 Discovery Trend", "🔬 Methods"])

with tab1:
    yearly = run_query("SELECT * FROM v_discoveries_by_year")
    fig = px.bar(yearly, x="discovery_year", y="n_planets",
                 color="n_habitable", labels={
                     "discovery_year": "Year", "n_planets": "Planets discovered",
                     "n_habitable": "Habitable-zone"},
                 color_continuous_scale="Teal", title="Exoplanet discoveries per year")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.info("Exponential growth driven by space-based surveys (CoRoT → Kepler/K2 → TESS).")

with tab2:
    meth = run_query("SELECT * FROM v_method_breakdown")
    left, right = st.columns([3, 2])
    with left:
        figm = px.bar(meth, x="n_planets", y="discovery_method", orientation="h",
                      labels={"n_planets": "Planets", "discovery_method": "Method"},
                      color="pct_share", color_continuous_scale="Viridis",
                      title="Detections by discovery method")
        figm.update_layout(height=420, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(figm, use_container_width=True)
    with right:
        st.dataframe(meth, use_container_width=True, hide_index=True)
        st.markdown("**Takeaway:** Transit photometry dominates because it is "
                    "survey-scalable; RV excels at measuring masses.")

st.divider()
st.subheader("🗺️ Project navigation")
st.markdown("""
| Page | What you'll find |
|---|---|
| 📊 **Overview** | The science story: trends, methods, the radius valley |
| 🔭 **Exploration** | Interactive mass–radius diagram & catalog filtering |
| 🌍 **Habitability** | Habitable-zone candidates, Earth Similarity Index |
| 🧪 **SQL Lab** | Write your own SQL against the star-schema database |
""")

st.caption("Built with Python · SQLite (SQL) · Plotly · Streamlit — a portfolio "
           "project demonstrating the full data-analyst / BI pipeline.")
