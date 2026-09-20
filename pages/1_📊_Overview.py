"""Overview page — discovery trends & the radius valley."""
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_utils import run_query

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")
st.title("📊 The Big Picture")

st.markdown("The exoplanet census transformed astronomy after 1995. Two datasets "
            "below tell the story: **how fast** we find planets, and **what kinds** "
            "of planets exist.")

left, right = st.columns(2)

with left:
    yearly = run_query("SELECT * FROM v_discoveries_by_year")
    fig = px.area(yearly, x="discovery_year", y="n_planets",
                  labels={"discovery_year": "Year", "n_planets": "Discoveries"},
                  title="Cumulative discovery acceleration",
                  color_discrete_sequence=["#2ec4b6"])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with right:
    hab = run_query("SELECT * FROM v_habitability")
    figh = px.pie(hab, values="n_planets", names="size_category", hole=0.45,
                  title="Planet size categories",
                  color_discrete_sequence=px.colors.sequential.Teal_r)
    figh.update_layout(height=400)
    st.plotly_chart(figh, use_container_width=True)

st.subheader("The Radius Valley")
st.markdown("Between ~1.5–2.0 Earth radii, the occurrence rate drops sharply — "
            "the **radius valley**. It's a fossil record of atmospheric loss: "
            "planets either keep a rocky surface or accrete a thick gas envelope.")
r = run_query("SELECT radius_earth FROM dim_planet")
figr = px.histogram(r, x="radius_earth", nbins=60,
                    labels={"radius_earth": "Radius (Earth radii)", "count": "Planets"},
                    color_discrete_sequence=["#ff9f1c"], title="Radius distribution")
figr.add_vrect(x0=1.5, x1=2.0, fillcolor="red", opacity=0.12,
               annotation_text="radius valley", annotation_position="top")
figr.update_layout(height=420)
st.plotly_chart(figr, use_container_width=True)
