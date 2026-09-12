# Humanize AI — Submission Checklist

## Project title

Humanize AI

## What we built

Humanize is a browser-native UX review agent for the page currently open in Chrome. A reviewer intentionally audits the active tab; Humanize collects bounded DOM and viewport evidence, produces a structured evidence-backed report, and lets the reviewer inspect the observed CTAs on the live page.

Its core differentiator is **Focus Preview**. With an explicit reviewer action, Humanize temporarily emphasizes the observed primary action and softens competing actions in the current tab. It then compares a browser-derived visual-prominence proxy before and during the preview. Revert, leaving the report, or refreshing the page removes all Humanize-owned page state.

## Who it is for

Developers, founders, and designers reviewing a landing page before launch who need feedback grounded in the page they are actually looking at.

## Why the browser context matters

Humanize can see the current viewport, the rendered heading hierarchy, CTA candidates, image alt-text signals, form-label signals, and element positions. It can point to the affected live elements and safely test a temporary visual alternative. A standalone chat prompt cannot reliably collect, target, or verify that active browser state.

## Sponsor technologies

- **OpenRouter:** server-side multimodal model gateway for structured UX review.
- **Exa:** optional web-grounding source links for the review context.
- **Neon:** optional persisted audit records in Postgres.

## What was built during the hackathon

- Humanize product concept and browser-native UX-review workflow.
- Chrome extension, active-tab evidence capture, screenshot flow, and branded report.
- Browser-measured UX Flight Recorder signals and Focus Preview/revert experience.
- FastAPI audit service, constrained OpenRouter/Exa integration, and Neon persistence path.
- Demo page, tests, documentation, release notes, and Signal Violet design system.

## Inherited and third-party building blocks

- AI Tinkerers event rules, reference material, and starter guidance.
- Open-source frameworks and packages including WXT, React, FastAPI, SQLAlchemy, Alembic, and Chrome APIs.
- OpenRouter, Exa, Neon, and Render services.

## Clean-clone quickstart

Follow [Team Setup](docs/TEAM_SETUP.md), then run:

```bash
npm run verify
npm run test:api
npm run package:extension
```

For a no-credential smoke test, set `DEMO_MODE=true` in the root `.env`. For a live audit, configure the server-side OpenRouter key; Exa and Neon are optional.

## Two-minute demo outline

1. Open the supplied demo landing page and explain that Humanize reads the rendered page rather than a pasted description.
2. Run **Humanize this page**.
3. Open the observed CTA evidence and select **Inspect on page**.
4. Apply **Focus Preview** after the UI explains that it is temporary.
5. Show the before/preview measurement and the in-page “Preview only” marker.
6. Revert the preview and show that the target site has not been changed.

## Submission links to complete

- Public repository: `https://github.com/diegoCaceresDev/humanize_ai`
- Two-minute video: _add before submission_
- Social post: _add before submission and tag partners per local organizer instructions_

## Safety and scope

- Humanize never sends provider keys to the extension.
- Audits only begin after an explicit reviewer action.
- The extension audits normal HTTP(S) pages only.
- Focus Preview is a visual/structural proxy, not a claim about conversion, usability, or accessibility compliance.
- Do not include secrets, private screenshots, or confidential page content in the repository, recording, or submission.
