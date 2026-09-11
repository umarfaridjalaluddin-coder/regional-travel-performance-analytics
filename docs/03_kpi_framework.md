# 03 — Regional KPI Framework

## Purpose

This document defines the initial KPI framework for the synthetic Regional Travel Performance Analytics project.

The objective is to ensure that Malaysia, Singapore and Indonesia use consistent definitions for business performance reporting.

All KPI definitions in this project are fictional analytical definitions created for demonstration purposes.

---

## 1. KPI Governance Principles

Every KPI should have:

- A clear business definition
- A documented formula
- A defined reporting grain
- A known source
- An accountable business owner
- A validation rule
- A reconciliation approach where required
- A documented treatment of cancellations, refunds and missing data

A KPI should not be included in executive reporting until its definition is sufficiently clear and reproducible.

---

## 2. Reporting Currency

Regional reporting requires a common reporting currency.

For this synthetic project:

- Malaysia source currency: MYR
- Singapore source currency: SGD
- Indonesia source currency: IDR
- Regional reporting currency: MYR

Exchange rates will be synthetic and stored in:

`data/reference/currency_reference.csv`

All converted values will retain both:

- Original local-currency amount
- Regional reporting-currency amount

This allows auditability between source values and regional reporting.

---

## 3. Revenue

### Business Definition

Revenue earned from completed or recognised travel transactions.

### Formula

`Revenue = Sum of recognised transaction revenue`

### Reporting Grain

Can be analysed by:

- Date
- Country
- Customer
- Supplier
- Product
- Channel

### Source

Booking / transaction data.

### Key Validation

Revenue should reconcile to finance control totals within an agreed tolerance.

### Important Treatment

Cancelled or refunded transactions must follow defined accounting treatment rather than being automatically included as normal revenue.

---

## 4. Booking Value

### Business Definition

Gross monetary value of travel booked through the business.

### Formula

`Booking Value = Sum of booking transaction value`

### Purpose

Used to understand:

- Customer travel spend
- Supplier volume
- Product demand
- Market activity

Booking value is not the same as revenue.

---

## 5. Cost

### Business Definition

Direct transaction-related cost associated with providing the travel product or service.

### Formula

`Cost = Sum of recognised direct transaction costs`

### Primary Use

Supports gross-margin analysis.

---

## 6. Gross Margin

### Formula

`Gross Margin = Revenue - Cost`

### Purpose

Measures the absolute commercial contribution generated after direct transaction cost.

---

## 7. Gross Margin %

### Formula

`Gross Margin % = Gross Margin / Revenue`

Where revenue is greater than zero.

### Purpose

Allows profitability comparison across:

- Countries
- Customers
- Suppliers
- Products
- Channels

### Data-Quality Rule

Division by zero must be handled explicitly.

---

## 8. Transaction Count

### Definition

Number of valid recognised booking transactions.

### Formula

`Transaction Count = Count of valid unique booking IDs`

### Validation

Duplicate booking IDs must not artificially inflate transaction count.

---

## 9. Revenue per Transaction

### Formula

`Revenue per Transaction = Revenue / Transaction Count`

### Purpose

Indicates average revenue generated per transaction.

---

## 10. Booking Value per Transaction

### Formula

`Booking Value per Transaction = Booking Value / Transaction Count`

### Purpose

Indicates average transaction size.

---

## 11. Active Customers

### Definition

Number of distinct customers with at least one valid recognised transaction during the reporting period.

### Formula

`Active Customers = Distinct Count of Regional Customer IDs`

### Grain

Typically calculated monthly, quarterly and annually.

---

## 12. Customer Growth

### Formula

`Customer Revenue Growth % = (Current Period Revenue - Prior Period Revenue) / Prior Period Revenue`

Equivalent calculations may also be performed for:

- Booking value
- Transactions
- Gross margin

### Comparison Periods

Examples:

- Month over Month
- Quarter over Quarter
- Year over Year
- Rolling 12 Months versus Prior Rolling 12 Months

---

## 13. Customer Retention

### Concept

Measures whether customers active in a prior period remain active in the current comparison period.

### Example Formula

`Retention Rate = Retained Customers / Prior Period Active Customers`

The exact comparison period must always be stated.

---

## 14. Customer Concentration

### Purpose

Measures dependency on a relatively small number of customers.

Potential measures include:

- Top 5 Customer Revenue %
- Top 10 Customer Revenue %
- Top 20 Customer Revenue %

