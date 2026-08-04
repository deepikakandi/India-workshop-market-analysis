# Power BI Pilot Dashboard Plan

Power BI should initially connect to stable tables in the PostgreSQL `powerbi` schema for the Bengaluru and Hyderabad pilot.

## Pilot filters

- City: Bengaluru, Hyderabad
- Category: Cooking and baking, Art and painting, Pottery and ceramics, Coffee making

## Planned pilot pages

1. Market overview: total listings, active organizers, median price, source coverage, and availability coverage.
2. City comparison: Bengaluru versus Hyderabad volume, prices, formats, and demand proxies.
3. Category comparison: volume, pricing, sold-out or registration status, repeat-event signals, and source coverage by pilot category.
4. Product and format view: individual workshops, camps, birthday events, dedicated studio, rented venue, mobile, and online formats.
5. Quality coverage: missing-value rates, duplicate-review queues, classification-confidence coverage, and source coverage by city/category.

The dashboard should not use notebook exports as the primary source. It should consume intentionally modeled `powerbi` tables from dbt.
