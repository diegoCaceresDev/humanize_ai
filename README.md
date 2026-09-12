# Humanize AI

> An evidence-first UX reviewer for the page currently open in Chrome.

**Current release:** [`v0.1.0`](docs/RELEASE_NOTES_v0.1.0.md) · **Status:** ready for a teammate to install and test locally.

Humanize gives a developer, founder, or designer a grounded second opinion on a live page. One click captures bounded page evidence and the visible viewport, sends it to the API, and returns a branded report with a Humanity Score, findings, and practical next steps. It is not an AI-authorship detector.

## What is included

- Chrome Manifest V3 extension built with WXT, React, and TypeScript.
- One-button active-tab capture for normal HTTP(S) pages.
- FastAPI audit service with structured model output and branded report data.
- OpenRouter model integration; the key remains on the server.
- Optional Exa research grounding.
- Neon Postgres persistence with Alembic migrations.
- Render Blueprint for deployment.
- A local demo page for an end-to-end test.

## Architecture

`Active Chrome tab → extension popup → FastAPI → optional Exa context → OpenRouter → Neon Postgres → result in popup`

The extension sends the visible screenshot, bounded text/structure, and image metadata. It does not upload original image binaries in this release.

## Quick start for teammates

The complete clone-to-test instructions are in [docs/TEAM_SETUP.md](docs/TEAM_SETUP.md). In short:

```bash
git clone https://github.com/diegoCaceresDev/humanize_ai.git
cd humanize_ai
npm ci
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt
cp .env.example .env
# Add provider keys and Neon URLs to .env; see docs/TEAM_SETUP.md.
npm run migrate:api
npm run package:extension
```

In separate terminals, run `npm run dev:api` and `npm run dev:demo`, load `apps/extension/.output/chrome-mv3` at `chrome://extensions`, and audit `http://localhost:4173`.

For a provider-free UI smoke test, set `DEMO_MODE=true` in `.env`. That keeps the extension-to-API flow while returning a deterministic sample report.

## Configuration

Copy [.env.example](/Users/jpino/Development/humanize/.env.example) to `.env`; never commit the completed file. The API loads a root `.env` first, then `apps/api/.env`.

| Purpose | Required for live audit | Accepted variables |
| --- | --- | --- |
| Model access | Yes | `OPENROUTER_API_KEY` or `OPEN_ROUTER` |
| Database runtime | Yes for persistence | `DATABASE_URL`, `NEON_DATABASE_URL`, or `NEON_URL` |
| Migrations | Yes for migrations | `DATABASE_URL_UNPOOLED` or `NEON_DATABASE_URL_UNPOOLED` |
| Web grounding | Optional | `EXA_API_KEY` or `EXA_AI`, plus `EXA_ENABLED=true` |
| Extension API URL | Local default works | `apps/extension/.env` → `VITE_API_BASE_URL` |

Use Neon’s pooled connection string for `DATABASE_URL` and its direct/unpooled connection string for `DATABASE_URL_UNPOOLED`. Team members with access to the linked Neon project can pull only those variables with:

```bash
npx neon@latest env pull --file .env --env DATABASE_URL --env DATABASE_URL_UNPOOLED
```

## Local commands

| Command | Purpose |
| --- | --- |
| `npm run dev:api` | Start FastAPI on port 8000 (activate `.venv` first). |
| `npm run dev:demo` | Serve the sample page on port 4173. |
| `npm run migrate:api` | Apply Alembic migrations (activate `.venv` first). |
| `npm run verify` | Type-check and build the extension. |
| `npm run test:api` | Run API tests (activate `.venv` first). |
| `npm run package:extension` | Create the loadable build and release ZIP. |

## Installing the extension

1. Run `npm run package:extension`.
2. Visit `chrome://extensions`.
3. Enable **Developer mode**.
4. Choose **Load unpacked** and select `apps/extension/.output/chrome-mv3`.
5. Pin **Humanize AI**, visit a normal `http://` or `https://` page, and click **Humanize this page**.

Chrome does not load an extension ZIP directly in developer mode; unpack the ZIP or use the generated `chrome-mv3` directory. See [the final test workflow](docs/FINAL_TEST.md) for expected results and troubleshooting.

## Deployment

[render.yaml](/Users/jpino/Development/humanize/render.yaml) defines the FastAPI service. Configure the provider secrets and both Neon URLs in Render; startup runs `alembic upgrade head` before Uvicorn. `/healthz` checks process health and `/readyz` checks database connectivity.

Set `VITE_API_BASE_URL` to the deployed Render URL before packaging a production extension. Restrict `ALLOWED_ORIGINS` to the final Chrome extension origin once known.

## Documentation

- [Team setup and test guide](docs/TEAM_SETUP.md)
- [Final user workflow](docs/FINAL_TEST.md)
- [Release notes for v0.1.0](docs/RELEASE_NOTES_v0.1.0.md)
- [Cloud test deployment guide](docs/CLOUD_TEST_DEPLOYMENT.md)
- [Changelog](CHANGELOG.md)
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md)
- [Team ownership and acceptance criteria](docs/TEAM_PLAN.md)
- [Design system](docs/HUMANIZE_DESIGN_SYSTEM.md)

## Privacy and scope

- An audit is explicitly triggered by the reviewer.
- The OpenRouter key is server-only and never included in the extension.
- Page content is untrusted input, not instructions.
- The report is advisory; the reviewer chooses whether to make any change.
