# 01 — Business Requirements

## Project Context

This is an independent synthetic portfolio case study for a regional corporate travel analytics environment.

The fictional business operates across:

- Malaysia
- Singapore
- Indonesia

Each country currently produces operational and financial data from different source systems and file formats.

The regional leadership team needs a consistent and trusted way to understand business performance, customer behaviour, supplier performance, travel demand, commercial opportunities and future performance.

All data used in this project will be synthetic.

---

## 1. Business Objective

Build a regional business performance and analytics capability that enables leadership to:

1. Understand current regional and country performance.
2. Identify growth, decline and emerging risks.
3. Compare performance consistently across markets.
4. Understand customer profitability and behaviour.
5. Evaluate supplier and product performance.
6. Monitor travel programme behaviour and compliance.
7. Improve confidence in reported KPIs.
8. Identify commercial opportunities.
9. Support forecasting and planning.
10. Translate analytical findings into management actions.

---

## 2. Core Management Questions

### Regional Performance

Leadership should be able to answer:

- How is the region performing overall?
- Which countries are growing or declining?
- Which markets are above or below target?
- What is driving changes in revenue, booking value and margin?
- Are regional results concentrated in a small number of customers?
- Which products and channels are contributing most to performance?
- Where are the major performance risks?

### Country Performance

For Malaysia, Singapore and Indonesia:

- What are the main drivers of country performance?
- Which customer segments perform best?
- Which products are growing or declining?
- Are performance trends consistent across countries?
- Which successful practices may be transferable between markets?
- Are there market-specific issues requiring different actions?

### Customer Performance

Management should understand:

- Who are the highest-value customers?
- Which customers generate the highest revenue and gross margin?
- Which customers are becoming more or less active?
- Which accounts show signs of decline?
- Which customers have low profitability despite high booking value?
- Is revenue excessively concentrated among a small group of customers?
- Which accounts may present retention, cross-sell or growth opportunities?

### Supplier Performance

Management should understand:

- Which suppliers generate the most business?
- Which suppliers contribute the strongest margins?
- Is supplier concentration creating commercial or operational risk?
- Which suppliers are growing or declining?
- Are preferred suppliers being used effectively?
- Where might there be negotiation opportunities based on transaction volume?

### Product and Channel Performance

The business should be able to compare:

- Air
- Hotel
- Ground transport
- Other travel-related products

And understand:

- Product revenue
- Product booking value
- Product margin
- Transaction volume
- Product mix
- Channel mix
- Online versus offline adoption
- Changes in customer purchasing behaviour

### Travel Programme Analytics

The analytical capability should support travel-management questions such as:

- Are customers increasing online booking adoption?
- Are travellers booking sufficiently in advance?
- Are preferred suppliers being used?
- Are bookings compliant with travel policy?
- Are customers booking air but not hotel through the company?
- Are transactions potentially leaking outside the managed programme?
- Which accounts show opportunities for travel programme optimisation?

### Finance and Data Trust

Leadership should be able to trust the numbers used for decision-making.

The solution should therefore answer:

- Do booking-system totals reconcile with finance totals?
- Are key customer, supplier and transaction identifiers complete?
- Are duplicate transactions present?
- Are currencies consistently handled?
- Are customer and supplier names mapped consistently?
- Are all countries using the same KPI definitions?
- Which data-quality problems could materially affect management reporting?

### Forecasting and Planning

Regional management should understand:

- What level of business activity is expected in coming periods?
- Which countries or customers may grow or decline?
- Where is actual performance diverging from forecast?
- What emerging risks require management attention?
- What commercial opportunities should leadership prioritise?

---

## 3. Initial KPI Categories

The initial regional KPI framework will cover:

### Commercial Performance

- Revenue
- Booking Value
- Gross Margin
- Gross Margin %
- Transaction Count
- Revenue per Transaction
- Booking Value per Transaction

### Customer Performance

