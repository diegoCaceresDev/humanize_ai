# Humanize AI v0.2.2

Release date: 2026-09-12

## Highlights

v0.2.2 is the polished controlled-cloud handoff for Humanize AI. It packages the verified Chrome extension, production FastAPI route, Neon persistence, OpenRouter report generation, optional Exa research grounding, browser evidence, and Focus Preview into a clear team-ready release.

## Included

- A professional README with four verified end-to-end screenshots from a completed AI Tinkerers audit.
- Version-aligned project, extension, API, package, test, setup, and cloud-deployment documentation.
- A cloud-test extension template configured only with the public Render API URL.
- Bounded page-capture fields that prevent long public-page data from violating the API contract.
- Readable structured-validation errors in the popup instead of raw `[object Object]` output.
- The UX Flight Recorder: CTA, heading, and accessibility evidence, a user-approved temporary Focus Preview, and a clean revert path.

## Validated workflow

The release was validated through the real cloud path:

```text
Chrome extension → Render FastAPI → OpenRouter + Exa → Neon Postgres → popup report
```

The included screenshots show a 75/100 AI Tinkerers audit, severity-tagged findings, quick wins, Exa context, and browser-measured CTA and heading evidence.

## Installation

```bash
git checkout v0.2.2
npm ci
cp apps/extension/.env.cloud.example apps/extension/.env.production
npm run package:extension
```

Then load `apps/extension/.output/chrome-mv3` through Chrome’s **Load unpacked** flow. See [Team setup](TEAM_SETUP.md) and [Cloud deployment](CLOUD_TEST_DEPLOYMENT.md) for the complete instructions.

## Scope and safety

- Audits require an explicit reviewer action and support normal HTTP(S) tabs only.
- Provider and database secrets stay server-side.
- Captured page data is treated as untrusted evidence.
- Focus Preview is reversible and does not save target-site changes.
- The report is advisory; it does not establish conversion, accessibility, or usability outcomes.
