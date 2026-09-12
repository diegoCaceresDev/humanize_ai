# Cloud test deployment

This guide deploys the Humanize API for a real, team-only cloud test. It is not a substitute for end-user authentication, billing controls, or a public launch review.

## Current account prerequisite

The configured Render account can authenticate with the Render API, but Blueprint validation currently returns `need_payment_info`. Add billing information in Render before creating the service. No Render service exists yet.

## 1. Create the Render service

Create the Blueprint from `render.yaml` on the `landing` branch. Render must receive these secret values through its dashboard or API; do not put them in Git:

```dotenv
DATABASE_URL=<Neon pooled URL>
DATABASE_URL_UNPOOLED=<Neon direct URL>
OPENROUTER_API_KEY=<OpenRouter key>
EXA_API_KEY=<Exa key>
ALLOWED_ORIGINS=chrome-extension://<extension-id>
```

The checked-in service configuration sets `APP_ENV=production`, `DEMO_MODE=false`, and disables broad Chrome-extension CORS. The pooled Neon URL is used by FastAPI; the direct URL is used by Alembic during service startup.

## 2. Establish the extension origin

1. Build the extension once with its local configuration and load `apps/extension/.output/chrome-mv3` in Chrome.
2. Copy its ID from `chrome://extensions`.
3. Set Render’s `ALLOWED_ORIGINS` to `chrome-extension://<extension-id>` and deploy.

For a short-lived first smoke test only, `ALLOW_ANY_CHROME_EXTENSION_ORIGIN=true` can be set temporarily. Set it back to `false` and deploy again as soon as the team’s extension ID is known.

## 3. Verify the cloud API

After Render provides an HTTPS URL, verify:

```bash
curl https://<your-render-service>.onrender.com/healthz
curl https://<your-render-service>.onrender.com/readyz
```

Both must succeed before packaging the cloud extension. A live audit must then create a persisted Neon record and return a structured report.

## 4. Package the cloud extension

Do not put any provider or database secret in the extension. Create `apps/extension/.env.production` from `apps/extension/.env.cloud.example`, set only the Render HTTPS URL, then run:

```bash
npm run package:extension
```

Reload or load the resulting `apps/extension/.output/chrome-mv3` directory. The popup now calls the cloud API instead of `localhost`.

## Production boundary

This service is safe for controlled team testing once CORS is restricted to the team extension ID. It is not ready for unrestricted public use: the audit endpoint still needs real user authentication, usage quotas/rate limiting, abuse monitoring, and a retention/deletion policy before a public release.
