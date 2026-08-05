# Day 5 Batch 01 Collection Notes

Observation date: 2026-08-05
Researcher: Codex

## Scope

Batch 01 contains 12 real, non-synthetic manual records transcribed from approved first-party sources. No scraping, API calls, terminal network tools, browser automation, booking forms, images, customer details, testimonials, cookies, or credentials were used or stored.

## Sources reviewed

- Baking Hub Academy: 2 records.
- Mud Effects Pottery Studio: 2 records.
- Kalasaara Art Studio: 1 record.
- Specialty Coffee Academy of India: 2 records, one Bengaluru product and one Hyderabad chapter product.
- T-Works: 2 records.
- Crust & Crumble Bakers: 1 record.
- Mystic Palette: 2 records.

## Pages unavailable or limited

- Crust & Crumble's workshop booking subdomain did not provide a separately usable manual page in this pass, so only the official main-site Kids Baking Workshops product was recorded.
- SCAI's Hyderabad chapter was visible in the SCAI workshops collection view; no separate product-detail URL was confirmed in this pass.
- Kalasaara exposed product/class names but not prices or exact dated occurrences.

## Record counts by source

- baking_hub: 2
- mud_effects: 2
- kalasaara: 1
- scai: 2
- tworks: 2
- crust_and_crumble: 1
- mystic_palette: 2

## Historical versus current records

- Historical/completed: Baking Hub Brownies and Blondies Masterclass; Baking Hub June 2026 certification course product.
- Current/in-progress: SCAI Crop to Cup Workshop - Bengaluru Chapter spans 3-7 Aug 2026.
- Scheduled/future: Mud Effects September 2026 Ganesha idol workshop product.
- Undated recurring or product listings: Mud Effects weekend wheel pottery, Kalasaara Acrylic Painting, T-Works ceramic products, Crust & Crumble Kids Baking Workshops, Mystic Palette products, and SCAI Hyderabad chapter.

## Ambiguous values

- T-Works Wheel Throwing Level 01 showed a price-like value that was intentionally left blank because it appeared malformed or unclear.
- Several sources listed products without exact occurrence dates; those records use recurrence text and blank event timestamps.
- SCAI Bengaluru was in-progress as of 2026-08-05; the taxonomy has no explicit ongoing status, so source availability was retained and the quality report separately classifies the temporal bucket.

## Fields intentionally left blank

- Prices were left blank where not published or unclear.
- Seat totals, seats available, interested counts, registration deadlines, tax treatment, and certificate flags were left blank unless explicitly visible.
- Age ranges were left blank where not published.
- Event timestamps were left blank for recurring products or product listings without specific dates.

## Source-page inconsistencies

- Crust & Crumble includes workshop promotion on the main bakery page but exposes limited structured workshop details there.
- SCAI has city coverage in the site footer and city-specific product names, but not every product detail page establishes all city offerings equally.
- Mud Effects includes a dated September 2026 workshop with multiple selectable dates; it was recorded as one product, not duplicated per date.

## Quality-gate result

The initial 12-record batch passed local schema, governance, duplicate, and privacy validation. All records are `self_checked`; none are independently verified because the same researcher entered and checked them. Controlled expansion was not performed because the initial high-quality batch already met the requested initial range and quality took priority over count.
