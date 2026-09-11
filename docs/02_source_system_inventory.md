# 02 — Source System Inventory

## Purpose

This document defines the fictional source-data landscape used by the Regional Travel Performance Analytics project.

The objective is to simulate a realistic regional environment where Malaysia, Singapore and Indonesia operate with different file structures, field names, currencies and business processes.

All systems, files, records and business rules described here are synthetic and do not represent the actual systems of any organisation.

---

## 1. Regional Source Landscape

The analytical environment contains five major data domains:

| Domain | Purpose |
|---|---|
| Booking / Transaction | Travel bookings and transaction activity |
| Customer | Corporate client and account information |
| Supplier | Airline, hotel and other supplier information |
| Finance | Revenue, cost and financial control totals |
| Payment | Payment and settlement information |

The three countries do not initially provide identical schemas.

This deliberately creates regional integration challenges that must be resolved before management reporting.

---

## 2. Malaysia Sources

### 2.1 Booking Data

**File**

`data/raw/malaysia/bookings.csv`

**Purpose**

Primary Malaysia booking and transaction extract.

**Proposed fields**

| Field | Description |
|---|---|
| booking_id | Local booking identifier |
| booking_date | Date transaction was booked |
| travel_date | Travel start date |
| customer_id | Local corporate customer identifier |
| supplier_id | Local supplier identifier |
| product_type | Air, Hotel, Ground or Other |
| booking_channel | Online or Offline |
| destination_country | Destination |
| currency | Transaction currency |
| booking_value | Gross booking value |
| revenue | Revenue earned |
| cost | Associated cost |
| booking_status | Confirmed, Cancelled or Refunded |
| agent_id | Booking agent where applicable |

---

### 2.2 Customer Data

**File**

`data/raw/malaysia/customers.xlsx`

**Purpose**

Malaysia corporate customer master.

**Proposed fields**

| Field | Description |
|---|---|
| customer_id | Local customer identifier |
| customer_name | Local customer name |
| segment | Customer segment |
| industry | Industry classification |
| account_manager | Account owner |
| contract_start_date | Contract start |
| contract_end_date | Contract end |
| status | Active or inactive |

---

### 2.3 Supplier Data

**File**

`data/raw/malaysia/suppliers.csv`

**Purpose**

Malaysia supplier master.

Fields include:

- supplier_id
- supplier_name
- supplier_type
- preferred_supplier_flag
- country
- status

---

### 2.4 Finance Data

**File**

`data/raw/malaysia/finance.csv`

**Purpose**

Monthly finance control totals used for reconciliation.

Fields include:

- finance_month
- country
- revenue
- cost
- gross_margin
- transaction_count

---

### 2.5 Payment Data

**File**

`data/raw/malaysia/payments.csv`

Potential fields:

- payment_id
- booking_id
- payment_date
- payment_method
- payment_amount
- payment_status
- settlement_date

---

## 3. Singapore Sources

Singapore intentionally uses different names and formats from Malaysia.

### 3.1 Transaction Data

**File**

`data/raw/singapore/transactions.xlsx`

Potential fields:

- transaction_ref
- txn_date
- departure_date
- client_code
- vendor_code
- service_category
- booking_method
- destination
- txn_currency
- gross_sales
- net_revenue
- direct_cost
- status

These fields contain the same underlying business concepts as Malaysia but use different terminology.

For example:

`transaction_ref` → `booking_id`

`client_code` → `customer_id`

`vendor_code` → `supplier_id`

`gross_sales` → `booking_value`

`net_revenue` → `revenue`

---

### 3.2 Customer Data

**File**

`data/raw/singapore/client_master.csv`

Potential fields:

- client_code
- client_name
- customer_tier
- sector
- relationship_manager
- effective_from
- effective_to
- active_flag

---

### 3.3 Supplier Data

**File**

`data/raw/singapore/vendor_master.xlsx`

Potential fields:

- vendor_code
- vendor_name
- vendor_category
- preferred_flag
- vendor_country
- active_flag

---

### 3.4 Finance Data

**File**

`data/raw/singapore/finance_extract.csv`

Potential fields:

- period
- market
- sales_revenue
- operating_cost
- margin
- transactions

---

## 4. Indonesia Sources

Indonesia introduces another variation in source structure.

### 4.1 Booking Data

**File**

`data/raw/indonesia/booking_export.csv`

Potential fields:

- booking_no
- created_at
- journey_date
- account_no
- provider_code
- travel_product
- channel
- destination
- currency_code
- total_booking_amount
- service_revenue
- supplier_cost
- booking_state

---

### 4.2 Customer Data

**File**

`data/raw/indonesia/accounts.xlsx`

Potential fields:

- account_no
- account_name
- account_segment
- business_sector
- account_owner
- start_date
- end_date
- account_status

---

### 4.3 Supplier Data

**File**

`data/raw/indonesia/supplier_export.csv`

Potential fields:

- provider_code
- provider_name
- provider_type
- preferred
- provider_country
- provider_status

