CREATE OR REPLACE TABLE gold.fact_booking AS
SELECT
    b.booking_id,
    b.source_country AS country_code,
    b.booking_date,
    b.travel_date,

    b.regional_customer_id,
    b.regional_supplier_id,

    b.regional_product,
    b.regional_channel,
    b.destination_country,

    b.transaction_currency,

    b.booking_value_local,
    b.revenue_local,
    b.cost_local,
    b.gross_margin_local,

    b.reporting_currency,
    b.rate_to_reporting_currency,

    b.booking_value_reporting,
    b.revenue_reporting,
    b.cost_reporting,
    b.gross_margin_reporting,

    b.margin_pct,
    b.advance_purchase_days,
    b.booking_status,

    b.customer_scope,
    b.primary_segment,
    b.primary_industry,

    b.supplier_scope,
    b.primary_supplier_type,

    b.source_system,
    b.source_row_number,
    b.staging_loaded_at

FROM intermediate.int_booking_fx b;