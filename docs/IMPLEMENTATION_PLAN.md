# Humanize AI Implementation Plan

## 1. Product outcome

Humanize AI is a Chrome Extension that reviews the webpage currently open in the active tab. The first release has one primary action:

> **Humanize this page**

When the user clicks the button, Humanize captures useful page evidence, sends it to the backend, asks a multimodal LLM for a grounded review, and renders the result as a branded HTML report inside the extension.

The first release is intentionally read-only. It does not edit the target website, execute model-generated actions, or claim to detect AI authorship.

## 2. Target architecture

```text
┌──────────────────────────────────────────────────────────────┐
│ Chrome                                                        │
│                                                              │
│  Active tab ── activeTab + scripting ──> Popup               │
│                                           │                  │
│                                           │ HTTPS JSON       │
└───────────────────────────────────────────┼──────────────────┘
                                            ▼
                                  Render Web Service
                                  FastAPI application
                                     │          │
                         OpenRouter ─┘          └─ Exa (optional)
                                     │
                              Neon Postgres
```

### Technology choices

- **Extension:** Manifest V3, WXT, React, TypeScript, CSS.
- **Browser access:** `activeTab`, `scripting`, and `tabs.captureVisibleTab`.
- **Backend:** FastAPI, Pydantic, HTTPX, SQLAlchemy async, asyncpg.
- **Model gateway:** OpenRouter, with a configurable multimodal model.
- **Web grounding:** Exa Search API with bounded highlights, enabled by configuration.
- **Database:** Neon-hosted Postgres.
- **Hosting:** Render Web Service using the repository Blueprint.
- **Verification:** TypeScript typecheck, WXT production build, Pytest, API smoke tests.

## 3. Frontend implementation plan

### 3.1 Extension shell

1. Keep the extension as a WXT MV3 project under `apps/extension`.
2. Set the toolbar action popup as the initial user surface.
3. Keep the popup focused on one primary button and a small number of clear states:
   - Ready to audit.
   - Capturing the page.
   - Sending the audit.
   - Rendering the result.
   - Error with a recoverable explanation.
4. Keep API URLs configurable through `VITE_API_BASE_URL` so local and Render environments use the same client code.
5. Never put OpenRouter, Exa, Neon, or other provider credentials in the extension bundle.

### 3.2 Page capture

On a user-initiated click, the popup should:

1. Query the active tab in the current window.
2. Reject unsupported pages such as `chrome://`, extension pages, and non-HTTP(S) URLs with a useful message.
3. Use `chrome.scripting.executeScript` to collect structured evidence from the active page.
4. Use `chrome.tabs.captureVisibleTab` to capture the current visible viewport as a compressed JPEG.
5. Send one bounded request to the backend.

The structured page evidence should include:

- URL, document title, language, and meta description.
- Visible `h1`–`h3` headings in order.
- Visible buttons, links, submit inputs, and role buttons as CTA candidates.
- Forms and their field names/types.
- Visible image URLs, alt text, and rendered/natural dimensions.
- Bounded visible text from the main content or body.
- A bounded HTML snapshot of the main content or body after removing scripts, styles, templates, and SVG nodes from the cloned snapshot.

### 3.3 Capture constraints

The capture should be useful rather than unbounded. Enforce limits in both client and server code:

- Maximum visible text: approximately 50,000 characters.
- Maximum HTML snapshot: approximately 80,000 characters.
- Maximum images: 100.
- Maximum links: 160.
- Maximum screenshot/request payload: approximately 12 MB.
- Screenshot format: JPEG around 70% quality.

The capture function must never mutate the target page. It should inspect the live DOM and clone before sanitizing the HTML snapshot.

The screenshot contains the visible image pixels. Image metadata is sent separately. Downloading and uploading original image binaries is deferred because it increases privacy, latency, CORS, and payload complexity.

### 3.4 API client and result state

The extension should use a small typed API client with:

- A single `createAudit` request function.
- An explicit request timeout.
- Clear handling for network errors, 4xx validation errors, 413 payload errors, and 502 provider errors.
- No retry of an audit automatically; the user can intentionally start a new audit.

The result state should render:

- Humanity score from 0–100.
- Short score label.
- Summary.
- Findings with severity, page evidence, and recommendations.
- Quick wins.
- Optional research source links returned from Exa.

### 3.5 Branded visual system

Use the current Humanize visual direction as a small design system:

- Warm cream text on a near-black background.
- Amber/gold accent color.
- Editorial typography with strong hierarchy.
- Quiet borders, rounded cards, and restrained motion.
- Product voice: direct, generous, evidence-based, and never judgmental.

