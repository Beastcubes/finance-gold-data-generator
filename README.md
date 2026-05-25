Finance Gold Dataset Generator

Deterministic FP&A Gold Layer for AI Explanations

This project generates a governed, AI-ready Finance Gold dataset for Balance vs Actuals and Month-End Close use cases.

The goal is to simulate a production-grade semantic layer that can safely power:

Executive variance explanations

AI narrative generation (Gemini via Vertex AI)

Deterministic finance validation

CFO-ready demonstrations

BigQuery + ADK agent integration

This is not random synthetic data.
This is a deterministic finance simulation engine.

1. Project Purpose

We are building a Gold semantic finance layer that:

Looks like trusted enterprise FP&A data

Includes real business logic

Supports variance drivers

Supports trend analysis

Supports materiality rules

Supports close status and data maturity

Supports deterministic injected business events

This dataset is intended to be loaded into BigQuery and queried by an ADK agent using Vertex AI Gemini for narrative generation.

2. Architecture Overview
finance_gold_generator/
│
├── config/
│   ├── finance_structure.yaml
│   └── materiality.yaml
│
├── generator/
│   └── generate_gold_dataset.py
│
├── validation/
│   └── sanity_checks.py
│
├── rules/
│   └── finance_generation_rules.md
│
├── output/
│   ├── gold_dataset.csv
│   └── gold_dataset.parquet
│
├── analysis.ipynb
├── requirements.txt
└── README.md

3. Locked Gold Schema (29 Columns)

The dataset strictly enforces this schema:

Core Period Metadata

fiscal_year

fiscal_period

fiscal_period_name

period_close_status

Dimensional Layer

cost_center_id

cost_center_name

department_name

gl_account_id

gl_account_name

pnl_category

Financial Measures

actual_amount

budget_amount

variance_amount

variance_pct

variance_direction

is_material

Driver Intelligence

variance_driver

variance_driver_detail

driver_confidence

Comparative Metrics

prior_period_variance_amount

variance_change_vs_prior

variance_trend_direction

rolling_3_period_variance

Close & Governance

has_late_posting

late_posting_amount

late_posting_period_count

data_maturity_level

explanation_readiness

finance_signoff_flag

4. Deterministic Finance Logic
4.1 Budget Engine

Budget is derived from:

Base GL budget

Cost center multiplier

YoY growth factor (4%)

Seasonal factor by fiscal period

This creates:

Structured budget hierarchy

Department size realism

Growth progression

Predictable seasonality

4.2 Variance Engine

Variance % is determined by:

Department volatility bias

Q4 volatility amplification

Controlled probability distribution:

85% normal range

12% moderate swings

3% extreme swings

Variance direction:

Positive variance_amount = Unfavorable

Negative variance_amount = Favorable

Materiality rule:

abs(variance_amount) >= dollar_threshold
OR
abs(variance_pct) >= pct_threshold


Configured in config/materiality.yaml.

4.3 Injected Business Event

We injected a deterministic structured event:

Cloud Expansion Program

Applies to:

FY25 P11

FY25 P12

Engineering cost centers

GL Account 6200 (Cloud Infrastructure)

Effect:

~18% unfavorable variance

Concentrated across Engineering

Labeled as driver: "Cloud Expansion Program"

This allows AI explanations to identify:

Coordinated cost expansion

Programmatic initiative

Multi-center impact

Elevated period risk

This is not random noise.

5. Data Maturity & Close Policy

Close policy defined in YAML:

Open periods

Soft Closed periods

Hard Closed periods

Derived columns:

period_close_status

data_maturity_level

finance_signoff_flag

This simulates enterprise month-end close governance.

6. Dataset Scale

For a mid-size company:

15–20 cost centers

~10 GL accounts

24 periods

Result: ~3,600 rows

This is optimal for:

Demoing AI explanations

Realistic variance density

Controlled complexity

Clear pattern visibility

7. Validation Layer

File: validation/sanity_checks.py

Checks include:

Column count matches schema (29)

No nulls in financial measures

Variance math consistency

Material rows exist

Q4 volatility > Q1 volatility

Run:

python .\validation\sanity_checks.py


Expected output:

=== ALL SANITY CHECKS PASSED ===


This ensures deterministic finance integrity.

8. Notebook Analysis

File: analysis.ipynb

Demonstrates:

Filtering injected event

Top drivers by period

Aggregated variance summaries

Executive-style explanation simulation

Risk tone logic

This notebook simulates how an AI agent would reason — but deterministically.

9. How to Run
Step 1: Install dependencies
pip install -r requirements.txt

Step 2: Generate dataset
python .\generator\generate_gold_dataset.py


Outputs:

output/gold_dataset.csv

output/gold_dataset.parquet

Step 3: Run validation
python .\validation\sanity_checks.py

10. BigQuery & ADK Integration Strategy

This dataset is designed to become:

BigQuery Gold Table or View
    ↓
ADK BigQuery Tool
    ↓
Gemini (Vertex AI)
    ↓
Narrative Explanation
    ↓
Cloud Run Deployment


Hard Rules for AI integration:

All math stays in BigQuery.

Tool returns structured governed JSON.

LLM generates explanation only.

No recalculation inside prompt.

Use service account auth.

GOOGLE_GENAI_USE_VERTEXAI=true.

11. What Makes This Enterprise-Grade

Deterministic generation

Governed schema

Materiality thresholds

Close policy simulation

Programmatic event injection

Trend comparatives

Structured drivers

Validation framework

CFO-ready explanation modeling

This is not synthetic demo data.
This is controlled finance simulation.

12. Next Evolution

Potential extensions:

Late posting simulation

Multi-year rolling forecast logic

Headcount-based expense modeling

Revenue-side modeling

Forecast vs Budget comparison

Auto Insights integration

Full ADK Cloud Run deployment

13. Authoring Philosophy

This project follows a strict enterprise design:

Bronze → Silver → Gold logic mindset

Governed semantic layer

Deterministic reproducibility

CFO explainability

AI narrative separation from math

The dataset is built for AI readiness without sacrificing finance control.