- Active Customers
- Revenue by Customer
- Gross Margin by Customer
- Customer Growth
- Customer Retention
- Customer Concentration
- Customer Profitability

### Market Performance

- Revenue by Country
- Margin by Country
- Transactions by Country
- Country Growth
- Actual versus Target
- Market Contribution %

### Supplier Performance

- Supplier Booking Value
- Supplier Revenue
- Supplier Margin
- Supplier Share
- Preferred Supplier Usage
- Supplier Concentration

### Product and Channel

- Product Mix
- Channel Mix
- Online Adoption
- Offline Share
- Average Transaction Value

### Travel Programme Performance

- Advance Purchase
- Policy Compliance
- Preferred Supplier Adoption
- Hotel Attachment
- Potential Leakage
- Cancellation Rate
- Refund Rate

### Data Quality

- Completeness
- Uniqueness
- Validity
- Consistency
- Referential Integrity
- Timeliness
- Finance Reconciliation Variance

### Planning

- Forecast Revenue
- Forecast Booking Value
- Forecast Transactions
- Forecast Accuracy
- Actual versus Forecast

---

## 4. Expected Analytical Outputs

The project will ultimately produce three main analytical products.

### A. Regional Management Analytics

Designed for regional leadership.

Focus:

- Regional performance
- Country comparison
- Commercial trends
- Customer performance
- Supplier performance
- Product and channel mix
- Targets
- Forecasts
- Risks
- Opportunities

### B. Corporate Client Travel Analytics

Designed to demonstrate client-level travel programme analytics.

Focus:

- Client spend
- Travel behaviour
- Online adoption
- Advance purchase
- Policy compliance
- Preferred supplier usage
- Hotel attachment
- Potential savings and optimisation opportunities

### C. Data and Operations Control

Designed to demonstrate data trust and operational governance.

Focus:

- Data quality
- Missing keys
- Duplicate records
- Mapping failures
- Reconciliation
- Pipeline completeness
- Data freshness
- Critical reporting issues

---

## 5. Decision-Making Principle

The project will not treat dashboards as the final output.

The analytical process should follow:

Business Question  
→ Trusted Data  
→ KPI  
→ Analysis  
→ Insight  
→ Recommendation  
→ Management Action  
→ Measurable Outcome

Technical implementation exists to support business decisions rather than becoming the objective itself.

---

## 6. Scope

### In Scope

- Malaysia
- Singapore
- Indonesia
- Synthetic booking data
- Synthetic customer data
- Synthetic supplier data
- Synthetic finance data
- Synthetic targets
- Data quality
- Reconciliation
- Customer analytics
- Supplier analytics
- Product analytics
- Channel analytics
- Travel programme analytics
- Forecasting
- Commercial opportunity identification
- Power BI reporting

### Out of Scope for Initial Version

- Real company data
- Real customer information
- Real supplier contracts
- Production APIs
- Live GDS integrations
- Real payment gateway integrations
- Enterprise cloud deployment
- Streaming analytics
- Machine-learning infrastructure
- Generative AI
- Spark
- Kafka
- Kubernetes

These may be discussed as future extensions where appropriate, but they are not required to demonstrate the core regional analytics capability.

---

## 7. Success Criteria

The project will be considered successful when it can demonstrate:

1. Consistent KPI definitions across all three countries.
2. Reproducible data-quality checks.
3. Transparent finance reconciliation.
4. Standardised customer and supplier identities.
5. A dimensional analytical model.
6. Regional performance reporting.
7. Customer and supplier insights.
8. Travel programme analytics.
9. Basic forecasting.
10. Commercial opportunity identification.
11. Management-ready Power BI outputs.
12. A clear explanation of how insights lead to actions.

---

## 8. Portfolio Disclaimer

This repository is an independent synthetic portfolio project.

It does not contain confidential or proprietary information belonging to Peter Stuyvesant Travel or any other organisation.

The fictional source systems, datasets, business rules, KPIs and architecture are created solely for learning, demonstration and interview preparation purposes.