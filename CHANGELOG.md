# Changelog

All notable changes to Humanize AI are documented here.

## [0.1.0] - 2026-09-12

### Added

- A Chrome Manifest V3 extension with one-click active-tab auditing.
- Visible-viewport capture and bounded page evidence collection.
- FastAPI audit endpoints, structured findings, and a branded popup report.
- OpenRouter model integration and optional Exa research grounding.
- Neon Postgres audit persistence with an Alembic migration.
- Render deployment Blueprint, local demo page, API tests, and extension verification.
- Team onboarding, final test, and release documentation.

### Security and privacy

- Provider secrets remain in server-side environment configuration.
- The extension only audits a normal HTTP(S) tab when a reviewer explicitly requests it.
- Page input is treated as untrusted data.
