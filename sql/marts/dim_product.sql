CREATE OR REPLACE TABLE gold.dim_product AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY regional_product
    ) AS product_key,
    regional_product,
    COUNT(*) AS booking_count

FROM staging.bookings

GROUP BY regional_product;