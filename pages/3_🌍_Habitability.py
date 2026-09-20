"""Habitability page — HZ candidates & Earth Similarity Index."""
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_utils import run_query

st.set_page_config(page_title="Habitability", page_icon="🌍", layout="wide")
st.title("🌍 The Habitable Zone")

st.markdown("A planet is flagged as a **candidate** when it is rocky "
            "(radius < 1.8 R⊕ or mass < 10 M⊕) and orbits within the optimistic "
            "habitable zone of its star — where liquid water could exist.")

c1, c2, c3 = st.columns(3)
hab = run_query("SELECT * FROM v_habitability")
c1.metric("HZ candidates", int(hab["n_habitable"].sum()))
c2.metric("Most promising category",
          hab.sort_values("pct_habitable", ascending=False).iloc[0]["size_category"])
c3.metric("Avg ESI of top candidates",
          run_query("SELECT ROUND(AVG(esi_radius_mass),2) AS m FROM v_top_habitable").iloc[0]["m"])
st.divider()

left, right = st.columns([3, 2])

with left:
    df = run_query("""
        SELECT semi_major_axis_au, radius_earth, stellar_temp_k,
               pl_name, hz_inner_au, hz_outer_au, potentially_habitable
        FROM dim_planet WHERE radius_earth < 8
    """)
    fig = px.scatter(df, x="semi_major_axis_au", y="radius_earth",
                     color="potentially_habitable", log_x=True,
                     hover_data=["pl_name", "stellar_temp_k"],
                     labels={"semi_major_axis_au": "Distance from star (AU, log)",
                             "radius_earth": "Planet radius (R⊕)",
                             "potentially_habitable": "HZ candidate"},
                     color_continuous_scale="Teal", title="Where the candidates live")
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)

with right:
    figh = px.bar(hab, x="size_category", y="pct_habitable",
                  color="n_habitable", labels={
                      "size_category": "Category", "pct_habitable": "% habitable-zone",
                      "n_habitable": "HZ candidates"},
                  color_continuous_scale="Teal", title="Habitability rate by size")
    figh.update_layout(height=480)
    st.plotly_chart(figh, use_container_width=True)

st.subheader("🏆 Top candidates — Earth Similarity Index (ESI)")
st.markdown("ESI compares radius and mass to Earth's. Values near 1.0 are the "
            "closest analogs we know.")
top = run_query("SELECT * FROM v_top_habitable")
st.dataframe(top, use_container_width=True, hide_index=True)
st.caption("Source view: `v_top_habitable` — SQL-side filtering, ranking, and limiting.")
