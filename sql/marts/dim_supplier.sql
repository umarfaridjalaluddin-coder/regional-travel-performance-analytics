CREATE OR REPLACE TABLE gold.dim_supplier AS
SELECT
    regional_supplier_id,
    regional_supplier_name,
    supplier_scope,
    local_entity_count,
    country_count,
    primary_supplier_type
FROM master.dim_supplier_master;