# Pilot Notebook Plan

Notebook work should validate the Bengaluru and Hyderabad pilot before full-scale collection.

## Planned notebooks

1. `notebooks/eda/pilot_market_overview.ipynb`
   - Review record counts, source contribution, city coverage, category coverage, date coverage, and missing values.
2. `notebooks/eda/pilot_pricing_review.ipynb`
   - Compare prices for cooking and baking, art and painting, pottery and ceramics, and coffee making.
3. `notebooks/hypothesis_tests/pilot_demand_signals.ipynb`
   - Test whether demand proxies are sufficiently available and comparable across the four pilot categories.
4. `notebooks/feasibility/pilot_business_model_assumptions.ipynb`
   - Explore startup-cost and break-even assumptions for the pilot categories and formats.

Notebook outputs should remain exploratory. Stable analytical outputs should be promoted into dbt models before Power BI consumption.
