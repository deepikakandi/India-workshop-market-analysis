# Pilot Scope

The pilot study covers two cities and four initial workshop categories.

The canonical machine-readable taxonomy is `config/taxonomy/pilot_scope.yml`. Seed files, fixtures, and readable planning documents mirror that file and should be refreshed whenever the canonical taxonomy changes.

## Pilot cities

- Bengaluru
- Hyderabad

## Pilot categories

- Cooking and baking
- Art and painting
- Pottery and ceramics
- Coffee making

## Category classification fields

Each classified record should eventually support:

- `primary_category_code`
- `subcategory_code`
- `secondary_category_codes`
- `classification_confidence`
- `classification_method`
- `original_category_text`

The classifier itself is intentionally not implemented on Day 2.

## Category boundary rules

- Coffee painting is `art_and_painting`, not `coffee_making`.
- Coffee-mug painting or decoration is art or pottery depending on the material and activity.
- A workshop hosted at a cafe is not automatically a coffee-making workshop.
- Coffee-flavored cake belongs under cooking and baking.
- Latte art belongs under coffee making.
- Ceramic painting belongs under pottery and ceramics.
- Resin art belongs under art and painting.
- A hybrid workshop may have one primary category and one or more secondary tags.
- Preserve the original source category and title before assigning standardized categories.

## Pilot product types

- Individual workshops
- Camps
- Birthday events

## Pilot formats

- Dedicated studio
- Rented venue
- Mobile
- Online

This scope should be used to validate source accessibility, field consistency, raw-response storage, cleaning rules, entity resolution, dbt models, quality gates, notebooks, and Power BI tables before expanding to the remaining metro cities and categories.

Price tiers are provisional analytical tiers and may be recalibrated after the pilot price distribution is examined.
