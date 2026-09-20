"""Exploration page — interactive catalog filtering & mass-radius diagram."""
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_utils import run_query

st.set_page_config(page_title="Exploration", page_icon="🔭", layout="wide")
st.title("🔭 Catalog Exploration")

# ---------------- Filters (sidebar) ----------------
st.sidebar.header("Filters")
methods = run_query("SELECT DISTINCT discovery_method FROM dim_planet")["discovery_method"].tolist()
sel_methods = st.sidebar.multiselect("Discovery method", methods, default=methods)
yr_min, yr_max = st.sidebar.slider("Discovery year", 1992, 2025, (1992, 2025))
r_max = st.sidebar.slider("Max radius (R⊕)", 0.5, 15.0, 15.0)
hab_only = st.sidebar.checkbox("Habitable-zone candidates only", value=False)

# ---------------- Parameterized SQL (no SQL injection — analytics skill) ----------------
sql = """
SELECT * FROM dim_planet
WHERE discovery_method IN ({placeholders})
  AND discovery_year BETWEEN ? AND ?
  AND radius_earth <= ?
  {hab_clause}
ORDER BY discovery_year DESC
""".format(placeholders=",".join("?" * len(sel_methods)),
           hab_clause="AND potentially_habitable = 1" if hab_only else "")
params = tuple(sel_methods) + (yr_min, yr_max, r_max)
df = run_query(sql, params)

st.caption(f"Query returned **{len(df):,}** planets (parameterized SQL against `dim_planet`).")

# ---------------- Mass–Radius diagram ----------------
st.subheader("Mass–Radius Diagram")
st.markdown("Each dot is a world. The diagonal band is the empirical mass–radius "
            "relation; outliers hint at unusual compositions (iron cores, water worlds).")
fig = px.scatter(df, x="radius_earth", y="mass_earth", color="size_category",
                 hover_data=["pl_name", "discovery_year", "semi_major_axis_au",
                             "stellar_temp_k", "distance_pc"],
                 log_x=True, log_y=True,
                 labels={"radius_earth": "Radius (R⊕, log)", "mass_earth": "Mass (M⊕, log)",
                         "size_category": "Category"},
                 color_discrete_map={"Terrestrial": "#2ec4b6", "Super-Earth": "#ffbf69",
                                     "Sub-Neptune/Neptune": "#5f6caf", "Gas Giant": "#9d4edd"})
fig.update_layout(height=520)
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig2 = px.scatter(df, x="semi_major_axis_au", y="orbital_period_days",
                      color="discovery_method", log_x=True, log_y=True,
                      labels={"semi_major_axis_au": "Semi-major axis (AU, log)",
                              "orbital_period_days": "Period (days, log)"},
                      title="Kepler's third law in the data")
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)
with right:
    fig3 = px.scatter(df, x="stellar_temp_k", y="radius_earth",
                      color="potentially_habitable",
                      labels={"stellar_temp_k": "Stellar temperature (K)",
                              "radius_earth": "Planet radius (R⊕)",
                              "potentially_habitable": "Habitable"},
                      title="Planet size vs. host star temperature",
                      color_continuous_scale="Teal")
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Filtered catalog")
st.dataframe(df, use_container_width=True, hide_index=True)
