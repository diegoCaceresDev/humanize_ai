# Humanize AI v0.2.0

Release date: 2026-09-12

Humanize v0.2.0 introduces the **UX Flight Recorder**: a browser-native evidence and verification loop that goes beyond an LLM-generated UX report.

## Included

- Browser-measured evidence for visible CTA candidates, hero CTA count, missing alt text, and unlabeled form fields.
- Element-level CTA inspection in the active tab.
- A user-approved **Focus Preview** that highlights the measured primary CTA and softens up to five competing actions.
- A before/preview primary-action prominence comparison and explicit `Site mutations: 0` status.
- A bounded API contract for browser evidence; internal DOM locators remain inside the extension and are never sent to the API.

## How Focus Preview works

1. Audit an HTTP(S) page from the Humanize popup.
2. Inspect the CTA evidence on the live page.
3. Apply Focus Preview from the report.
4. Review the structural/visual comparison.
5. Revert the preview when finished.

Focus Preview is temporary. It only injects Humanize-owned CSS and attributes into the current tab; it does not change target-site content, behavior, or saved styles. Reverting, leaving the result view, or refreshing the page clears it.

## Validation

- Extension type-check and production build pass.
- API test suite passes with browser-evidence validation and endpoint coverage.

## Scope boundaries

- The extension handles normal HTTP(S) tabs only.
- Focus Preview is not evidence of conversion, usability, or accessibility compliance.
- Humanize does not automatically apply recommendations or generate site edits.
- Audit history persistence remains optional and depends on the configured database.
