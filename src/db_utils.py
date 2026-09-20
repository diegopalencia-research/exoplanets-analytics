"""Shared database helpers for the Exoplanet Analytics dashboard."""
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data/exoplanets.db"


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """Return a cached SQLite connection (read-only mode)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=300)
def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame."""
    con = get_connection()
    return pd.read_sql(sql, con, params=params)
