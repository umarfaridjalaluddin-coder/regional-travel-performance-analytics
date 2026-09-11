# 04 — Operating Model

## Purpose

This document defines the proposed operating model for the synthetic Regional Travel Performance Analytics project.

The objective is to clarify how Regional Business Performance & Analytics works with Finance, Business Systems / Data, and Country Teams.

This is a fictional operating model created for portfolio and interview preparation purposes.

---

## 1. Core Principle

Regional analytics should not operate as an isolated reporting function.

The operating model should connect:

Business Questions  
→ Data  
→ Validation  
→ Analysis  
→ Decision  
→ Action  
→ Measurement

Each function has a different responsibility within this process.

---

## 2. Regional Business Performance & Analytics

### Primary Role

Own the regional performance framework and convert trusted data into management insight.

### Responsibilities

- Define regional KPI methodology
- Standardise performance measurement across markets
- Analyse country and regional performance
- Identify commercial drivers
- Analyse customer profitability
- Analyse supplier performance
- Evaluate product and channel mix
- Support forecasting and planning
- Identify risks and commercial opportunities
- Present insights to leadership
- Recommend management actions
- Monitor whether actions improve results
- Coordinate cross-market performance reviews
- Promote analytical best practices across countries

### Does Not Automatically Own

- Every source-system integration
- Every ETL pipeline
- Production infrastructure
- Enterprise application administration
- Finance accounting rules
- Vendor technical implementation

The Regional Head should understand these areas sufficiently to govern outcomes, challenge assumptions and ensure analytical requirements are met.

---

## 3. Business Systems / Data

### Primary Role

Translate business requirements into reliable data and system outcomes.

### Responsibilities

- Source-system integration
- Technical source mapping
- Data extraction
- Transformation implementation
- Pipeline reliability
- Data validation
- System workflow support
- Integration troubleshooting
- Technical documentation
- Data model implementation
- UAT support
- Vendor coordination where relevant

### Relationship with Regional Analytics

Regional Analytics defines:

- What management needs to know
- Which KPIs are required
- How business concepts should be interpreted
- Which analytical outcomes are needed

Business Systems / Data supports:

- How required source data is obtained
- How data is transformed
- How technical rules are implemented
- How pipelines remain reliable

---

## 4. Finance

### Primary Role

Own financial control and accounting interpretation.

### Responsibilities

- Finance control totals
- Revenue recognition guidance
- Cost treatment
- Margin control
- Accounting-period reporting
- Financial reconciliation review
- Explanation of finance adjustments
- Approval of finance-related definitions where required

### Relationship with Regional Analytics

Regional Analytics should not silently override Finance values.

Where operational and Finance reporting differ:

1. Calculate the variance.
2. Quantify the materiality.
3. Investigate the cause.
4. Document the explanation.
5. Resolve through agreed business rules.
6. Preserve the audit trail.

---

## 5. Country Teams

### Primary Role

Provide local market context and source clarification.

### Responsibilities

- Explain local business processes
- Clarify source-data issues
- Validate local interpretations
- Provide market context
- Support customer and supplier interpretation
- Identify local commercial issues
- Implement agreed actions
- Provide feedback on regional reporting

### Regional Relationship

Regional consistency should not eliminate legitimate local differences.

The Regional Head should distinguish between:

- Inconsistent definitions that require standardisation
- Genuine market differences that should remain visible

---

## 6. Executive Leadership

### Primary Role

Use the analytical outputs to make decisions and set priorities.

Leadership requires:

- Trusted performance information
- Clear explanations of drivers
- Forward-looking risks
- Commercial opportunities
- Recommended actions
- Accountability for follow-up

Regional Analytics should avoid overwhelming leadership with technical detail unless that detail materially affects the decision.

---

## 7. Proposed Information Flow

### Step 1 — Business Question

Example:

Why is one market underperforming against target?

### Step 2 — Analytical Requirement

Define:

- KPI
- comparison period
- required dimensions
- source requirements

### Step 3 — Data Provision

Business Systems / Data produces reliable inputs from the required sources.

### Step 4 — Validation

Data Quality and Finance checks establish whether the numbers are sufficiently trustworthy.

### Step 5 — Analysis

Regional Analytics evaluates:

- customer drivers
- supplier drivers
- product mix
- channel mix
- transaction behaviour
- country trends

### Step 6 — Insight

Example:

Underperformance is concentrated within a small group of declining corporate accounts rather than a market-wide decline.

### Step 7 — Recommendation

Example:

Prioritise retention activity for high-value declining accounts.

### Step 8 — Action

Commercial or country teams execute agreed actions.

### Step 9 — Measurement

Regional Analytics monitors whether performance improves after intervention.

---

## 8. Example RACI

Legend:

- R = Responsible
- A = Accountable
- C = Consulted
- I = Informed

| Activity | Regional Analytics | Business Systems / Data | Finance | Country Teams | Leadership |
|---|---|---|---|---|---|
| Define regional KPIs | A/R | C | C | C | I |
| Source extraction | C | A/R | I | C | I |
| Technical mapping | C | A/R | C | C | I |
| Data quality rules | A/R | R | C | C | I |
| Finance reconciliation | R | C | A/R | C | I |
| Customer master mapping | A | R | C | R | I |
| Supplier master mapping | A | R | C | R | I |
| Regional performance analysis | A/R | C | C | C | I |
| Forecasting | A/R | C | C | C | I |
| Commercial opportunity analysis | A/R | C | C | C | I |
| Executive reporting | A/R | C | C | I | I |
| Market interpretation | A | I | C | R | I |
| Management decision | C | I | C | C | A/R |
| Action implementation | C | I | I | R | A |
| Post-action measurement | A/R | C | C | C | I |

This RACI is illustrative and may change based on actual organisational structure.

---

## 9. Regional Head Operating Rhythm

A possible regional operating rhythm could include:

### Weekly

- Data-quality exceptions
- Major performance movements
- Significant customer issues
- Commercial risks
- Critical operational anomalies

### Monthly

- Regional performance review
- Country comparison
- Customer performance
- Supplier performance
- Actual versus target
- Forecast update
- Opportunity pipeline

### Quarterly

- Strategic customer trends
- Supplier concentration
- Product and channel shifts
- Travel programme optimisation
- Cross-market best-practice review
- Forecast and planning assumptions

The exact cadence should reflect business needs rather than being fixed unnecessarily.

---

## 10. Player-Coach Model

Where the analytics team is small, the Regional Head may need to operate as a player-coach.

This means being able to:

- Review SQL
- Understand data transformations
- Validate analytical logic
- Build prototypes
- Challenge data-quality issues
- Support dashboard design

However, the role should still remain focused on:

- Prioritisation
- Governance
- Interpretation
- Stakeholder alignment
- Commercial outcomes
- Capability development

The Regional Head should not become a bottleneck by personally owning every technical task.

---

## 11. Capability Maturity

### Level 1 — Data Trust

Focus:

- source inventory
- data quality
- reconciliation
- master data
- KPI definitions

### Level 2 — Performance Visibility

Focus:

- regional reporting
- country comparison
- customer analysis
- supplier analysis
- product and channel performance

### Level 3 — Travel Programme Intelligence

Focus:

- online adoption
- policy compliance
- advance purchase
- preferred suppliers
- hotel attachment
- potential leakage

### Level 4 — Proactive Analytics

Focus:

- forecasting
- anomaly detection
- account-health monitoring
- opportunity identification
- scenario analysis

### Level 5 — Advanced Analytics

Potential future capabilities:

- predictive modelling
- automated recommendations
- optimisation
- AI-assisted analytics

Advanced capabilities should only be introduced after the underlying data and KPI foundations are trusted.

---

## 12. Escalation Principles

Issues should be escalated based on business impact.

Examples:

### Critical

- Material finance-reconciliation failure
- Missing country data
- Major reporting inconsistency
- Broken executive KPI
- Severe source-quality failure

### High

- Large master-data mapping issue
- Significant customer mismatch
- Supplier mapping problem
- Delayed critical extract

### Medium

- Non-critical missing attributes
- Small mapping gaps
- Limited reporting delay

### Low

- Cosmetic dashboard issue
- Non-material descriptive-field issue

Severity should be based on impact rather than technical inconvenience.

---

## 13. Management Communication

Executive communication should follow:

Issue  
→ Impact  
→ Cause  
→ Recommendation  
→ Owner  
→ Next Action

Example:

Issue: Indonesia revenue is below target.

Impact: Regional growth is being reduced by the market.

Cause: Analysis shows the decline is concentrated in several high-value corporate accounts.

Recommendation: Conduct targeted account reviews and identify whether decline is due to reduced travel demand, share loss or service issues.

Owner: Country Commercial Lead.

Next Action: Review the identified accounts and report findings at the next performance meeting.

---

## 14. Governance Principle

Analytics governance should enable decision-making rather than create unnecessary bureaucracy.

The minimum governance objective is:

- consistent definitions
- trusted data
- clear ownership
- transparent assumptions
- reproducible analysis
- traceable decisions

---

## 15. Portfolio Positioning

For this synthetic case study, the complete technical pipeline may be implemented personally to demonstrate end-to-end understanding.

In a real organisation, implementation responsibilities would depend on the existing team structure.

The Regional Head should therefore be able to understand the complete analytical chain while ensuring the correct ownership model is established across Analytics, Business Systems / Data, Finance and Country Teams.