# Final user test

Humanize `v0.1.0` is ready for a full local Chrome workflow using Neon, OpenRouter, and optional Exa credentials. For a fresh clone, complete [team setup](TEAM_SETUP.md) first.

## 1. Start the API

From the repository root:

```bash
source .venv/bin/activate
npm run migrate:api
npm run dev:api
```

Confirm the API and database are ready in another terminal:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

Expected responses:

```json
{"status":"ok"}
{"status":"ready","database":"connected"}
```

## 2. Start a page to audit

From the repository root:

```bash
npm run dev:demo
```

Open `http://localhost:4173` in Chrome. The sample page is intentionally generic so Humanize has concrete opportunities to identify.

## 3. Build and install the extension

From the repository root:

```bash
npm ci
npm run package:extension
```

In Chrome:

1. Go to `chrome://extensions`.
2. Turn on **Developer mode**.
3. Select **Load unpacked**.
4. Choose `apps/extension/.output/chrome-mv3`.
5. Pin **Humanize AI** to the toolbar if Chrome does not show it immediately.

The generated ZIP at `apps/extension/.output/extension-0.1.0-chrome.zip` is useful for sharing the build, but **Load unpacked** is the developer-install path for this MVP.

## 4. Run the audit

1. Return to the demo page.
2. Open the Humanize AI toolbar popup.
3. Click **Humanize this page** once.
4. Wait for the report to render.

The report should include a Humanity Score, a summary, evidence-backed findings, quick wins, and Exa research links when available.

## 5. Verify persistence

Every successful audit returns an `id`. Confirm that it was persisted:

```bash
curl http://localhost:8000/api/audits/<audit-id>
```

The returned record should match the report shown in the extension.

## Troubleshooting

- **`/readyz` returns 503:** confirm your Neon URLs are in the root `.env`, run `npm run migrate:api`, then restart the API. Team members with Neon access can run `npx neon@latest env pull --file .env --env DATABASE_URL --env DATABASE_URL_UNPOOLED`.
- **Popup cannot reach the API:** confirm it is running on `http://localhost:8000`; the extension default uses this URL.
- **OpenRouter error:** verify `OPEN_ROUTER` or `OPENROUTER_API_KEY` is present in `.env` and restart the API.
- **No Exa sources:** verify `EXA_AI` or `EXA_API_KEY` and `EXA_ENABLED=true` are present in `.env`; an Exa outage does not block the core audit.
- **Chrome refuses the page:** use a normal `http://` or `https://` webpage. Chrome internal pages cannot be audited.
