# Humanize UX Flight Recorder Plan

## Decision

Humanize will evolve from an LLM-powered page critique into a browser-native UX verification tool.

The selected core interaction is:

> Detect a specific clarity problem in the current page, let the reviewer preview a safe focused version, and report exactly what changed without modifying the site permanently.

The model remains useful for interpreting evidence and explaining tradeoffs. The differentiating value comes from the extension's access to the live page: it can measure elements, place temporary annotations, compare browser-derived signals, and preserve a review artifact. A standalone chat assistant cannot provide that workflow from a text prompt alone.

## Product promise

Humanize is the browser's evidence layer for UX decisions. It shows what it observed, lets a person test a focused preview safely, and verifies the result.

The product must not claim that a preview proves user conversion or accessibility compliance. It verifies only the deterministic visual and structural signals that Humanize collects from the active tab.

## User and job to be done

**Primary user:** a founder, developer, or designer preparing a landing page for review or launch.

**Job:** “While looking at this exact page, help me identify the most important clarity issue, inspect the affected elements, and test a reversible alternative before I ask someone to change the site.”

## Why the browser is essential

| Browser-native capability | What Humanize does | What a generic LLM alone cannot reliably do |
| --- | --- | --- |
| Live DOM | Counts and classifies visible headings, CTA candidates, images, labels, and bounding boxes. | Know what is actually rendered in the active tab. |
| Viewport capture | Records the visible first impression and anchors feedback to the current screen. | Verify the current visual hierarchy or layout. |
| Element targeting | Highlights the actual CTA, heading, or image connected to a finding. | Point a reviewer to the exact live element. |
| Temporary preview | Applies scoped CSS only after an explicit user action, then removes it on revert or refresh. | Test an alternative directly in the user's current context. |
| Measurement diff | Compares deterministic metrics before and during a preview. | Prove which observable signals changed. |

## Scope for the next build

### In scope: Focus Preview

The first flight-recorder feature is a **Focus Preview** for competing calls to action.

1. Humanize captures the current page and calculates deterministic browser metrics.
2. The audit identifies a primary CTA candidate and any competing CTA candidates.
3. The result panel displays the evidence and an **Apply focus preview** button.
4. After explicit approval, the extension injects temporary, namespaced CSS into the active tab:
   - primary CTA receives a visible focus ring;
   - competing CTAs are visually de-emphasized without being hidden, disabled, moved, or edited;
   - annotated elements receive an accessible label identifying the preview.
5. Humanize recalculates the same browser metrics and renders a before/preview comparison.
6. The reviewer can select **Revert preview**. Revert removes only Humanize's injected stylesheet and annotations. Refreshing the page also removes the preview.

### Explicitly out of scope

- Editing a site's HTML, copy, classes, or persisted styles.
- Clicking, submitting, or navigating the target page.
- Claiming a conversion, usability, WCAG, or business outcome from the preview.
- Auto-applying model-generated code.
- Multi-page crawling or authenticated data collection.
- Team collaboration, notifications, and long-term trend dashboards until the single-page workflow is dependable.

## Evidence model

The extension should calculate evidence locally before calling a model. This keeps the factual basis inspectable and avoids treating a score as unexplained model opinion.

### Page metrics

| Metric | Calculation | Used for |
| --- | --- | --- |
| Visible CTA count | Visible buttons, submit inputs, role buttons, and action-like links in the viewport. | Identify CTA competition. |
| Hero CTA count | CTA candidates whose bounding boxes overlap the top viewport region. | Prioritize first-impression conflicts. |
| CTA labels | Normalized visible CTA text, element type, and bounding box. | Cite exact evidence. |
| Heading structure | Ordered visible `h1`–`h3` elements and their bounds. | Identify hierarchy gaps. |
| Missing alt count | Visible informative images with empty alt text. | Accessibility signal. |
| Form-label signal | Visible inputs lacking an associated label or accessible name. | Accessibility signal. |
| Text density | Bounded visible characters in viewport regions. | Flag crowding as a supporting signal only. |
| Primary-action prominence | A transparent heuristic from CTA size, viewport position, visibility, and contrast proxy. | Compare the same page before and during preview. |

All metrics must carry a `method` or `limitations` label where a heuristic is used. The UI should use language such as “observed 3 hero CTAs” and “preview increases visual emphasis,” never “this will improve conversion.”

### Element evidence contract

Each actionable finding should include one or more element references:

```ts
type ElementEvidence = {
  id: string;                 // Generated only for the current page session
  role: "primary-cta" | "competing-cta" | "heading" | "image" | "form-field";
  label: string;              // Visible text or accessible label
  selectorHint: string;       // Short, non-persistent diagnostic hint
  bounds: { x: number; y: number; width: number; height: number };
  viewportVisible: boolean;
};
```

`selectorHint` is diagnostic only. The extension must not save a full DOM path containing private values, form contents, or user data.

## Architecture

