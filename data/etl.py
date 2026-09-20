"""ETL pipeline: raw CSV -> SQLite staging -> SQL cleaning -> analytical views.

Run once (or whenever data refreshes):
    python data/etl.py
Then launch the dashboard:
    streamlit run app.py

Note: This project ships with a generated sample catalog (2,400 planets) so it
runs offline and deploys anywhere. To use REAL data, download the NASA
Exoplanet Archive composite table (CSV) and point RAW_CSV at it:
    https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PSCompPars
"""
import sqlite3
import pandas as pd
from pathlib import Path

RAW_CSV = Path(__file__).parent / "exoplanets_raw.csv"
DB_PATH = Path(__file__).parent / "exoplanets.db"

SCHEMA_SQL = Path(__file__).parent / "schema.sql"


def extract() -> pd.DataFrame:
    print(f"[EXTRACT] Reading {RAW_CSV}")
    return pd.read_csv(RAW_CSV)


def load_staging(con: sqlite3.Connection, df: pd.DataFrame) -> None:
    print("[LOAD] Writing staging_planets")
    df.to_sql("staging_planets", con, if_exists="replace", index=False)


def transform(con: sqlite3.Connection) -> None:
    print("[TRANSFORM] Applying schema.sql (cleaning + views)")
    con.executescript(SCHEMA_SQL.read_text())
    con.commit()


def main() -> None:
    df = extract()
    with sqlite3.connect(DB_PATH) as con:
        load_staging(con, df)
        transform(con)
    n = pd.read_sql("SELECT COUNT(*) AS n FROM dim_planet",
                    sqlite3.connect(DB_PATH)).iloc[0]["n"]
    print(f"[DONE] dim_planet rows: {n} | Database: {DB_PATH}")


if __name__ == "__main__":
    main()