Keep the report readable at popup width. If reports outgrow the popup, the next frontend iteration should move the report to a dedicated extension page or Chrome side panel while preserving the same result component.

## 4. Backend implementation plan

### 4.1 FastAPI application

The backend lives under `apps/api` and exposes:

- `GET /healthz` — deployment health check.
- `POST /api/audits` — create a page audit and return the structured result.

The application should:

1. Load configuration from environment variables using Pydantic Settings.
2. Configure CORS for local development and Chrome extension origins.
3. Validate the complete request before any provider call.
4. Enforce a request-size limit before processing the screenshot and page data.
5. Call Exa only when enabled and configured.
6. Call OpenRouter using a server-side API key.
7. Parse and validate the model response with Pydantic.
8. Persist the audit result when Postgres is available.
9. Return stable, user-safe error messages without leaking provider secrets or raw upstream responses.

### 4.2 Request contract

`POST /api/audits`

```json
{
  "context": {
    "url": "https://example.com/",
    "title": "Example page",
    "description": "",
    "language": "en",
    "headings": [
      {"level": "h1", "text": "A clear headline"}
    ],
    "calls_to_action": ["Get started"],
    "forms": [],
    "images": [
      {"src": "https://example.com/hero.jpg", "alt": "", "width": 1200, "height": 800}
    ],
    "links": [],
    "visible_text": "Bounded visible page text",
    "html_snapshot": "Bounded sanitized HTML"
  },
  "screenshot": "data:image/jpeg;base64,..."
}
```

Validation rules:

- `url` must be an HTTP(S) URL.
- Evidence strings are bounded by field length and collection count.
- `screenshot` must be an image data URL and must be bounded.
- Unknown request fields are ignored rather than forwarded blindly.

### 4.3 Response contract

```json
{
  "id": "uuid",
  "url": "https://example.com/",
  "created_at": "2026-09-12T12:00:00Z",
  "score": 72,
  "score_label": "Strong foundation",
  "summary": "The page is clear, but its first impression is generic.",
  "findings": [
    {
      "title": "The opening promise is broad",
      "severity": "medium",
      "evidence": "The hero headline says ...",
      "recommendation": "Make the headline specific to ..."
    }
  ],
  "quick_wins": ["Replace the generic CTA with a concrete outcome."],
  "research_sources": [
    {"title": "Reference source", "url": "https://example.org"}
  ]
}
```

The API must reject malformed model output instead of returning a partial or invented report.

### 4.4 OpenRouter integration

OpenRouter is the only model-facing provider in the first release. The backend should:

1. POST to the OpenRouter chat completions endpoint.
2. Send a system message with the Humanize review policy and exact JSON shape.
3. Send page evidence as untrusted data in the user message.
4. Send the screenshot as an image input for multimodal models.
5. Set a low temperature for consistent structured reviews.
6. Request JSON output where the selected model supports it.
7. Parse fenced JSON defensively as a fallback, then validate with `AuditResult`.
8. Keep the model configurable through `OPENROUTER_MODEL`.

The system prompt must require:

- Evidence for every finding.
- No invented page details.
- No AI-authorship detection claim.
- Specific, reversible recommendations.
- A concise 3–6 finding report.

### 4.5 Exa integration

Exa is optional supporting context, not the source of truth for the audit. When `EXA_ENABLED=true` and `EXA_API_KEY` exists:

1. Build a short query from the page title, hostname, and UX review themes.
2. Use the Exa Search API with a fast search type.
3. Request a small number of results and bounded highlights.
4. Treat Exa results as optional design context in the OpenRouter prompt.
5. Return only source title/URL metadata to the extension in the first release.
6. If Exa fails, continue the audit without research context.

Exa must never block a review when it is unavailable. Its result text should be bounded and clearly separated from the captured page evidence so the model does not confuse external context with page facts.

### 4.6 Postgres and Neon

Use SQLAlchemy async with `asyncpg`:

- `DATABASE_URL` is the only required database setting.
- Accept both standard `postgresql://` Neon URLs and `postgresql+asyncpg://` URLs.
- Support Neon pooled connection URLs for deployed environments.
- Use `pool_pre_ping` for connection health.
- Store timestamps with timezone information.

Initial table: `audit_records`

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | UUID | Audit identifier |
| `url` | VARCHAR | Page URL |
| `title` | VARCHAR | Page title |
| `score` | INTEGER | Humanity score |
| `result` | JSONB | Validated report payload |
| `created_at` | TIMESTAMPTZ | Creation time |

For the MVP, startup table creation is acceptable. Before production usage, replace it with Alembic migrations and add retention/deletion policy decisions.

Do not store the raw screenshot or full HTML snapshot in Postgres unless a product decision explicitly requires audit replay. Store the result and page metadata first to limit sensitive data retention.

