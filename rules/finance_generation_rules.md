# Finance Gold Dataset Generation Rules

## Budget Logic
- Base budget defined per GL account.
- Cost center multiplier applied.
- 4% YoY growth applied.
- Mild intra-year seasonality slope.

## Variance Logic
- 85% small fluctuations.
- 12% moderate volatility.
- 3% large negative shocks.
- Q4 volatility amplified by 40%.

## Materiality
- Material if:
    - Dollar variance >= configured threshold
    OR
    - Percentage variance >= configured threshold

## Governance
- Hard Closed → Final + Signoff True
- Open / Soft Closed → Preliminary