### Example

`Top 10 Revenue Concentration = Revenue from Top 10 Customers / Total Revenue`

High concentration may represent both:

- Commercial strength
- Customer-dependency risk

Interpretation requires business context.

---

## 15. Customer Profitability

Customer profitability will be evaluated using:

- Revenue
- Gross margin
- Gross margin %
- Transaction volume
- Booking value

The project will not assume that the highest-booking-value customer is automatically the most profitable customer.

---

## 16. Country Contribution %

### Formula

`Country Contribution % = Country Revenue / Regional Revenue`

Equivalent measures may be calculated for:

- Booking value
- Margin
- Transactions

---

## 17. Actual versus Target

### Absolute Variance

`Variance = Actual - Target`

### Percentage Variance

`Variance % = (Actual - Target) / Target`

### Measures

Targets may exist for:

- Revenue
- Gross margin
- Transactions
- Booking value

---

## 18. Supplier Share

### Formula

`Supplier Share % = Supplier Booking Value / Total Booking Value`

Can be calculated by:

- Country
- Product
- Customer segment

### Purpose

Supports:

- Supplier negotiation
- Concentration analysis
- Preferred supplier monitoring
- Commercial planning

---

## 19. Supplier Concentration

Potential measures:

- Top Supplier Share
- Top 5 Supplier Share
- Top 10 Supplier Share

High concentration may indicate:

- Strong negotiating leverage
- Dependency risk

The interpretation should not be automated without business context.

---

## 20. Preferred Supplier Adoption

### Formula

`Preferred Supplier Adoption % = Eligible Transactions Using Preferred Suppliers / Eligible Transactions`

### Requirement

The denominator must only include transactions where preferred-supplier usage is applicable.

---

## 21. Product Mix

### Formula

`Product Mix % = Product Booking Value / Total Booking Value`

May also be calculated based on:

- Revenue
- Transactions
- Gross margin

Main product categories:

- Air
- Hotel
- Ground
- Other

---

## 22. Channel Mix

Primary categories:

- Online
- Offline

### Formula

`Channel Share % = Channel Transactions / Total Transactions`

---

## 23. Online Adoption

### Formula

`Online Adoption % = Eligible Online Transactions / Eligible Transactions`

### Important Requirement

Eligibility must be explicitly defined.

Transactions that cannot reasonably be completed through the online channel should not automatically reduce the adoption rate.

---

## 24. Advance Purchase Days

### Formula

`Advance Purchase Days = Travel Date - Booking Date`

### Potential Reporting

- Average advance-purchase days
- Median advance-purchase days
- Distribution by customer
- Distribution by country
- Distribution by product

### Data-Quality Rule

Negative values require investigation.

---

## 25. Advance Purchase Compliance

A hypothetical policy threshold may be defined for eligible Air transactions.

Example synthetic rule:

`Compliant if Advance Purchase Days >= Defined Policy Threshold`

The threshold should be stored as configurable reference data rather than permanently hard-coded into dashboards.

---

## 26. Policy Compliance

### Concept

Percentage of eligible transactions satisfying defined travel-policy rules.

### Formula

`Policy Compliance % = Compliant Eligible Transactions / Total Eligible Transactions`

Potential policy dimensions:

- Advance purchase
- Preferred supplier
- Booking channel
- Product selection

The project will use synthetic policies only.

---

## 27. Hotel Attachment

### Purpose

Identifies customers purchasing air travel without corresponding hotel activity where hotel travel may reasonably be expected.

### Conceptual Formula

`Hotel Attachment % = Qualifying Trips with Hotel Booking / Qualifying Trips Requiring Accommodation`

A simplified portfolio implementation may use account-level air-versus-hotel behaviour.

### Interpretation

Low attachment can indicate a cross-sell opportunity, but it should not automatically be classified as leakage without additional evidence.

---

## 28. Potential Leakage

Leakage cannot be definitively identified using internal booking data alone.

The synthetic project may therefore define a proxy signal such as:

- High Air activity
- Low or zero Hotel activity
- Historical evidence of multi-day travel

This should be labelled:

`Potential Leakage Indicator`

rather than proven leakage.

---

## 29. Cancellation Rate

### Formula

`Cancellation Rate = Cancelled Transactions / Total Booked Transactions`

### Requirement

The denominator definition must remain consistent across reporting periods.

---

## 30. Refund Rate

### Formula

`Refund Rate = Refunded Transactions / Eligible Transactions`