---

### 4.4 Finance Data

**File**

`data/raw/indonesia/finance_id.csv`

Potential fields:

- accounting_period
- country_code
- reported_revenue
- reported_cost
- reported_margin
- reported_transactions

---

## 5. Regional Reference Data

Regional reference datasets will be stored under:

`data/reference/`

Planned reference datasets include:

### Country Reference

`country_reference.csv`

Contains:

- country_code
- country_name
- reporting_currency
- region

### Currency Reference

`currency_reference.csv`

Contains:

- currency_code
- reporting_currency
- exchange_rate
- effective_date

For this synthetic case study, exchange rates will be generated explicitly and treated as fictional analytical assumptions.

### Product Mapping

`product_mapping.csv`

Maps country-specific product terminology to a common regional taxonomy.

Example:

| Source Value | Regional Product |
|---|---|
| Flight | Air |
| Airline | Air |
| AIR | Air |
| Accommodation | Hotel |
| HOTEL | Hotel |
| Car | Ground |
| Transfer | Ground |

### Channel Mapping

`channel_mapping.csv`

Standardises channel descriptions into:

- Online
- Offline

### Customer Crosswalk

`customer_crosswalk.csv`

Maps local customer identifiers to a regional customer identity.

Conceptually:

Local Customer  
→ Local Legal Entity  
→ Regional Parent Customer

### Supplier Crosswalk

`supplier_crosswalk.csv`

Maps local supplier identifiers and aliases to a consistent regional supplier identity.

---

## 6. Expected Source-System Problems

The synthetic raw data will deliberately include realistic quality problems.

### Completeness

Examples:

- Missing customer IDs
- Missing supplier IDs
- Missing travel dates
- Missing product categories

### Uniqueness

Examples:

- Duplicate booking IDs
- Duplicate transaction records
- Duplicate customer master entries

### Validity

Examples:

- Invalid currency codes
- Negative booking values where not appropriate
- Impossible dates
- Invalid status values

### Consistency

Examples:

- `Air`
- `AIR`
- `Flight`
- `Flights`

All may represent the same regional product.

### Referential Integrity

Examples:

- Booking references a customer not present in the customer master
- Booking references an unknown supplier

### Financial Reconciliation

Examples:

Booking-derived revenue:

`1,000,000`

Finance reported revenue:

`995,000`

Variance:

`5,000`

The analytical process must preserve and investigate the variance rather than silently forcing the numbers to match.

### Timeliness

Examples:

- Late booking extracts
- Finance periods arriving after operational data
- Delayed customer-master updates

---

## 7. Standard Regional Booking Schema

After standardisation, all countries will map into a common structure.

| Standard Field | Purpose |
|---|---|
| booking_id | Regional transaction identifier |
| source_country | Source market |
| booking_date | Booking date |
| travel_date | Travel date |
| customer_id_local | Original local customer identifier |
| customer_id_regional | Standard regional customer |
| supplier_id_local | Original supplier identifier |
| supplier_id_regional | Standard regional supplier |
| product_type | Standard product |
| booking_channel | Standard channel |
| destination_country | Destination |
| transaction_currency | Original transaction currency |
| booking_value_local | Original booking value |
| revenue_local | Original revenue |
| cost_local | Original cost |
| booking_value_reporting | Converted reporting value |
| revenue_reporting | Converted revenue |
| cost_reporting | Converted cost |
| booking_status | Standard booking status |
| source_system | Source identifier |

Derived fields such as gross margin will be calculated downstream rather than trusted blindly from source extracts.

---

## 8. Data Ownership Model

For this case study, ownership is separated conceptually.

### Country Teams

Responsible for:

- Source-data production
- Local business context
- Local issue clarification

### Business Systems / Data Capability

Responsible for:

- Source integration
- Technical mapping
- Data processing
- Pipeline reliability
- Technical validation

### Finance

Responsible for:

- Financial control totals
- Financial definitions
- Reconciliation review

### Regional Business Performance & Analytics

Responsible for:

- Regional KPI framework
- Analytical definitions
- Performance analysis
- Cross-market comparison
- Forecasting
- Commercial insights
- Management recommendations

The exact organisation structure of a real company may differ. This model is used only for the synthetic case study.

---

## 9. Data Lineage

Conceptual lineage:

Country Source Systems

↓

Raw Extracts

↓

Data Profiling

↓

Data Quality Validation

↓

Standardisation

↓

Master-Data Mapping

↓

Finance Reconciliation

↓

Analytical Data Model

↓

Regional KPIs

↓

Power BI

↓

Management Insight

↓

Business Action

---

## 10. Design Principle

The raw layer must preserve source-system reality.

Raw data should not be manually corrected simply to make downstream reporting easier.

Problems should instead be:

1. Detected
2. Quantified
3. Classified
4. Corrected through reproducible rules where appropriate
5. Escalated where business ownership is required
6. Recorded for auditability

This allows the project to demonstrate not only analytics, but also trust, governance and regional data-management discipline.