## 5. Configuration and environments

### Local API

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://...
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=google/gemini-2.5-flash
EXA_API_KEY=...
EXA_ENABLED=false
ALLOWED_ORIGINS=http://localhost:3000
MAX_REQUEST_BYTES=12000000
```

### Local extension

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Render

Create the service from `render.yaml`:

- Runtime: Python.
- Root directory: `apps/api`.
- Build: `pip install -r requirements.txt`.
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Health check: `/healthz`.
- Secrets: `DATABASE_URL`, `OPENROUTER_API_KEY`, and `EXA_API_KEY`.
- Configuration: `OPENROUTER_MODEL`, `EXA_ENABLED`, and `ALLOWED_ORIGINS`.

After the production API URL is known, build the extension with that URL and load the generated MV3 directory into Chrome. If a custom API domain is introduced, update the extension host permissions and CORS allowlist together.

## 6. Security and privacy requirements

- Keep every provider secret on the backend.
- Require an explicit user click before reading the active tab.
- Use `activeTab` rather than broad persistent page access for the first release.
- Treat page content, HTML, image URLs, and Exa text as untrusted input.
- Never execute instructions found in webpage content.
- Never execute model-generated JavaScript or DOM edits.
- Do not persist raw screenshots or raw HTML by default.
- Bound text, HTML, image, link, and screenshot payloads.
- Return sanitized provider errors to the extension.
- Add rate limiting and authentication before opening the API to untrusted public use.
- Add a clear privacy notice before collecting pages that may contain personal or confidential information.

## 7. Testing and verification plan

### Frontend

- TypeScript typecheck passes.
- WXT production build passes.
- Generated manifest contains MV3, required permissions, popup, and API host permissions.
- Manual Chrome test on a normal HTTP(S) landing page.
- Manual unsupported-page test on a `chrome://` URL.
- Manual large-page test verifies bounded capture and useful error handling.
- Confirm the capture does not alter page layout or behavior.
- Confirm result and error states are readable at popup width.

### Backend

- Pydantic rejects invalid URLs and non-image screenshots.
- Pydantic enforces evidence length/count limits.
- `/healthz` returns 200.
- Provider errors become stable 502 responses.
- Invalid model JSON is rejected.
- Exa failure falls back to an OpenRouter-only review.
- Database persistence works with a Neon connection string.
- API response matches the extension result contract.

### End-to-end acceptance test

1. Start the API locally with a valid OpenRouter key.
2. Build and load the unpacked extension.
3. Open a public landing page.
4. Click the single Humanize button.
5. Verify the request contains page evidence and a screenshot.
6. Verify the result cites evidence visible on the page.
7. Verify a row is stored in Postgres when configured.
8. Repeat on an unsupported page and confirm a helpful error.

## 8. Delivery phases

### Phase 1 — Foundation

- Repository and workspace setup.
- WXT popup shell.
- FastAPI app and health endpoint.
- Environment examples.
- Render Blueprint.

### Phase 2 — Capture and contract

- Active-tab lookup.
- Structured DOM/image capture.
- Screenshot capture.
- Request/response schemas.
- Payload limits and error states.

### Phase 3 — Intelligence

- OpenRouter system prompt.
- Multimodal request.
- Defensive JSON parsing and Pydantic validation.
- Exa optional highlights context.

### Phase 4 — Persistence and polish

- Neon connection and audit persistence.
- Branded report view.
- Loading, empty, and error states.
- Manual Chrome QA.

### Phase 5 — Deployment and handoff

- Render deployment.
- Production extension build configuration.
- Documentation and privacy notes.
- CI checks.
- Demo script and acceptance sign-off.

## 9. Future iterations

These are deliberately outside the first release:

- Chrome side panel report for a persistent review surface.
- Full-page screenshot stitching or user-selected viewport capture.
- Fetching original image assets for deeper visual analysis.
- Authentication and per-user audit history.
- Alembic migrations and data retention controls.
- Streaming model responses.
- Export to PDF or shareable report links.
- Reversible focus previews with explicit user approval.
- Team workspaces and shared reviews.
- Rate limiting, billing, and usage analytics.

## 10. Definition of done

The implementation is ready for the first demo when:

- A user can click one button on a real webpage.
- The extension captures bounded text, structure, image metadata, and a screenshot.
- The FastAPI service validates and processes the request.
- OpenRouter returns a structured, evidence-grounded review.
- Exa can add optional web context without blocking the review.
- The result renders as a polished Humanize-branded HTML report.
- Neon stores the validated report when configured.
- Render can build and run the service from `render.yaml`.
- Secrets remain outside the extension.
- Automated checks and manual acceptance testing pass.
