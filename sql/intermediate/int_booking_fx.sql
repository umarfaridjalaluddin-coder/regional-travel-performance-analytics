CREATE OR REPLACE TABLE intermediate.int_booking_fx AS
SELECT
    b.*,

    fx.reporting_currency,
    fx.rate_to_reporting_currency,
    fx.rate_type,

    b.booking_value_local
        * fx.rate_to_reporting_currency
        AS booking_value_reporting,

    b.revenue_local
        * fx.rate_to_reporting_currency
        AS revenue_reporting,

    b.cost_local
        * fx.rate_to_reporting_currency
        AS cost_reporting,

    b.gross_margin_local
        * fx.rate_to_reporting_currency
        AS gross_margin_reporting

FROM intermediate.int_bookings_enriched b

LEFT JOIN reference.currency_reference fx
    ON b.booking_month = fx.effective_month
    AND b.transaction_currency = fx.currency_code;