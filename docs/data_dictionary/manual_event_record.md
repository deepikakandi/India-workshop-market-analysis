# Manual Event Record Data Dictionary

Day 4 defines the import contract for the Day 5 limited manual pilot. This contract is for manually transcribed factual workshop/course fields from individually reviewed first-party sources only. It is not a scraper contract and does not authorize automated collection.

## Source and evidence requirements

Every record must include `source_id`, `source_url`, `evidence_url`, and a timezone-aware `observed_at` timestamp. The `source_id` must exist in `docs/source_register/source_register.csv`, and the source must have `collection_decision = approved_manual_collection` for the intended manual scope.

Researchers must write a short factual `description_short_original` themselves. Do not copy full source descriptions, marketing copy, images, image URLs, customer names, reviews, cookies, credentials, payment data, or authorization material.

## Field groups

- Record identity: `manual_record_id`, `source_id`, `source_record_identifier`, `source_url`, `evidence_url`, `observed_at`, `entered_by`, `verified_by`, `verification_status`.
- Workshop identity: original title, organizer, venue, city, locality, source category, and short researcher-written description.
- Standardized fields: pilot city/category codes plus subcategory, secondary categories, product type, delivery format, operating model, audience, age range, and skill level.
- Schedule: start/end timestamps, duration, recurrence text/type, and registration deadline.
- Pricing: listed and discounted INR price, fees, pricing unit, tier, materials, take-home product, and certificate flags.
- Demand and availability: status, seats, public interest count where published, sold-out observation, waitlist and booking flags, and demand notes.
- Data quality: classification, price, date, and status confidence plus missing-field/reviewer notes.

## Validation rules

Validation enforces allowed city/category/taxonomy codes, non-negative prices, discounted price not above list price, age ranges, seat counts, timezone-aware observation timestamps, no unapproved fields, no image URLs or sensitive strings, and no inference that `registration_closed` means `sold_out`.
