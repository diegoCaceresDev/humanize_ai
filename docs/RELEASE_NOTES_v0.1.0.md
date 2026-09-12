# Humanize AI v0.1.0

Release date: 2026-09-12

This is the first testable release of Humanize AI. It provides the complete local path from a Chrome tab to an evidence-based UX report, with optional web grounding and persistent audit records.

## Included

- Branded Humanize AI Chrome extension and icon.
- One-button capture of the current HTTP(S) tab’s visible viewport and bounded page structure.
- FastAPI API with health, readiness, create-audit, and retrieve-audit endpoints.
- OpenRouter-powered structured UX review.
- Optional Exa sources attached as report context.
- Neon Postgres storage and the initial `audit_records` migration.
- Render deployment Blueprint.
- A branded local demo page and complete teammate test workflow.

## Install

Follow [the team setup guide](TEAM_SETUP.md). For Chrome developer installation, use `apps/extension/.output/chrome-mv3` after running `npm run package:extension`.

## Validation performed

- Extension type-check and production build.
- Extension ZIP packaging.
- API unit and provider-contract tests.
- Neon migration and API readiness check.
- Live FastAPI → Exa → OpenRouter → Neon audit and persisted-record retrieval.

## Known scope boundaries

- The extension handles normal HTTP(S) tabs only.
- It captures metadata and a screenshot, not original page image binaries.
- The product returns review recommendations; it never changes the audited webpage.
- The distributed ZIP is an archive artifact. Chrome developer testing uses the unpacked build directory.
