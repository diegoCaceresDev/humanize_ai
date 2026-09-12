import type { ElementEvidence } from "./pageEvidence";

export type PreviewResult = { applied: number; primaryFound: boolean };

/** Functions in this file are serialized into the inspected page. Keep them self-contained. */
export function inspectElements(elements: ElementEvidence[]): number {
  document.getElementById("humanize-evidence-style")?.remove();
  document.querySelectorAll("[data-humanize-evidence]").forEach((element) => element.removeAttribute("data-humanize-evidence"));
  const style = document.createElement("style");
  style.id = "humanize-evidence-style";
  style.textContent = `
    [data-humanize-evidence] { outline: 2px solid #c8f36b !important; outline-offset: 4px !important; position: relative !important; }
    [data-humanize-evidence="primary-cta"] { outline-color: #7357ff !important; box-shadow: 0 0 0 5px rgba(115, 87, 255, .18) !important; }
  `;
  document.documentElement.append(style);
  const matchesEvidence = (element: Element, label: string) => {
    const visibleLabel = element instanceof HTMLInputElement ? element.value || element.getAttribute("aria-label") || "" : element.textContent || element.getAttribute("aria-label") || "";
    return visibleLabel.replace(/\s+/g, " ").trim().includes(label.slice(0, 32));
  };
  let found = 0;
  elements.forEach((evidence) => {
    try {
      const element = document.querySelector(evidence.locator);
      if (element && matchesEvidence(element, evidence.label)) {
        element.setAttribute("data-humanize-evidence", evidence.role);
        found += 1;
      }
    } catch {
      // A stale or malformed locator should never affect the inspected page.
    }
  });
  return found;
}

export function clearInspection(): void {
  document.getElementById("humanize-evidence-style")?.remove();
  document.querySelectorAll("[data-humanize-evidence]").forEach((element) => element.removeAttribute("data-humanize-evidence"));
}

export function applyFocusPreview(primary: ElementEvidence, competitors: ElementEvidence[]): PreviewResult {
  document.getElementById("humanize-focus-preview")?.remove();
  document.querySelectorAll("[data-humanize-preview]").forEach((element) => element.removeAttribute("data-humanize-preview"));
  const style = document.createElement("style");
  style.id = "humanize-focus-preview";
  style.textContent = `
    [data-humanize-preview="primary"] { outline: 3px solid #c8f36b !important; outline-offset: 5px !important; box-shadow: 0 0 0 7px rgba(115, 87, 255, .28) !important; }
    [data-humanize-preview="competing"] { opacity: .42 !important; filter: saturate(.55) !important; }
  `;
  document.documentElement.append(style);
  const matchesEvidence = (element: Element, label: string) => {
    const visibleLabel = element instanceof HTMLInputElement ? element.value || element.getAttribute("aria-label") || "" : element.textContent || element.getAttribute("aria-label") || "";
    return visibleLabel.replace(/\s+/g, " ").trim().includes(label.slice(0, 32));
  };
  let primaryFound = false;
  const mark = (evidence: ElementEvidence, state: "primary" | "competing") => {
    try {
      const element = document.querySelector(evidence.locator);
      if (!element || !matchesEvidence(element, evidence.label)) return false;
      element.setAttribute("data-humanize-preview", state);
      return true;
    } catch {
      return false;
    }
  };
  primaryFound = mark(primary, "primary");
  const applied = competitors.slice(0, 5).filter((competitor) => mark(competitor, "competing")).length + Number(primaryFound);
  if (!primaryFound) style.remove();
  return { applied, primaryFound };
}

export function revertFocusPreview(): void {
  document.getElementById("humanize-focus-preview")?.remove();
  document.querySelectorAll("[data-humanize-preview]").forEach((element) => element.removeAttribute("data-humanize-preview"));
}