```text
Active Chrome tab
  │
  ├── User starts audit
  │     ├── collect bounded DOM evidence + screenshot
  │     ├── calculate deterministic metrics locally
  │     └── send bounded evidence to FastAPI
  │
  ├── FastAPI + OpenRouter
  │     └── return evidence-backed finding + optional Exa context
  │
  ├── User approves Focus Preview
  │     ├── execute scoped preview script in the active tab
  │     ├── recalculate same local metrics
  │     └── show before / preview metric difference
  │
  └── User reverts
        └── remove Humanize-only style and annotations
```

### Client responsibilities

- Generate session-only element IDs and collect bounds.
- Keep preview state keyed by `tabId` and a generated `auditId`.
- Use a single injected `<style id="humanize-focus-preview">` and `data-humanize-preview` attributes.
- Verify a preview target still belongs to the current document before applying it.
- Restore the page solely by removing Humanize-owned state; never restore captured site values.
- Display an explicit scope note: “Preview only. No site changes are saved.”

### API responsibilities

- Accept bounded metrics and element evidence with the existing audit request.
- Require each model finding to reference supplied evidence rather than inventing selectors or measurements.
- Return a structured `preview_suggestion` only when evidence supports one.
- Persist the audit artifact only when the configured database is available.
- Never issue browser actions, generate injected JavaScript, or execute preview decisions.

## UI flow

### 1. Audit result

Show score, summary, findings, and a “Measured on this page” section. For a CTA-competition finding, display the number of visible hero CTAs and the exact labels.

### 2. Inspect evidence

Selecting a finding asks the extension to highlight its matching live elements. The panel states how many elements are highlighted and gives the reviewer a **Clear highlights** action.

### 3. Apply focus preview

The primary CTA finding shows one violet primary action:

> Apply focus preview

The confirmation copy is short and specific:

> We’ll highlight “Book a demo” and soften two competing actions in this tab. Nothing is saved to the site.

### 4. Compare

Show a compact before/preview table:

| Signal | Before | Preview | Meaning |
| --- | ---: | ---: | --- |
| Hero CTAs detected | 3 | 3 | No content removed. |
| Primary-action prominence | 44 | 71 | The primary action is more visually distinct. |
| Page mutations | 0 | 0 | Only Humanize’s temporary overlay is active. |

### 5. Revert

The primary action changes to **Revert preview**. On success, show “Preview removed. The page is back to its original state.”

## Delivery phases

### Phase 1 — Deterministic evidence

Implement a reusable browser collector for CTA candidates, bounds, heading structure, image alt signals, form-label signals, and metrics. Add unit tests for normalization and metric calculations.

**Exit criteria:** a local debug view can show the metrics for the demo page without an LLM call.

### Phase 2 — Evidence-backed audit

Pass metrics and element references to the API. Update the prompt and response schema so one CTA-competition finding may include a structured preview suggestion.

**Exit criteria:** the panel identifies actual CTA labels from the active page and never returns a preview target not present in the evidence payload.

### Phase 3 — Inspect and preview

Implement temporary highlight and focus-preview scripts, a tab-scoped state machine, and a clean revert path.

**Exit criteria:** preview and revert work repeatedly on the demo page; refresh always clears Humanize state.

### Phase 4 — Verification and report

Recalculate metrics after preview, display the before/preview diff, and save the audited result when persistence is configured.

**Exit criteria:** the demo shows a real, reproducible metric difference and accurately labels its limitations.

### Phase 5 — Submission hardening

Run the live integration, record a two-minute demo, add `SUBMISSION.md`, and document inherited vs. event-built work.

**Exit criteria:** another reviewer can run the extension, reproduce the core flow, and understand exactly what is live versus simulated.

## Acceptance criteria

- [ ] Humanize extracts browser-native CTA, hierarchy, and accessibility signals without an LLM.
- [ ] Every previewable finding names the observed elements and includes a scope/limitations note.
- [ ] A reviewer explicitly approves all preview actions.
- [ ] Focus Preview uses only namespaced, temporary page state owned by Humanize.
- [ ] Revert removes the preview reliably; refresh removes it by design.
- [ ] The before/preview comparison uses the same metric definitions.
- [ ] The extension never claims that a visual proxy equals user behavior or compliance.
- [ ] The core flow works against a real HTTP(S) page and the supplied demo page.
- [ ] `npm run verify` and `npm run test:api` pass before recording.

## Demo narrative

1. Start on a real or demo landing page containing three hero CTAs.
2. Explain that Humanize sees the rendered page, not a pasted description.
3. Audit the page and open the CTA-competition finding.
4. Inspect the exact highlighted actions.
5. Apply Focus Preview after the extension explains the temporary change.
6. Show the measured before/preview comparison and state its limitation.
7. Revert the preview and show that no site change remains.

The key line for judges:

> A chat model can recommend a clearer CTA. Humanize measures the live page, lets the reviewer test that recommendation in context, and verifies what changed without taking control away from them.
