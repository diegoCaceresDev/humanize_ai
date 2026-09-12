# Humanize Team Plan

## Mission

Ship one dependable browser-native workflow: a reviewer audits the current page and understands evidence-based UX findings in a branded report.

## Product decisions

- **Surface:** Chrome popup with one primary button; page context is the product.
- **User:** a developer, founder, or designer reviewing a landing page before launch.
- **Core action:** audit the active tab and return a grounded UX review.
- **Human control:** the report is advisory. A reviewer may approve a temporary Focus Preview, which only applies Humanize-owned styling and can always be reverted.
- **Scope boundary:** Humanize is not an AI-authorship detector.

## Four-person ownership

1. **Extension engineer** — Manifest V3, one-button popup, active-tab capture, DOM/image extraction, and branded result view.
2. **Agent and backend engineer** — FastAPI endpoint, OpenRouter/Exa provider boundary, Neon persistence, validation, system prompt, and structured output.
3. **Product and UX engineer** — report language, severity, score explanation, and sample landing. Every finding cites page evidence.
4. **Demo and release owner** — onboarding documentation, test run, release notes, version tag, and repository hygiene.

## Two-hour delivery plan

- **0-25 min:** extension shell, DOM/image/screenshot capture, local FastAPI audit endpoint.
- **25-55 min:** report structure, constrained prompt, error states.
- **55-70 min:** report presentation, error states, and persistence check.
- **70-85 min:** generic landing page plus live QA.
- **85-120 min:** documentation, submission evidence, and video.

## Acceptance criteria

- [ ] One-button popup audits a real active HTTP(S) tab.
- [ ] Extension sends a screenshot and bounded DOM evidence to the local service.
- [ ] The server, never the extension, holds the OpenRouter key.
- [ ] Report includes score, summary, findings, evidence, and recommendations.
- [ ] Findings refer to actual page content, not invented details.
- [ ] Result is rendered as a branded HTML view.
- [ ] Result exposes measured CTA/accessibility signals from the active tab.
- [ ] Reviewer can inspect observed CTA elements, apply a Focus Preview, compare the visual-prominence proxy, and revert without modifying the site.
- [ ] `npm run verify` and `npm run test:api` pass.

## Two-minute demo

1. Show a deliberately generic landing page and name the problem.
2. Audit the actual page with Humanize.
3. Explain one finding with its visible evidence and inspect the matched CTAs on the page.
4. Apply the Focus Preview, show the before/preview measurement, then revert it.
5. Explain why the agent belongs inside the browser: it measures and safely tests the active page rather than only suggesting changes.

## Risks and controls

- **Invalid model JSON:** constrain prompt, parse defensively, show a clear error.
- **Large screenshot:** JPEG capture with a request payload cap.
- **Preview safety:** inject only namespaced Humanize styles and attributes; clean them up on revert, reset, or page refresh.
- **Invented UX claims:** require evidence in every finding; never execute model-generated DOM edits.
