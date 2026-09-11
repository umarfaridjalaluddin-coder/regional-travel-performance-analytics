CREATE OR REPLACE TABLE gold.dim_date AS
WITH date_spine AS (
    SELECT *
    FROM GENERATE_SERIES(
        DATE '2024-09-01',
        DATE '2026-12-31',
        INTERVAL 1 DAY
    )
)
SELECT
    CAST(generate_series AS DATE) AS date_key,

    EXTRACT(YEAR FROM generate_series)::INTEGER
        AS year,

    EXTRACT(QUARTER FROM generate_series)::INTEGER
        AS quarter_number,

    'Q' || EXTRACT(
        QUARTER FROM generate_series
    )::INTEGER AS quarter_name,

    EXTRACT(MONTH FROM generate_series)::INTEGER
        AS month_number,

    STRFTIME(generate_series, '%B')
        AS month_name,

    STRFTIME(generate_series, '%Y-%m')
        AS year_month,

    DATE_TRUNC(
        'month',
        generate_series
    )::DATE AS month_start_date,

    EXTRACT(WEEK FROM generate_series)::INTEGER
        AS week_number,

    EXTRACT(DOW FROM generate_series)::INTEGER
        AS day_of_week_number,

    STRFTIME(generate_series, '%A')
        AS day_name,

    CASE
        WHEN EXTRACT(DOW FROM generate_series)
            IN (0, 6)
        THEN TRUE
        ELSE FALSE
    END AS is_weekend

FROM date_spine;