# Deterministic Evidence Engine Plan

## Decision

Humanize will treat the browser as the source of truth for observable page facts. The extension must produce the same evidence, rankings, and preview targets for the same page state, viewport, and engine version—without requiring an LLM or network request.

The LLM may explain measured evidence. It must not invent measurements, select an unsafe DOM target, or determine whether a preview may execute.

## Product promise

> Humanize separates what it measured from what it inferred.

Every result should make it clear which information is deterministic browser evidence, which conclusion is a transparent heuristic, and which recommendation is an LLM-assisted interpretation.

## Determinism contract

For a fixed input tuple:

```text
(document state, viewport dimensions, scroll position, browser engine version,
 evidence-engine version, preview state)
```

the Evidence Engine returns an identical canonical snapshot:

```text
canonical snapshot = normalized elements + metrics + ranking + diagnostics
```

The implementation may use DOM APIs and computed styles, but it must not use timestamps, randomness, network calls, model outputs, locale-dependent formatting, or unstable iteration order in its calculations.

### What is deterministic vs. interpretive

| Layer | Owner | Examples | Rule |
| --- | --- | --- | --- |
| Browser facts | Extension | element bounds, text, tag, accessible name, `alt`, label relationship | Captured locally and reproducibly. |
| Derived metrics | Extension | hero CTA count, heading order, prominence score | Pure, versioned formulas with component breakdowns. |
| Preview decision | Extension + explicit user click | target identity, styles injected, measurement comparison | Must only use validated local evidence. |
| Interpretation | Model | why three CTAs may feel competing, copy recommendation | Must cite browser facts; may not alter them. |
| Outcome claims | Not supported | conversion increase, compliance, usability proof | Never infer from a structural proxy. |

## Architecture

```text
Live tab
  │
  ▼
Deterministic collector ──► Canonicalizer ──► Metric engine ──► Target ranking
  │                              │                   │                  │
  │                              ▼                   ▼                  ▼
  └────────────────────────► Evidence snapshot   Diagnostics        Preview plan
                                                                         │
                              LLM receives read-only snapshot ──────────┤
                                                                         ▼
                                                             User approves preview
                                                                         │
                                                                         ▼
                                                          Namespaced temporary styles
                                                                         │
                                                                         ▼
                                                         Same engine re-measures state
```

## Canonical evidence snapshot

Introduce one versioned browser-side object. The API receives a privacy-filtered form; the extension keeps session-only locators locally.

```ts
type EvidenceSnapshotV1 = {
  engineVersion: "deterministic-evidence-v1";
  document: {
    url: string;
    viewport: { width: number; height: number; scrollX: number; scrollY: number };
    capturedAt: "omitted"; // snapshots are comparable without a time-dependent field
  };
  elements: EvidenceElement[];
  headings: HeadingEvidence[];
  metrics: PageMetrics;
  ranking: {
    primaryCtaId: string | null;
    competingCtaIds: string[];
    method: "cta-prominence-v1";
  };
  diagnostics: Diagnostic[];
};
```

### Stable element identity

The current generated ordinal IDs (`cta-1`, `heading-1`) are appropriate only within a live session. Replace them for persisted comparisons with a stable fingerprint:

```text
fingerprint = hash(
  normalized role + normalized accessible label + structural path + rounded bounds + ordinal among matching siblings
)
```

Rules:

- Never hash form values, tokens, query strings, or arbitrary private text.
- Keep the raw locator extension-local and session-only.
- Use a deterministic structural path that does not depend on CSS module hashes or random IDs.
- Keep a `captureOrdinal` as a tie-breaker; do not use DOM object identity.
- If the same fingerprint appears twice, emit a diagnostic and require user inspection rather than applying a preview automatically.

## Collector design

Split the current serialized page function into pure stages. The injected wrapper should be thin; all logic that can run outside the page should be separately testable.

### Stage 1 — Collect raw candidates

Capture a bounded set of raw facts in DOM order:

- action candidates: `button`, submit/button inputs, `[role=button]`, action-like links;
- headings: `h1` through `h3`;
- visible images and alt text;
- visible input, textarea, and select controls;
- viewport and document geometry;
- current Humanize preview state.

Raw candidates must preserve DOM order and include only normalized primitives: tag, role, accessible label, rectangle, visibility flags, and session locator.

### Stage 2 — Canonicalize

Apply one set of pure normalization rules:

