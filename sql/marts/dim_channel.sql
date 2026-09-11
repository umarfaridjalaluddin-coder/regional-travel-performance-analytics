CREATE OR REPLACE TABLE gold.dim_channel AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY regional_channel
    ) AS channel_key,
    regional_channel,
    COUNT(*) AS booking_count

FROM staging.bookings

GROUP BY regional_channel;