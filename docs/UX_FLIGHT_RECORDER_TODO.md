# Humanize UX Flight Recorder TODO

This list follows the selected **Focus Preview** scope in [UX Flight Recorder Plan](UX_FLIGHT_RECORDER_PLAN.md). Complete the P0 items before adding any broader redesign or team features.

For the next implementation cycle, follow the [Deterministic Evidence Engine Plan](DETERMINISTIC_EVIDENCE_PLAN.md). It defines the versioned formulas, test strategy, and model boundary required before adding more preview types or persisted history.

## P0 — Demo-critical core workflow

- [x] Create a shared `pageEvidence` module in the extension.
  - [x] Collect CTA candidates with text, semantic type, bounding box, and viewport visibility.
  - [x] Identify the top-viewport/hero region without depending on page-specific selectors.
  - [x] Collect heading bounds in addition to the existing ordered heading structure.
  - [x] Count visible images with empty alt text.
  - [x] Detect visible form fields without labels or accessible names.
  - [x] Normalize all text, cap collections, and omit form values.
- [x] Define `PageMetrics` and `ElementEvidence` TypeScript types.
  - [x] Document which signals are deterministic measurements and which are heuristics.
  - [x] Add a session-only generated ID to every evidence element.
  - [x] Do not persist raw selectors or sensitive form content.
- [x] Add matching bounded Pydantic schemas to the API request contract.
  - [x] Reject unbounded element lists and invalid bounds.
  - [x] Keep the existing page-capture contract backward compatible during migration.
- [x] Update the audit prompt and `AuditResult` schema.
  - [x] Require citations to supplied evidence for every finding.
  - [x] Add optional `preview_suggestion` with a primary element ID and competing element IDs.
  - [x] Reject suggestions whose IDs are absent from the input evidence by dropping the optional suggestion while retaining the audit.
- [x] Build the evidence-inspection interaction in the popup.
  - [x] “Inspect on page” highlights only referenced elements.
  - [x] “Clear highlights” removes only Humanize annotations.
  - [x] Show the exact labels and count of highlighted elements in the inspect state.
- [x] Build Focus Preview in the active tab.
  - [x] Require an explicit click before injecting any styles.
  - [x] Use a namespaced `<style>` element and `data-humanize-*` attributes only.
  - [x] Highlight the suggested primary CTA and soften, but do not hide or disable, competing CTAs.
  - [x] Add an in-page “Preview only” annotation in addition to the popup status.
  - [x] Revert by removing Humanize-owned style and attributes only.
- [x] Implement before/preview measurement comparison.
  - [x] Recalculate from the same collector used for the original audit.
  - [x] Show CTA count, primary-action prominence proxy, and preview-state status.
  - [x] Label the comparison as visual/structural, not a conversion result.
- [ ] Add tests.
  - [ ] Unit-test CTA classification and metric calculations.
  - [x] Unit-test API validation for evidence and preview suggestions.
  - [ ] Add a manual smoke-test script for inspect → apply → compare → revert.

## P1 — Reliability and submission readiness

- [x] Handle navigation, stale tabs, and ambiguous CTA ranking during inspect, apply, and revert.
- [ ] Clear any active Humanize state when a new audit starts for the same tab.
- [ ] Add an explicit unavailable-preview state when a model suggestion does not map to live elements.
- [ ] Store the metric snapshot and preview outcome with persisted audit records.
- [ ] Add a view/reload path for a saved audit report.
- [x] Add a root `SUBMISSION.md`.
  - [x] Describe the browser-native core interaction.
  - [x] Separate inherited starter code from hackathon work.
  - [x] List live and optional integrations.
  - [x] Include clean-clone and demo steps.
- [ ] Prepare a two-minute recording using the demo narrative in the plan.
- [ ] Run `npm run verify` and `npm run test:api` against the final commit.

## P2 — Follow-up product value

- [ ] Add a local or Neon-backed audit timeline for the same URL.
- [ ] Detect metric regressions between saved audits.
- [ ] Add screenshot crops for evidence elements.
- [ ] Add an exportable, team-readable review artifact.
- [ ] Add more safe preview types:
  - [ ] heading hierarchy emphasis;
  - [ ] missing-alt annotation;
  - [ ] form-label annotation;
  - [ ] text-density guide.
- [ ] Add an element-level confidence and limitations display.

## Non-negotiable safeguards

- [x] No target-site writes, clicks, form submissions, or navigation.
- [x] No preview starts without explicit user action.
- [x] No user input values, passwords, tokens, or private DOM data in stored evidence.
- [x] No claims that a preview proves accessibility compliance, conversion, or usability outcomes.
- [x] No provider key or secret in the extension bundle, screenshots, test fixtures, commits, or demo recording.
