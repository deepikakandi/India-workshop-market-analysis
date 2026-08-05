# Source Evaluation Rules

Use these controlled rules when reviewing candidate sources for the Bengaluru and Hyderabad pilot.

## Source register versus discovery backlog

`source_register.csv` must contain only concrete, individually reviewable sources such as a named platform, API, government/industry website, or specific organization website.

Generic source families belong in `source_discovery_backlog.csv` until they produce a concrete source. Examples include organizer websites, public studio calendars, coffee-specific official websites as a broad family, and local coffee schools/roasters/cafes/training studios to discover.

Each discovered organizer, studio calendar, coffee school, roaster, cafe, or training studio must later be added to `source_register.csv` as its own row with a stable `source_id`.

## Reliability rating

- High: first-party organizer, government, industry body, or official API.
- Medium: established ticketing or event platform.
- Low: aggregator, user-generated listing, or unverified social post.

## Historical coverage rating

- Current only
- Less than 6 months
- 6-12 months
- 1-3 years
- More than 3 years
- Unknown

## Duplicate risk

- Low
- Medium
- High

## Pilot priority

- Essential
- Supporting
- Optional
- Excluded

## Access status

- Official API permitted
- Public export permitted
- Manual collection permitted
- Public-page collection pending review
- Automated collection prohibited or unsuitable
- Unknown; legal/terms review required

Never mark scraping or automated collection as approved without recorded evidence from a terms, robots, API, or access review.

## Collection decision

Use these controlled values in `collection_decision`:

- `approved_official_api`
- `approved_manual_collection`
- `approved_limited_public_collection`
- `pending_review`
- `rejected`
- `not_technically_feasible`

All Day 2 candidate sources remain `pending_review`.

An approved source must include review evidence:

- `terms_url` or `api_documentation_url` when applicable
- `review_evidence_url`
- `reviewed_by`
- `reviewed_at`
- `collection_decision_reason`

Do not mark any source approved only because it is public or easy to access.

## Registration status rule

Keep `registration_closed` separate from `sold_out`. Do not infer that a closed registration means the event sold out.
