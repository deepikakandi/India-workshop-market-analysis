# Source Review Checklist

Use this checklist before any source is approved for collection. This is a governance workflow, not legal advice. Source terms can change, so every reviewed source needs a re-review date.

## 1. Source identity

- Source ID
- Source name
- Owner or operator
- Base URL
- Source type
- Reviewer
- Review date

## 2. Public access

- Is authentication required?
- Is a paid account required?
- Are event pages publicly accessible?
- Are listings rendered in HTML, JSON-LD, embedded JSON, API responses, or JavaScript?
- Is a public sitemap, RSS feed, calendar feed, export, or API available?

## 3. Terms and permissions

- Terms URL
- Privacy URL
- Robots URL
- API documentation URL
- Relevant terms text or summarized restriction
- Commercial-use restrictions
- Automated-access restrictions
- Redistribution restrictions
- Storage restrictions
- Attribution requirements
- Rate limits
- Whether written authorization is needed

Robots rules are access instructions for crawlers; they do not by themselves provide permission to reuse content.

## 4. Technical feasibility

- Static HTML
- JavaScript-rendered
- Official API
- Public feed
- Sitemap
- Manual-only
- Login protected
- Anti-bot controls
- CAPTCHA
- Geolocation dependency

## 5. Data usefulness

- Cities covered
- Workshop categories covered
- Fields available
- Price availability
- Date and duration availability
- Age-group availability
- Organizer availability
- Venue availability
- Availability or sold-out status
- Historical depth
- Recurring-event information
- Expected duplicate risk

## 6. Decision

Controlled `collection_decision` values:

- `approved_official_api`
- `approved_manual_collection`
- `approved_limited_public_collection`
- `pending_review`
- `rejected`
- `not_technically_feasible`

Distinguish this from `automation_permission_status`: `automation_permission_status` is the current operational restriction, while `collection_decision` is the final source-governance decision for the intended project use.

Every decision must include:

- Decision reason
- Supporting evidence
- Reviewer
- Review timestamp
- Re-review date
- Permitted fields
- Prohibited fields
- Maximum request frequency where applicable

No automated collection may begin unless the source register row has a reviewed decision, evidence, reviewer, timestamp, permitted scope, and collection limits.