The financial effect of refunds should be separately analysed.

---

## 31. Data Completeness

### Formula

For a critical field:

`Completeness % = Non-null Valid Records / Total Records`

Critical fields may include:

- Booking ID
- Customer ID
- Supplier ID
- Booking Date
- Currency
- Booking Value

---

## 32. Uniqueness

### Example

`Duplicate Rate = Duplicate Critical-Key Records / Total Records`

Booking identifiers are expected to meet defined uniqueness rules.

---

## 33. Referential Integrity

### Formula

`Valid Reference % = Records Matching Master Data / Records Requiring Master-Data Match`

Examples:

- Booking to customer master
- Booking to supplier master

---

## 34. Finance Reconciliation

### Revenue Variance

`Revenue Variance = Booking-derived Revenue - Finance Revenue`

### Cost Variance

`Cost Variance = Booking-derived Cost - Finance Cost`

### Margin Variance

`Margin Variance = Booking-derived Margin - Finance Margin`

### Principle

Variances must be reported transparently.

The project will not alter operational data merely to force reconciliation to zero.

---

## 35. Data Freshness

### Concept

Measures whether expected source data has arrived within an agreed reporting window.

Potential measure:

`Data Age = Current Reporting Date - Latest Available Source Date`

Freshness thresholds will be configurable.

---

## 36. Forecast Revenue

Revenue forecasts will initially use transparent statistical baselines.

Potential models:

- Naive
- Seasonal Naive
- Moving Average
- Exponential Smoothing

More complex models will only be introduced if they materially improve performance.

---

## 37. Forecast Accuracy

Potential evaluation metrics:

### MAE

`Mean Absolute Error`

### RMSE

`Root Mean Squared Error`

### WAPE

`Weighted Absolute Percentage Error`

For business reporting, WAPE may be easier to interpret across larger aggregated values.

Model selection should be based on validation performance rather than complexity.

---

## 38. Commercial Opportunity Indicators

The project will generate explainable opportunity signals rather than opaque scores.

Examples:

### Retention Risk

High-value customer with sustained decline in revenue or margin.

### Hotel Cross-Sell

High Air activity with comparatively low Hotel activity.

### Digital Adoption

High eligible offline transaction share.

### Supplier Opportunity

High transaction volume concentrated with a supplier where negotiation may be commercially relevant.

### Growth Opportunity

Customer, product or route demonstrating sustained growth.

Every opportunity should retain the analytical evidence that caused it to be flagged.

---

## 39. KPI Ownership Model

For this synthetic operating model:

### Finance

Primary owner of:

- Finance reported revenue
- Finance reported cost
- Finance reported margin
- Financial control totals

### Regional Business Performance & Analytics

Primary owner of:

- Analytical KPI definitions
- Regional comparison methodology
- Performance analysis
- Forecasting methodology
- Commercial opportunity logic

### Business Systems / Data

Primary owner of:

- Technical source mappings
- Transformation execution
- Pipeline reliability
- Technical data validation

### Country Teams

Responsible for:

- Local interpretation
- Source clarification
- Market context

Ownership does not mean functions operate independently. KPI governance requires shared agreement across relevant stakeholders.

---

## 40. KPI Dictionary Structure

The final machine-readable KPI dictionary should eventually contain fields such as:

| Field | Description |
|---|---|
| kpi_id | Unique KPI identifier |
| kpi_name | KPI name |
| business_definition | Plain-language definition |
| formula | Calculation |
| numerator | Numerator where relevant |
| denominator | Denominator where relevant |
| grain | Reporting grain |
| source | Primary source |
| owner | Business owner |
| reporting_currency | Currency treatment |
| exclusions | Excluded records |
| validation_rule | Validation logic |
| status | Draft / Approved / Deprecated |
| effective_date | Governance date |

The initial dictionary will later be stored as structured reference data.

---

## 41. Management Interpretation Principle

A KPI is not an insight by itself.

For example:

`Indonesia Revenue Growth = -8%`

is a measurement.

The analytical process must continue by asking:

- Which customers drove the decline?
- Which products were affected?
- Was transaction volume lower?
- Did average transaction value change?
- Did supplier or channel mix change?
- Is the decline temporary or sustained?
- What action should management consider?

The final analytical workflow is therefore:

KPI  
→ Driver Analysis  
→ Business Interpretation  
→ Recommendation  
→ Action  
→ Follow-up Measurement