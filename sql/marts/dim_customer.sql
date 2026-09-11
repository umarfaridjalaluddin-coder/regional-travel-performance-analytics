CREATE OR REPLACE TABLE gold.dim_customer AS
SELECT
    regional_customer_id,
    regional_customer_name,
    customer_scope,
    local_entity_count,
    country_count,
    primary_segment,
    primary_industry
FROM master.dim_customer_master;