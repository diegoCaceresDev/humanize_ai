# Changelog

All notable changes to Humanize AI are documented here.

## [Unreleased]

## [0.2.2] - 2026-09-12

### Added

- A production-quality project README with verified cloud-audit screenshots and descriptions of the score, findings, actions, Exa context, and browser evidence experience.
- A controlled team-cloud configuration template pointing to the deployed Render API.
- A complete `v0.2.2` test, setup, cloud, and release-documentation handoff.

### Fixed

- Captured page metadata is bounded to the API contract before submission, preventing unusually long public-page fields from failing validation.
- Structured FastAPI validation responses now render as useful popup messages instead of `[object Object]`.

## [0.2.1] - 2026-09-12

### Fixed

- Published the Chrome extension validation and readable-error fix as a standalone patch release.

### Added

- Heading-bound evidence and a rendered heading-structure signal in the Flight Recorder.
- Exact inspected CTA labels/count in the popup and an in-page “Preview only” marker.
- A submission-ready project checklist with demo, attribution, safety, and release guidance.
- Versioned browser evidence, CTA score components, stable fingerprints, ambiguity diagnostics, and pre-preview fingerprint validation.
- Sanitized optional model evidence references that cannot introduce an unmeasured preview target.

## [0.2.0] - 2026-09-12

### Added

- Browser-native UX Flight Recorder evidence for visible CTA candidates, first-viewport CTA count, missing image alt text, and unlabeled form fields.
- Element-level CTA inspection in the active tab.
- A reviewer-approved Focus Preview that emphasizes the measured primary action and temporarily softens competing actions.
- Before/preview primary-action prominence comparison and an explicit zero-site-mutations indicator.
- A bounded browser-evidence API contract that excludes extension-only element locators.

### Safety

- Preview state is limited to Humanize-owned CSS and `data-humanize-*` attributes.
- Revert, result reset, and page refresh remove preview state; no site content, behavior, or persisted styles are changed.
- Browser metrics are labeled as structural/visual proxies and never as proof of conversion, usability, or accessibility compliance.

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
