# Humanize Team Plan

## Mission

Ship one dependable browser-native workflow: a reviewer audits the current page, understands evidence-based UX findings, applies a reversible preview, and exports the report.

## Product decisions

- **Surface:** Chrome side panel; page context is the product.
- **User:** a developer, founder, or designer reviewing a landing page before launch.
- **Core action:** audit the active tab and return a grounded UX review.
- **Human control:** preview is explicit, reversible, and never writes to the target site.
- **Scope boundary:** Humanize is not an AI-authorship detector.

## Four-person ownership

1. **Extension engineer** — Manifest V3, side panel, active-tab capture, DOM extraction, preview, and revert.
2. **Agent and backend engineer** — local audit endpoint, server-side key boundary, validation, system prompt, and structured output.
3. **Product and UX engineer** — report language, severity, score explanation, and sample landing. Every finding cites page evidence.
4. **Demo and release owner** — README, submission checklist, test run, two-minute script, recording, and repository hygiene.

## Two-hour delivery plan

- **0-25 min:** extension shell, DOM/screenshot capture, local audit endpoint.
- **25-55 min:** report structure, constrained prompt, error states.
- **55-70 min:** reversible preview and PDF print workflow.
- **70-85 min:** generic landing page plus live QA.
- **85-120 min:** documentation, submission evidence, and video.

## Acceptance criteria

- [ ] Side panel audits a real active HTTP(S) tab.
- [ ] Extension sends a screenshot and bounded DOM evidence to the local service.
- [ ] The server, never the extension, holds the OpenAI key.
- [ ] Report includes score, summary, findings, evidence, and recommendations.
- [ ] Findings refer to actual page content, not invented details.
- [ ] Preview is reversible or removed by refresh.
- [ ] PDF export opens the browser print flow.
- [ ] `npm run verify` passes and the web app builds.

## Two-minute demo

1. Show a deliberately generic landing page and name the problem.
2. Audit the actual page with Humanize.
3. Explain one finding with its visible evidence.
4. Apply and revert the focus preview.
5. Save the report as a PDF.
6. Explain why the agent belongs inside the browser.

## Risks and controls

- **Invalid model JSON:** constrain prompt, parse defensively, show a clear error.
- **Large screenshot:** JPEG capture with a request payload cap.
- **Scope expansion:** keep only the reversible focus preview.
- **Invented UX claims:** require evidence in every finding; never execute model-generated DOM edits.
