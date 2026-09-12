# Team setup and local test guide

This guide takes a teammate from a fresh clone to a complete local Humanize workflow. It is written for release `v0.2.0`.

## Prerequisites

- Node.js 22 or newer and npm.
- Python 3.12 or newer.
- Google Chrome.
- Access to the shared secrets manager for the OpenRouter key and, if used, the Exa key.
- Access to the Humanize Neon project for database URLs, or `DEMO_MODE=true` for a provider-free smoke test.

Do not send `.env` files in chat or commit them. Request access through the team’s approved secret-sharing process.

## 1. Clone and install dependencies

```bash
git clone https://github.com/diegoCaceresDev/humanize_ai.git
cd humanize_ai
git checkout v0.2.0
npm ci
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt
```

Keep the virtual environment activated whenever using `npm run dev:api`, `npm run migrate:api`, or `npm run test:api`.

## 2. Configure your local environment

```bash
cp .env.example .env
cp apps/extension/.env.example apps/extension/.env
```

For a live audit, add these values to the root `.env`:

```dotenv
DEMO_MODE=false
OPENROUTER_API_KEY=<team-provided-key>
DATABASE_URL=<Neon-pooled-url>
DATABASE_URL_UNPOOLED=<Neon-direct-url>
EXA_ENABLED=true
EXA_API_KEY=<team-provided-key>
```

`EXA_ENABLED` and `EXA_API_KEY` are optional. The API also accepts the existing aliases `OPEN_ROUTER` and `EXA_AI`.

If you have Neon project access, you may pull only the database variables into the root `.env`:

```bash
npx neon@latest env pull --file .env --env DATABASE_URL --env DATABASE_URL_UNPOOLED
```

Use the pooled URL for `DATABASE_URL`; use the direct/unpooled URL for `DATABASE_URL_UNPOOLED`. This split prevents schema migration traffic from using a transaction pooler.

For a no-credential smoke test, use `DEMO_MODE=true` and omit provider/database variables. The extension and FastAPI report UI still work, but no live model call or persisted record is created.

## 3. Prepare the database and extension

```bash
npm run migrate:api
npm run verify
npm run package:extension
```

The package command creates:

- `apps/extension/.output/chrome-mv3/` — choose this directory in Chrome’s **Load unpacked** flow.
- `apps/extension/.output/extension-0.2.0-chrome.zip` — the versioned release artifact for archive or distribution.

## 4. Run the local services

Open two terminals from the repository root. Activate `.venv` in the API terminal.

```bash
# Terminal 1
source .venv/bin/activate
npm run dev:api
```

```bash
# Terminal 2
npm run dev:demo
```

Confirm the API and, for a live configuration, database are ready:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

Expected live responses are `{"status":"ok"}` and `{"status":"ready","database":"connected"}`.

## 5. Install and test in Chrome

1. Open `chrome://extensions`.
2. Turn on **Developer mode**.
3. Select **Load unpacked** and choose `apps/extension/.output/chrome-mv3`.
4. Pin **Humanize AI**.
5. Visit `http://localhost:4173`.
6. Open the Humanize AI toolbar popup and select **Humanize this page**.
7. Wait for the report: it should show a score, summary, evidence-backed findings, quick wins, and browser-measured evidence. Live runs may also show Exa sources.
8. Use **Inspect on page**, then **Apply focus preview**. Confirm **Revert preview** restores the untouched page state.

For live runs, copy the returned audit `id` and confirm persistence:

```bash
curl http://localhost:8000/api/audits/<audit-id>
```

## Troubleshooting

- **The popup cannot connect:** confirm `npm run dev:api` is still running and `apps/extension/.env` has `VITE_API_BASE_URL=http://localhost:8000`; rebuild and reload the extension after changing it.
- **`/readyz` reports a failure:** verify both Neon URLs, run `npm run migrate:api`, and restart FastAPI.
- **OpenRouter fails:** verify the key in the root `.env`, then restart FastAPI. The key must not be put in `apps/extension/.env`.
- **No Exa sources:** set `EXA_ENABLED=true` and provide `EXA_API_KEY`; a missing or unavailable Exa integration does not stop the core audit.
- **Chrome rejects the page:** the extension can audit only regular HTTP(S) pages, not browser internal pages such as `chrome://extensions`.
- **The extension shows old code:** rebuild with `npm run package:extension`, then click Reload on the extension card in `chrome://extensions`.

## Before sharing a change

```bash
source .venv/bin/activate
npm run verify
npm run test:api
npm run package:extension
```

Do not commit `.env`, `.neon`, `.venv`, `node_modules`, or `.output`.
