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

Robots rules do not by themselves provide permission to reuse content. They must be reviewed alongside terms, privacy policy, copyright language, API documentation, and any source-specific restrictions.

## Operational restriction versus governance decision

- `automation_permission_status` records the current operational restriction observed during review. It answers: what is the system allowed or not allowed to do right now?
- `collection_decision` records the final source-governance decision for the intended use. It answers: has this source been approved, rejected, or left pending for the project collection scope?

These fields can differ during review. For example, a source may have `automation_permission_status = Automated collection prohibited or unsuitable` while `collection_decision = pending_review` until a human review decides whether to reject it, seek written permission, or allow only manual observation.

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

## Day 3 source-review fields

The source register includes these governance fields:

- `permitted_use_scope`
- `permitted_fields`
- `prohibited_fields`
- `re_review_date`
- `written_permission_required`
- `data_retention_limit`
- `attribution_required`

Use `written_permission_required=yes` when terms suggest reuse, automated access, commercial use, redistribution, or storage may need explicit authorization.

Source terms can change. Reviewed sources need `re_review_date` and must be revisited before collection begins or after meaningful source changes.

## Registration status rule

Keep `registration_closed` separate from `sold_out`. Do not infer that a closed registration means the event sold out.

## Day 4 limited manual collection rule

A concrete first-party source may receive `collection_decision = approved_manual_collection` only for manually transcribed factual public fields when the review record documents public access, evidence URLs, reviewer, review timestamp, permitted fields, prohibited fields, and the absence of an explicit prohibition on the planned manual use. This is an internal project-governance decision for internal research only; it does not imply that the source owner granted a license, approved reuse, or endorsed the project. It does not approve crawling, scraping, bulk extraction, copying long descriptions, storing images, reusing review text, collecting personal data, or storing protected creative content.

For manual-approved Day 4 sources, `automation_permission_status` remains `Automated collection prohibited or unsuitable`. In other words, the operational restriction blocks automation while the governance decision allows only narrow manual transcription.

Dedicated terms or privacy pages are not always visible during first review. When absent, the official public source page reviewed for policy links is recorded and the source must be re-reviewed before expanding beyond the Day 5 manual pilot.