- trim whitespace, collapse internal whitespace, normalize Unicode to NFC;
- preserve source casing for display but use lowercase normalized text for matching;
- round geometry to whole CSS pixels;
- sort by document order, then top, left, and structural fingerprint;
- cap candidate collections before serializing;
- use explicit `null` for unavailable values instead of sentinel strings;
- record omitted candidates in diagnostics instead of silently changing the denominator.

### Stage 3 — Derive metrics

Each metric is a pure function of the canonical candidate list and viewport.

```ts
type MetricResult = {
  id: string;
  value: number | string | boolean;
  method: string;
  inputs: string[];        // evidence IDs used
  limitations: string[];
};
```

Metrics must retain an input list and limitations so the UI and API can explain their source.

## Metric specifications

### Visibility

An element is visible when all conditions are true:

1. computed `display` is not `none`;
2. computed `visibility` is not `hidden` or `collapse`;
3. effective opacity is greater than zero;
4. bounding rectangle has positive width and height;
5. rectangle overlaps the viewport when a viewport-specific metric is calculated.

Use a distinct `rendered` field for conditions 1–4 and `viewportVisible` for condition 5. Do not conflate rendered but below-the-fold elements with hidden elements.

### CTA classification

Classification order:

1. Native button and submit/button input → CTA candidate.
2. Element with `role="button"` → CTA candidate.
3. Link → CTA candidate only if it has an action verb or an explicit action-like semantic role.
4. Navigation, hash-only, phone, mail, legal, and social links → excluded with a diagnostic reason.

Store `classificationReason`, for example `native-button`, `action-link-keyword`, or `excluded-navigation-link`. This makes false positives inspectable.

### Hero region

Define the hero region with one explicit versioned rule:

```text
heroTop = 0
heroBottom = min(viewportHeight × 0.60, 720 CSS px)
hero overlap = candidate rect overlaps [heroTop, heroBottom]
```

Do not call it “the hero element”; it is a top-viewport region heuristic. The UI must say “first viewport” unless a real semantic hero landmark is detected.

### Primary-action prominence

Replace the opaque total with an explainable component score:

```text
score = clamp(0, 100,
  base(28)
  + actionVerb(0 or 16)
  + position(0–24)
  + area(0–24)
  + firstViewport(0 or 14)
  + previewState(-18, 0, or +22)
)
```

The snapshot records every component. Ties resolve in this order:

1. highest score;
2. in first viewport;
3. topmost rectangle;
4. leftmost rectangle;
5. canonical candidate order.

If the top two scores differ by fewer than five points, emit `ambiguous-primary-cta`. The UI should then offer inspection but avoid presenting the result as a confident recommendation.

### Accessibility signals

- Missing alt: a rendered image with empty `alt`, excluding a declared decorative image only when the extension can reliably identify it.
- Unlabeled field: a rendered editable control with no associated `<label>`, `aria-label`, or `aria-labelledby`.
- These are signals for inspection—not claims of WCAG conformance.

## Preview plan determinism

The extension, not the model, produces a `PreviewPlanV1`.

```ts
type PreviewPlanV1 = {
  planVersion: "focus-preview-v1";
  primaryId: string;
  competingIds: string[];
  selectionReason: "highest-prominence" | "user-selected";
  blockedReasons: string[];
};
```

Before injection, validate each target against the current page:

1. resolve session locator;
2. confirm normalized label and structural fingerprint still match;
3. confirm the element is rendered;
4. abort the whole plan if the primary target is stale;
5. omit stale competing targets and report their IDs/reasons;
6. never follow navigation or invoke any page event.

The before and preview snapshots must use the same engine version, viewport, and metric formula. If they do not, label the comparison unavailable rather than comparing incompatible numbers.

## API and model boundary

Send a privacy-filtered `EvidenceSnapshotV1` to the API:

- include metric values, component breakdowns, stable evidence IDs, labels, rounded bounds, and diagnostics;
- exclude session locators, raw HTML paths, form values, credentials, and user-entered data;
- include `engineVersion` and metric method versions.

The API should validate the snapshot with Pydantic before a provider call. The model response may include optional evidence IDs, but the API must:

1. discard unknown IDs;
2. reject preview suggestions with a missing or stale primary target;
3. preserve a useful audit when an optional suggestion is invalid;
4. record a model-validation diagnostic instead of turning a bad optional suggestion into a browser action.

