# Regional Travel Performance Analytics

Independent synthetic portfolio project demonstrating an end-to-end regional business performance and analytics operating model for a corporate travel environment.

## Purpose

This project demonstrates how fragmented regional travel data can be transformed into trusted management information for commercial performance, customer analytics, supplier performance, forecasting, and executive decision-making.

The project simulates regional operations across:

- Malaysia
- Singapore
- Indonesia

> **Disclaimer:** All data in this repository is synthetic. This project does not contain confidential company information and does not claim to represent the actual internal architecture, data model, systems, processes, or commercial performance of Peter Stuyvesant Travel or any other organisation.

## Business Scenario

The simulated business operates across multiple regional markets where booking, customer, supplier, finance, and operational data originate from different source systems and file formats.

The objective is to develop a trusted regional analytics capability supporting:

- Regional business performance
- Customer profitability
- Supplier performance
- Commercial opportunity identification
- Travel programme analytics
- Data quality monitoring
- Finance reconciliation
- Forecasting and planning
- Executive reporting

## Architecture

The project follows this analytical flow:

**Business Requirements → Raw Data → Data Profiling & Quality → Cleaning & Standardisation → Master Data → Finance Reconciliation → DuckDB & SQL → Star Schema → Analytics → Power BI → Management Insights & Actions**

## Technology Stack

### Core

- Python 3.12
- pandas
- NumPy
- Faker
- PyArrow / Parquet
- DuckDB
- SQL
- Pandera
- pytest
- Power BI
- Power Query
- DAX
- Git / GitHub

### Supporting

- Jupyter
- Ruff
- statsmodels
- matplotlib

## Repository Structure

```text
regional-travel-performance-analytics/
├── config/
├── data/
│   ├── raw/
│   │   ├── malaysia/
│   │   ├── singapore/
│   │   └── indonesia/
│   ├── reference/
│   ├── staging/
│   ├── silver/
│   └── gold/
├── src/
├── sql/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   └── analysis/
├── tests/
├── notebooks/
├── database/
├── powerbi/
├── docs/
├── outputs/
└── presentation/
```

## Planned Development

The project will progressively cover:

1. Business requirements and analytical questions
2. Source-system inventory
3. Synthetic regional data generation
4. Raw-data inspection and profiling
5. Data-quality framework
6. Data contracts
7. Cleaning and standardisation
8. Customer, supplier, and product master data
9. Finance reconciliation
10. DuckDB staging and SQL transformations
11. Dimensional/star-schema modelling
12. Automated data tests
13. KPI governance
14. Regional performance analytics
15. Customer profitability analytics
16. Supplier analytics
17. Travel programme analytics
18. Commercial opportunity identification
19. Forecasting
20. Power BI semantic modelling and DAX
21. Regional executive dashboards
22. Data-quality and operational-control dashboards
23. UAT and governance
24. Executive presentation

## Management Perspective

The project is designed around the decision-making journey:

**Business Problem → Data → Trust → Analysis → Insight → Recommendation → Action**

The objective is not simply to build pipelines and dashboards. The technical implementation exists to support trusted regional business decisions.

## Project Status

**Stage 0 — Development environment:** Complete  
**Stage 1 — Repository foundation:** In progress