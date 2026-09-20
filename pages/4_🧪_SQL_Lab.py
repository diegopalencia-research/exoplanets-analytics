"""SQL Lab — write and run your own SQL against the star-schema database."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_utils import run_query

st.set_page_config(page_title="SQL Lab", page_icon="🧪", layout="wide")
st.title("🧪 SQL Lab")
st.markdown("Query the database directly. This is the heart of the project — "
            "every dashboard number you saw is one of these queries.")

schema = run_query("""
SELECT type, name FROM sqlite_master
WHERE name IN ('dim_planet','staging_planets')
   OR name LIKE 'v_%'
ORDER BY type DESC, name
""")
st.sidebar.header("Database schema")
st.sidebar.dataframe(schema, hide_index=True, use_container_width=True)

examples = {
    "Top 10 largest planets": """
SELECT pl_name, radius_earth, mass_earth, discovery_method
FROM dim_planet ORDER BY radius_earth DESC LIMIT 10;""",
    "Discoveries per decade": """
SELECT (discovery_year/10)*10 AS decade, COUNT(*) AS planets,
       SUM(potentially_habitable) AS habitable
FROM dim_planet GROUP BY decade ORDER BY decade;""",
    "Average radius by detection method": """
SELECT discovery_method, ROUND(AVG(radius_earth),2) AS avg_radius, COUNT(*) AS n
FROM dim_planet GROUP BY discovery_method ORDER BY n DESC;""",
    "Closest 15 HZ candidates": """
SELECT pl_name, distance_pc, radius_earth, esi_radius_mass
FROM dim_planet
WHERE potentially_habitable = 1
ORDER BY distance_pc ASC LIMIT 15;""",
}
choice = st.selectbox("Load an example query", ["(write your own)"] + list(examples))
default = examples.get(choice, "SELECT * FROM v_kpi_summary;")
sql = st.text_area("SQL", value=default.strip(), height=180)

if st.button("▶ Run query", type="primary"):
    try:
        result = run_query(sql)
        st.success(f"{len(result)} rows returned")
        st.dataframe(result, use_container_width=True, hide_index=True)
        if len(result) > 1 and result.select_dtypes("number").shape[1] >= 2:
            import plotly.express as px
            num = result.select_dtypes("number").columns[:2]
            st.plotly_chart(px.bar(result, x=result.columns[0], y=num[1]),
                            use_container_width=True)
    except Exception as e:
        st.error(f"SQL error: {e}")

with st.expander("📚 SQL reference — tables & views"):
    st.markdown("""
**`staging_planets`** — raw landing table (source of truth, unmodified)

**`dim_planet`** — cleaned dimensional table (star schema dimension), with derived
`size_category` and `esi_radius_mass` computed in SQL

**Analytical views (the BI semantic layer):**
| View | Purpose |
|---|---|
| `v_kpi_summary` | Portfolio-level KPIs |
| `v_discoveries_by_year` | Time trend + habitability mix |
| `v_method_breakdown` | Detection-method market share |
| `v_habitability` | Habitability rate by size category |
| `v_top_habitable` | Ranked Earth analogs (ESI) |
    """)
