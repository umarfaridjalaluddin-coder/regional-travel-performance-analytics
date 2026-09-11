CREATE OR REPLACE TABLE gold.dim_country AS
SELECT DISTINCT
    source_country AS country_code,

    CASE source_country
        WHEN 'MY' THEN 'Malaysia'
        WHEN 'SG' THEN 'Singapore'
        WHEN 'ID' THEN 'Indonesia'
        ELSE source_country
    END AS country_name,

    CASE source_country
        WHEN 'MY' THEN 'MYR'
        WHEN 'SG' THEN 'SGD'
        WHEN 'ID' THEN 'IDR'
        ELSE NULL
    END AS local_currency,

    'MYR' AS reporting_currency

FROM staging.bookings;