# Humanize

> A browser-native UX review agent that turns vague feedback into grounded, reversible improvements.

Built for **AI Tinkerers - Agents, Everywhere: Bots, Channels & More**.

## Why Humanize

Teams ship pages quickly, often from templates or AI-assisted generation. That can leave pages with an unclear value proposition, competing calls to action, flat hierarchy, vague copy, or overlooked accessibility basics.

Humanize does not determine whether a page was made with AI. It identifies observable, page-specific UX evidence and proposes improvements a reviewer can inspect and control.

## Demo workflow

1. Open a landing page in Chrome.
2. Open the Humanize side panel and choose **Audit this page**.
3. The extension collects the active tab's visible screenshot plus bounded DOM evidence: headings, CTAs, copy, accessibility signals, and structural metrics.
4. A local audit service sends that evidence to a multimodal model with a constrained system prompt.
5. Humanize returns a Humanity Score, evidence-based findings, and practical quick wins.
6. Apply a reversible focus preview, revert it, or save the report as a PDF.

The browser context is essential: the agent reviews the actual page state rather than relying on a pasted screenshot or generic conversation.

## Architecture

Active Chrome tab -> one-button popup -> programmatic capture with the `activeTab` permission -> FastAPI -> optional Exa context -> OpenRouter multimodal model -> branded result view. The API stores the audit result in Neon Postgres when a database URL is configured.

## Project layout

- `apps/extension/`: Chrome Manifest V3 extension built with WXT, React, and TypeScript.
- `apps/api/`: FastAPI service, OpenRouter/Exa providers, and SQLAlchemy persistence.
- `render.yaml`: Render Blueprint for the API service.
- `docs/TEAM_PLAN.md`: roles, delivery plan, demo script, and acceptance criteria.

## Setup

**Prerequisites:** Node.js 22+, Python 3.12+, Google Chrome, an OpenRouter API key, and a multimodal model available through OpenRouter. Exa and Neon are optional for local development.

Start the API:

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENROUTER_API_KEY. Add DATABASE_URL and EXA_API_KEY when available.
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

For a no-credentials smoke test, set `DEMO_MODE=true` in `apps/api/.env`. This returns a deterministic sample report while preserving the real extension-to-API flow. A deliberately generic test landing page is included in `apps/demo`; serve it with `npm run dev:demo` and open `http://localhost:4173` in Chrome.

There is also a root [.env.example](/Users/jpino/Development/humanize/.env.example) if you prefer keeping one shared local configuration file. The API accepts both the canonical provider variable names and the existing `OPEN_ROUTER`, `EXA_AI`, and Neon aliases.

If the repository is linked to a Neon project, pull its managed connection variables without overwriting the provider settings:

```bash
npx neon@latest env pull --file .env --env DATABASE_URL --env DATABASE_URL_UNPOOLED
```

The application uses the pooled `DATABASE_URL` for normal requests and reserves `DATABASE_URL_UNPOOLED` for future schema migrations.

Build the extension:

```bash
npm install
cp apps/extension/.env.example apps/extension/.env
npm run build:extension
npm run package:extension
```

In Chrome, open `chrome://extensions`, enable **Developer mode**, select **Load unpacked**, and choose the generated `apps/extension/.output/chrome-mv3` directory. Click the Humanize AI toolbar icon, then **Humanize this page**.

`npm run package:extension` also creates a versioned ZIP in `apps/extension/.output/`; use the unpacked `chrome-mv3` folder during development.

The extension captures the visible viewport as a screenshot and sends bounded text/structure plus image metadata. It does not upload original image binaries in this first version.

### Deploying the API on Render

The root `render.yaml` defines a native Python web service rooted at `apps/api`. Create a Blueprint from the repository, add the secret values in Render, and set `ALLOWED_ORIGINS` to the extension origin after the first unpacked build if you want strict origin allowlisting. Set both Neon connection strings: `DATABASE_URL` is the pooled runtime URL and `DATABASE_URL_UNPOOLED` runs Alembic migrations before startup. Render provides the `PORT` variable; `/healthz` checks process health and `/readyz` verifies database readiness.

### Provider roles

- **OpenRouter** is the server-side model gateway. The extension never sees this key.
- **Exa** is optional web grounding: the API requests fast search results with highlights, then supplies their titles and URLs as optional context to the reviewer.
- **Neon** supplies hosted Postgres through `DATABASE_URL`, `NEON_DATABASE_URL`, or `NEON_URL` (a standard `postgresql://` URL is accepted). The API creates the initial `audit_records` table on startup for the MVP.
- **Render** hosts the FastAPI web service using the included Blueprint.

## Safety and privacy

- The extension never receives or stores the OpenRouter key; the API owns it.
- An audit is explicitly initiated by the reviewer and uses only the active tab's visible screenshot plus bounded DOM evidence.
- Page text and HTML are treated as untrusted data, not instructions.
- Humanize does not claim to be an AI-authorship detector.

## Verification

Run `npm run verify` and `npm run test:api`.

## Inherited vs. hackathon work

**Inherited:** the Agents, Everywhere starter kit, its monorepo structure, model configuration pattern, and verification tooling.

**Built during the hackathon:** Humanize's product concept, Chrome extension, screenshot and DOM evidence pipeline, constrained UX-review prompt, FastAPI audit endpoint, branded popup report, Neon persistence, and project documentation.

## Team

See [the team plan](docs/TEAM_PLAN.md) for ownership, acceptance criteria, risks, and the two-minute demo sequence.
