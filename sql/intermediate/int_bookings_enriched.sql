CREATE OR REPLACE TABLE intermediate.int_bookings_enriched AS
SELECT
    b.source_country,
    b.booking_id,
    CAST(b.booking_date AS DATE) AS booking_date,
    CAST(b.travel_date AS DATE) AS travel_date,
    b.customer_id_local,
    b.regional_customer_id,
    b.supplier_id_local,
    b.regional_supplier_id,
    b.product_type_source,
    b.regional_product,
    b.booking_channel_source,
    b.regional_channel,
    b.destination_country,
    b.transaction_currency,
    b.booking_value_local,
    b.revenue_local,
    b.cost_local,
    b.gross_margin_local,
    b.margin_pct,
    b.advance_purchase_days,
    b.booking_status,
    b.source_system,
    b.source_row_number,
    b.staging_loaded_at,

    DATE_TRUNC(
        'month',
        CAST(b.booking_date AS DATE)
    )::DATE AS booking_month,

    DATE_TRUNC(
        'month',
        CAST(b.travel_date AS DATE)
    )::DATE AS travel_month,

    c.regional_customer_name,
    c.customer_scope,
    c.local_entity_count AS customer_local_entity_count,
    c.country_count AS customer_country_count,
    c.primary_segment,
    c.primary_industry,

    s.regional_supplier_name,
    s.supplier_scope,
    s.local_entity_count AS supplier_local_entity_count,
    s.country_count AS supplier_country_count,
    s.primary_supplier_type

FROM staging.bookings b

LEFT JOIN master.dim_customer_master c
    ON b.regional_customer_id = c.regional_customer_id

LEFT JOIN master.dim_supplier_master s
    ON b.regional_supplier_id = s.regional_supplier_id;