-- Star-schema build: staging -> dim_planet -> analytical views
DROP TABLE IF EXISTS dim_planet;
CREATE TABLE dim_planet AS
SELECT
    pl_name, hostname,
    CAST(discovery_year AS INTEGER) AS discovery_year,
    discovery_method, consortium,
    CAST(orbital_period_days AS REAL) AS orbital_period_days,
    CAST(radius_earth AS REAL) AS radius_earth,
    CAST(mass_earth AS REAL) AS mass_earth,
    CAST(semi_major_axis_au AS REAL) AS semi_major_axis_au,
    CAST(stellar_temp_k AS REAL) AS stellar_temp_k,
    CAST(stellar_radius_solar AS REAL) AS stellar_radius_solar,
    CAST(stellar_mass_solar AS REAL) AS stellar_mass_solar,
    CAST(distance_pc AS REAL) AS distance_pc,
    CAST(hz_inner_au AS REAL) AS hz_inner_au,
    CAST(hz_outer_au AS REAL) AS hz_outer_au,
    potentially_habitable,
    CASE
        WHEN radius_earth < 1.25 THEN 'Terrestrial'
        WHEN radius_earth < 2.0  THEN 'Super-Earth'
        WHEN radius_earth < 6.0  THEN 'Sub-Neptune/Neptune'
        ELSE 'Gas Giant'
    END AS size_category,
    ROUND(1 - SQRT( 0.5*((1 - MIN(radius_earth,15)/1.0)*(1 - MIN(radius_earth,15)/1.0))
                        + 0.5*((1 - MIN(mass_earth,10000)/1.0)*(1 - MIN(mass_earth,10000)/1.0)) ), 3) AS esi_radius_mass
FROM staging_planets
WHERE pl_name IS NOT NULL
  AND discovery_year BETWEEN 1992 AND 2025
  AND radius_earth > 0 AND orbital_period_days > 0;

CREATE INDEX IF NOT EXISTS idx_year   ON dim_planet(discovery_year);
CREATE INDEX IF NOT EXISTS idx_method ON dim_planet(discovery_method);
CREATE INDEX IF NOT EXISTS idx_hab    ON dim_planet(potentially_habitable);

DROP VIEW IF EXISTS v_discoveries_by_year;
CREATE VIEW v_discoveries_by_year AS
SELECT discovery_year, COUNT(*) AS n_planets,
       SUM(potentially_habitable) AS n_habitable,
       ROUND(AVG(radius_earth),3) AS avg_radius,
       ROUND(AVG(distance_pc),1)  AS avg_distance_pc
FROM dim_planet GROUP BY discovery_year ORDER BY discovery_year;

DROP VIEW IF EXISTS v_method_breakdown;
CREATE VIEW v_method_breakdown AS
SELECT discovery_method, COUNT(*) AS n_planets,
       ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(),1) AS pct_share,
       ROUND(AVG(radius_earth),3) AS avg_radius,
       ROUND(AVG(orbital_period_days),1) AS avg_period_days
FROM dim_planet GROUP BY discovery_method ORDER BY n_planets DESC;

DROP VIEW IF EXISTS v_habitability;
CREATE VIEW v_habitability AS
SELECT size_category, COUNT(*) AS n_planets,
       SUM(potentially_habitable) AS n_habitable,
       ROUND(100.0*SUM(potentially_habitable)/COUNT(*),1) AS pct_habitable
FROM dim_planet GROUP BY size_category;

DROP VIEW IF EXISTS v_top_habitable;
CREATE VIEW v_top_habitable AS
SELECT pl_name, hostname, discovery_year, discovery_method,
       radius_earth, mass_earth, semi_major_axis_au,
       stellar_temp_k, distance_pc, esi_radius_mass, size_category
FROM dim_planet
WHERE potentially_habitable = 1
ORDER BY esi_radius_mass DESC LIMIT 50;

DROP VIEW IF EXISTS v_kpi_summary;
CREATE VIEW v_kpi_summary AS
SELECT COUNT(*) AS total_planets, COUNT(DISTINCT hostname) AS host_stars,
       SUM(potentially_habitable) AS habitable_count,
       ROUND(AVG(radius_earth),2) AS mean_radius,
       ROUND(AVG(distance_pc),1) AS mean_distance,
       ROUND(MIN(distance_pc),1) AS nearest_pc,
       MAX(discovery_year) AS latest_year
FROM dim_planet;
