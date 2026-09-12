# Controlled cloud deployment and team test

Humanize v0.2.2 has a live FastAPI service on Render for controlled team testing:

| Service | Value |
| --- | --- |
| API base URL | `https://humanize-api-t9g3.onrender.com` |
| Runtime | FastAPI on Render |
| Database | Neon Postgres |
| AI provider | OpenRouter, server-side only |
| Research provider | Exa, server-side only when enabled |

This is a real cloud workflow: the extension sends a reviewer-approved capture to Render, FastAPI persists a completed audit in Neon, OpenRouter produces the structured review, and Exa can attach public research sources. It is suitable for controlled team tests, not an unrestricted public launch.

## Verify the deployment

Run these checks before a team test:

```bash
curl https://humanize-api-t9g3.onrender.com/healthz
curl https://humanize-api-t9g3.onrender.com/readyz
```

Expected responses:

```json
{"status":"ok"}
{"status":"ready","database":"connected"}
```

## Build a cloud-test extension

No provider key, database URL, or Render credential belongs in the extension.

```bash
cp apps/extension/.env.cloud.example apps/extension/.env.production
npm ci
npm run package:extension
```

`apps/extension/.env.production` contains only `VITE_API_BASE_URL`, pointing to the public Render URL. Chrome loads the unpacked build, not the ZIP:

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Choose **Load unpacked**.
4. Select `apps/extension/.output/chrome-mv3`.
5. Pin **Humanize AI**, visit an ordinary HTTP(S) page, and select **Humanize this page**.

After a source or environment change, run `npm run package:extension` again and click the extension card’s **Reload** button. Confirm the extension’s displayed version is `0.2.2`.

## Render configuration

The checked-in [render.yaml](../render.yaml) runs migrations before Uvicorn starts and sets production-safe defaults:

```text
APP_ENV=production
DEMO_MODE=false
```

Set these values in Render as secrets; do not commit them:

```dotenv
DATABASE_URL=<Neon pooled connection URL>
DATABASE_URL_UNPOOLED=<Neon direct connection URL>
OPENROUTER_API_KEY=<OpenRouter server key>
EXA_API_KEY=<Exa server key, optional>
ALLOWED_ORIGINS=chrome-extension://<known-extension-id>
```

Use the pooled Neon URL for application traffic and the direct/unpooled URL for Alembic startup migrations. The API normalizes quoted and encoded connection URLs, but pasted values should still be copied exactly from Neon.

## CORS and launch boundary

For a first controlled smoke test, a temporary broad Chrome-extension CORS policy may be necessary while the team confirms its extension identity. Before exposing the service beyond the team, set the exact `ALLOWED_ORIGINS` value for the known extension ID, set `ALLOW_ANY_CHROME_EXTENSION_ORIGIN=false`, and redeploy.

The API is intentionally not yet a public product endpoint. A public launch additionally needs authentication, user authorization, rate limits, abuse monitoring, audit-data retention/deletion controls, and a finalized privacy policy.

## Team-test checklist

- [ ] Health and readiness checks pass.
- [ ] Extension package contains the Render URL and no provider/database secret.
- [ ] A public test page returns a score, findings, quick wins, and browser evidence.
- [ ] A successful audit is retrievable from `GET /api/audits/<id>`.
- [ ] The team has tested Focus Preview and confirmed **Revert preview** and a browser refresh remove all Humanize styling.
- [ ] CORS is narrowed to approved extension IDs before expanding access.
