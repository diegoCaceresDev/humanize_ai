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

Active Chrome tab -> content script and service worker -> Humanize side panel -> local Next.js endpoint -> OpenAI Responses API.

## Project layout

- `apps/humanize-extension/`: Chrome Manifest V3 side-panel extension.
- `apps/web/src/app/api/humanize-audit/route.ts`: server-side LLM boundary.
- `docs/TEAM_PLAN.md`: roles, delivery plan, demo script, and acceptance criteria.

## Setup

**Prerequisites:** Node.js 22+, Google Chrome, and an OpenAI API key with an available multimodal model.

Run `npm ci`, copy `.env.example` to `.env`, configure `MODEL_PROVIDER=openai`, `OPENAI_API_KEY`, and `MODEL`, then run `npm run dev:web`.

In Chrome, open `chrome://extensions`, enable **Developer mode**, select **Load unpacked**, and choose `apps/humanize-extension`.

## Safety and privacy

- The extension never receives or stores the OpenAI key; the local server owns it.
- An audit is explicitly initiated by the reviewer and uses only the active tab's visible screenshot plus bounded DOM evidence.
- Page text and HTML are treated as untrusted data, not instructions.
- The focus preview is temporary and is removed by revert or page refresh.
- Humanize does not claim to be an AI-authorship detector.

## Verification

Run `npm run verify` and `npm run build --workspace web`.

## Inherited vs. hackathon work

**Inherited:** the Agents, Everywhere starter kit, its monorepo structure, Next.js/CopilotKit infrastructure, model configuration pattern, and verification tooling.

**Built during the hackathon:** Humanize's product concept, Chrome extension, screenshot and DOM evidence pipeline, constrained UX-review prompt, server-side audit endpoint, side-panel report, temporary preview, PDF workflow, and project documentation.

## Team

See [the team plan](docs/TEAM_PLAN.md) for ownership, acceptance criteria, risks, and the two-minute demo sequence.