The extension treats model suggestions as annotations only. A model cannot send CSS, selectors, JavaScript, or action parameters to the tab.

## Testing strategy

### Unit tests — pure engine

Extract canonicalization, classification, ranking, and metric functions into a dependency-free TypeScript module. Test them without Chrome.

Required fixtures:

- one obvious primary CTA;
- equal-score CTA tie;
- navigation links mixed with action links;
- below-the-fold CTA;
- hidden, transparent, and zero-size elements;
- duplicate labels and duplicate fingerprints;
- missing alt text and decorative images;
- labeled and unlabeled inputs;
- preview state before/after comparison;
- Unicode/whitespace normalization.

Assertions must include both results and diagnostics.

### Browser integration tests

Use a static fixture page under `apps/demo` and load it at a fixed viewport. Verify:

1. two repeated captures create byte-for-byte equal canonical snapshots after omitting runtime-only fields;
2. inspect adds only `data-humanize-evidence` and one Humanize style node;
3. preview adds only namespaced state plus the preview marker;
4. revert removes every Humanize-owned node/attribute;
5. page refresh clears state;
6. a stale locator blocks primary preview safely.

### API contract tests

- valid snapshot accepted;
- unknown fields ignored or rejected according to the declared contract;
- oversized lists and invalid geometry rejected;
- locator and form-value fields rejected from the network payload;
- invalid model evidence IDs become diagnostics and cannot create a preview plan.

### Golden snapshot tests

Store canonical JSON snapshots for the fixture pages. CI compares collector output against the goldens using a stable serializer with sorted keys. Any metric or ranking change requires:

1. an engine-version increment;
2. updated fixture/golden evidence;
3. a changelog entry explaining the behavior change;
4. a reviewer acknowledgement that before/after history is not cross-version comparable.

## Observability and diagnostics

Provide an optional developer-only Evidence Debug view that shows:

- engine version and viewport;
- candidate list with classification reasons;
- prominence score components and tie-break result;
- excluded candidates and reasons;
- preview target validation results;
- snapshot hash computed from the canonical privacy-safe payload.

Do not expose raw locators, form values, or sensitive page text in exported reports.

## Rollout phases

### Phase A — Make the current engine testable

- Extract pure normalization, CTA classification, score calculation, and ranking modules.
- Add canonical snapshot serialization and engine version fields.
- Add unit fixtures and golden snapshots.

**Exit:** repeated fixture captures are identical and every primary CTA has a component-score explanation.

### Phase B — Harden target safety

- Add structural fingerprints and duplicate detection.
- Add pre-preview validation diagnostics.
- Block ambiguous or stale primaries by default.

**Exit:** no preview can target a changed or ambiguous primary without an explicit user re-selection.

### Phase C — Formalize the API boundary

- Replace ad hoc browser evidence with `EvidenceSnapshotV1`.
- Add strict API validation and model-suggestion sanitization.
- Surface model validation diagnostics in the developer view.

**Exit:** no LLM output can alter target selection or styles without validation against local evidence.

### Phase D — Trustworthy history

- Persist engine version, canonical metric snapshot, and preview outcome.
- Compare only snapshots from compatible engine versions.
- Show “not comparable” instead of inventing a trend across formula changes.

**Exit:** audit history is reproducible and explains every metric change.

## Acceptance criteria

- [ ] Same fixture, viewport, and engine version produce identical canonical snapshots.
- [ ] Every ranking includes score components, tie-breaks, and diagnostics.
- [ ] No model output can identify a browser target outside the local snapshot.
- [ ] Every preview target is revalidated immediately before styling.
- [ ] Revert removes all and only Humanize-owned state.
- [ ] API payloads never include locators, form values, secrets, or raw private DOM paths.
- [ ] Golden tests gate changes to metric formulas and target ranking.
- [ ] UI distinguishes measurement, heuristic, interpretation, and unsupported outcome claim.

## Immediate implementation order

1. Extract pure CTA classification and score/ranking functions from `pageEvidence.ts`.
2. Add `engineVersion`, score components, classification reasons, and diagnostics to the local snapshot.
3. Add unit fixtures and golden snapshot tests.
4. Add pre-preview fingerprint validation and ambiguous-primary blocking.
5. Formalize `EvidenceSnapshotV1` in the API schema and sanitize optional model evidence IDs.
6. Persist compatible snapshots only after the deterministic engine is stable.
