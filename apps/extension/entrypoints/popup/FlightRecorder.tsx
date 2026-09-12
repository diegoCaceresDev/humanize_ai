import { useEffect, useState } from "react";

import { applyFocusPreview, clearInspection, inspectElements, revertFocusPreview } from "./pagePreview";
import { collectPageEvidence, type BrowserEvidence, type CapturedPage, type PageMetrics } from "./pageEvidence";

async function executeInTab<T>(tabId: number, func: unknown, args: unknown[] = []): Promise<T | undefined> {
  const [execution] = await browser.scripting.executeScript({
    target: { tabId },
    func: func as never,
    args: args as never[],
  });
  return execution?.result as T | undefined;
}

function Metric({ label, value, detail }: { label: string; value: number | string; detail: string }) {
  return <div className="metric-row"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>;
}

export function FlightRecorder({ tabId, evidence, onError }: { tabId: number; evidence: BrowserEvidence; onError: (message: string) => void }) {
  const [inspectionCount, setInspectionCount] = useState(0);
  const [previewMetrics, setPreviewMetrics] = useState<PageMetrics | null>(null);
  const [busy, setBusy] = useState(false);
  const primary = evidence.elements.find((element) => element.role === "primary-cta");
  const competitors = evidence.elements.filter((element) => element.role === "competing-cta");
  const inspectable = evidence.elements.slice(0, 6);
  const previewBlocked = evidence.ranking.ambiguousPrimary;

  useEffect(() => () => {
    void executeInTab<void>(tabId, revertFocusPreview);
    void executeInTab<void>(tabId, clearInspection);
  }, [tabId]);

  if (!primary) return null;

  async function inspect() {
    setBusy(true); onError("");
    try {
      const count = await executeInTab<number>(tabId, inspectElements, [inspectable]);
      setInspectionCount(count || 0);
      if (!count) onError("The page changed since the audit, so Humanize could not safely highlight those elements.");
    } catch {
      onError("Humanize could not inspect this page. It may have navigated or reloaded.");
    } finally { setBusy(false); }
  }

  async function clear() {
    setBusy(true); onError("");
    try { await executeInTab<void>(tabId, clearInspection); setInspectionCount(0); } catch { onError("Humanize could not clear the page highlights."); } finally { setBusy(false); }
  }

  async function preview() {
    setBusy(true); onError("");
    try {
      const applied = await executeInTab<{ primaryFound: boolean }>(tabId, applyFocusPreview, [primary, competitors]);
      if (!applied?.primaryFound) throw new Error("The selected action is no longer available on this page.");
      const refreshed = await executeInTab<CapturedPage>(tabId, collectPageEvidence);
      if (!refreshed) throw new Error("Humanize could not verify the preview.");
      setPreviewMetrics(refreshed.evidence.metrics);
      setInspectionCount(0);
    } catch (error) {
      onError(error instanceof Error ? error.message : "Humanize could not apply the preview.");
    } finally { setBusy(false); }
  }

  async function revert() {
    setBusy(true); onError("");
    try { await executeInTab<void>(tabId, revertFocusPreview); setPreviewMetrics(null); } catch { onError("Humanize could not revert the preview. Refreshing the page will remove it."); } finally { setBusy(false); }
  }

  return <>
    <section className="section measured-card">
      <div className="section-heading"><span className="eyebrow">Measured on this page</span><span className="method-tag">Browser evidence</span></div>
      <Metric label="Visible CTAs" value={evidence.metrics.visibleCtaCount} detail={`${evidence.metrics.heroCtaCount} in the first viewport`} />
      <Metric label="Primary action" value={evidence.metrics.primaryCtaLabel} detail={`${evidence.metrics.primaryActionProminence}/100 visual prominence`} />
      <Metric label="Heading structure" value={evidence.headings.length} detail={evidence.headings.length ? evidence.headings.map((heading) => heading.level.toUpperCase()).join(" → ") : "No visible headings detected"} />
      <Metric label="Accessibility signals" value={evidence.metrics.missingAltCount + evidence.metrics.unlabeledFormFieldCount} detail={`${evidence.metrics.missingAltCount} missing alt · ${evidence.metrics.unlabeledFormFieldCount} unlabeled fields`} />
    </section>
    <section className="section preview-card">
      <div className="section-heading"><span className="eyebrow">Focus Preview</span><span className={`preview-status ${previewBlocked ? "blocked" : ""}`}>{previewMetrics ? "Preview active" : previewBlocked ? "Needs selection" : "Reversible"}</span></div>
      <h2>Test a clearer first action.</h2>
      <p>Humanize observed <strong>“{primary.label}”</strong> as the most prominent action. {competitors.length ? `It can temporarily soften ${Math.min(competitors.length, 5)} competing action${competitors.length === 1 ? "" : "s"}.` : "It can temporarily make this action easier to inspect."}</p>
      {!previewMetrics && <div className="preview-actions"><button className="secondary-button" onClick={inspectionCount ? clear : inspect} disabled={busy}>{inspectionCount ? "Clear highlights" : "Inspect on page"}</button><button className="audit-button compact" onClick={preview} disabled={busy || previewBlocked}>{previewBlocked ? "Inspect candidates first" : busy ? "Applying…" : "Apply focus preview"}<span>→</span></button></div>}
      {!!inspectionCount && !previewMetrics && <p className="inspect-state"><span>Inspecting {inspectionCount} elements:</span> {inspectable.slice(0, inspectionCount).map((element) => `“${element.label}”`).join(", ")}</p>}
      {previewBlocked && !previewMetrics && <p className="preview-warning">Humanize found two equally prominent actions. It will not choose one for you—inspect the candidates and make the decision on the page.</p>}
      {previewMetrics && <><div className="comparison"><div><span>Before</span><strong>{evidence.metrics.primaryActionProminence}</strong></div><div><span>Preview</span><strong>{previewMetrics.primaryActionProminence}</strong></div><div><span>Site mutations</span><strong>0</strong></div></div><p className="scope-note">The score is a visual prominence proxy. Humanize has not changed page content, behavior, or conversion.</p><button className="secondary-button full" onClick={revert} disabled={busy}>{busy ? "Reverting…" : "Revert preview"}</button></>}
    </section>
  </>;
}
