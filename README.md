# Humanize

> An evidence-first UX review agent for the page currently open in Chrome.

Humanize helps developers, founders, and designers turn vague feedback into grounded, actionable UX improvements. From the extension popup, a reviewer deliberately audits the active page. Humanize captures bounded page evidence and the visible viewport, sends that evidence to the API, and returns a branded report with a Humanity Score, findings, and practical next steps.

Humanize is **not** an AI-authorship detector. It reviews the human quality of a live interface.

## What works today

- Chrome Manifest V3 extension built with WXT, React, and TypeScript.
- One-click audit of a normal HTTP(S) page from the extension popup.
- Active-tab capture: visible JPEG screenshot plus bounded text, structure, CTA, form, link, and image metadata.
- FastAPI service that produces structured report data.
- OpenRouter model integration; the provider key remains server-side.
- Optional Exa research grounding.
- Neon Postgres persistence with Alembic migrations.
- Local demo site, GitHub Actions workflow, and Render deployment blueprint.
- Signal Violet interface with a Humanity Score, findings, evidence, recommendations, and quick wins.

> **Current MVP boundary:** Humanize is a review-and-report tool. It does not yet alter the audited page, offer a CSS preview/revert flow, or export a PDF. Do not promise those features in the demo or submission until they are implemented.

## Architecture

```
Active Chrome tab
  → Humanize extension popup
  → FastAPI audit service
  → optional Exa context + OpenRouter model
  → Neon Postgres
  → structured report in the popup
```

The extension transmits the **visible screenshot** and the bounded page evidence required for the audit to the configured API. It does not upload original image binaries.

## Quick start (Windows PowerShell)

Requirements: Node.js 22 or later, Python 3.12 or later, and Chrome.

```powershell
# From the repository root
npm ci
Copy-Item .env.example .env
Copy-Item apps/extension/.env.example apps/extension/.env

# API environment
cd apps/api
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ../..
```

For a provider-free end-to-end UI smoke test, set `DEMO_MODE=true` in the root `.env`. For a live model audit, configure `OPENROUTER_API_KEY`; Exa is optional. Configure the database variables when using persistence and migrations.

Start the services in separate terminals:

```powershell
# Terminal 1 — from the repository root, with the API virtual environment activated
npm run dev:api

# Terminal 2 — repository root
npm run dev:demo
```

Build and load the extension:

```powershell
# Repository root
npm run build:extension
```

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Choose **Load unpacked** and select `apps/extension/.output/chrome-mv3`.
4. Open `http://localhost:4173`, pin Humanize, and choose **Humanize this page**.

To create the release ZIP, run `npm run package:extension`. Chrome Developer Mode loads the unpacked `chrome-mv3` folder, not the ZIP.

## Configuration

Copy the templates; never commit populated `.env` files.

| Purpose | Variables |
| --- | --- |
| Demo mode | `DEMO_MODE=true` |
| Live model audit | `OPENROUTER_API_KEY`, optional `OPENROUTER_MODEL` |
| Optional web grounding | `EXA_API_KEY`, `EXA_ENABLED=true` |
| Database | `DATABASE_URL`, `NEON_DATABASE_URL`, or `NEON_URL` |
| Extension API URL | `apps/extension/.env` → `VITE_API_BASE_URL` |

The extension defaults to `http://localhost:8000`. For a deployed API, set `VITE_API_BASE_URL` before building the extension.

## Verification

Run these from the repository root after installing dependencies. Activate the API virtual environment before the API test command.

```powershell
npm run verify
npm run test:api
npm run build:extension
```

The source tree includes tests and CI configuration. A local passing run and a Chrome audit against the demo page are still required before recording the final demo.

## Privacy and scope

- Audits only run after an explicit reviewer action.
- The OpenRouter key is server-side and is never bundled into the extension.
- The screenshot and bounded page evidence leave the browser for the configured API; do not audit private, confidential, or sensitive pages during the demo.
- Captured content is untrusted evidence, never instructions for the agent.
- The report is advisory: the reviewer decides what to change.

## Project structure

```
apps/
  extension/  # WXT + React Chrome extension
  api/        # FastAPI audit service, integrations, migrations, tests
  demo/       # local page used for the end-to-end demo
docs/         # team plan, design system, test and release notes
render.yaml   # Render deployment blueprint
```

## Hackathon declaration

**Built during the hackathon:** the Humanize UX-review concept, WXT extension, active-tab evidence capture, FastAPI audit pipeline, OpenRouter/Exa/Neon integrations, review experience, demo page, tests, documentation, and Signal Violet design system.

**Inherited or third-party:** the event rules and reference material, open-source frameworks and packages (WXT, React, FastAPI, SQLAlchemy, Alembic), Chrome APIs, and the external OpenRouter, Exa, Neon, and Render services. The current application runtime is not a CopilotKit/Next.js starter implementation.

## Documentation

- [Team setup and test guide](docs/TEAM_SETUP.md)
- [Final user workflow](docs/FINAL_TEST.md)
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md)
- [Team ownership and acceptance criteria](docs/TEAM_PLAN.md)
- [Humanize design system](docs/HUMANIZE_DESIGN_SYSTEM.md)
- [Release notes](docs/RELEASE_NOTES_v0.1.0.md)
- [Cloud test deployment](docs/CLOUD_TEST_DEPLOYMENT.md)
- [Changelog](CHANGELOG.md)
