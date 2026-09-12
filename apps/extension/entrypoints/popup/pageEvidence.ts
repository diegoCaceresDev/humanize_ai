export type PageContext = {
  url: string;
  title: string;
  description: string;
  language: string;
  headings: { level: string; text: string }[];
  calls_to_action: string[];
  forms: { action: string; fields: string[] }[];
  images: { src: string; alt: string; width: number; height: number }[];
  links: { text: string; href: string }[];
  visible_text: string;
  html_snapshot: string;
};

export type ElementRole = "primary-cta" | "competing-cta";

export type ElementEvidence = {
  id: string;
  role: ElementRole;
  label: string;
  locator: string;
  bounds: { x: number; y: number; width: number; height: number };
  viewportVisible: boolean;
  prominence: number;
  fingerprint: string;
  classificationReason: "native-button" | "button-input" | "role-button" | "action-link-keyword";
  scoreComponents: { base: number; actionVerb: number; position: number; area: number; firstViewport: number; previewState: number };
};

export type HeadingEvidence = {
  id: string;
  level: string;
  label: string;
  bounds: { x: number; y: number; width: number; height: number };
  viewportVisible: boolean;
};

export type PageMetrics = {
  visibleCtaCount: number;
  heroCtaCount: number;
  missingAltCount: number;
  unlabeledFormFieldCount: number;
  primaryActionProminence: number;
  primaryCtaLabel: string;
  method: "browser-structural-v1";
};

export type BrowserEvidence = {
  engineVersion: "deterministic-evidence-v1";
  elements: ElementEvidence[];
  headings: HeadingEvidence[];
  metrics: PageMetrics;
  ranking: { primaryCtaId: string | null; competingCtaIds: string[]; ambiguousPrimary: boolean; method: "cta-prominence-v1" };
  diagnostics: { code: string; message: string; evidenceIds: string[] }[];
};

export type CapturedPage = {
  context: PageContext;
  evidence: BrowserEvidence;
};

/**
 * This function is intentionally self-contained because Chrome serializes it
 * into the inspected page through chrome.scripting.executeScript.
 */
export function collectPageEvidence(): CapturedPage {
  const hash = (value: string) => {
    let result = 2_166_136_261;
    for (let index = 0; index < value.length; index += 1) result = Math.imul(result ^ value.charCodeAt(index), 16_777_619);
    return `v1-${(result >>> 0).toString(16).padStart(8, "0")}`;
  };
  const isVisible = (element: Element) => {
    const style = window.getComputedStyle(element);
    const box = element.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity || "1") > 0 && box.width > 0 && box.height > 0;
  };
  const text = (element: Element) => (element.textContent || "").replace(/\s+/g, " ").trim();
  const elementLabel = (element: Element) => {
    if (element instanceof HTMLInputElement) return element.value || element.getAttribute("aria-label") || element.name || element.type;
    return text(element) || element.getAttribute("aria-label") || element.getAttribute("title") || element.tagName.toLowerCase();
  };
  const locator = (element: Element) => {
    const parts: string[] = [];
    let current: Element | null = element;
    while (current && current !== document.body && parts.length < 7) {
      const tag = current.tagName.toLowerCase();
      const siblings = current.parentElement ? Array.from(current.parentElement.children).filter((child) => child.tagName === current!.tagName) : [];
      const index = Math.max(1, siblings.indexOf(current) + 1);
      parts.unshift(`${tag}:nth-of-type(${index})`);
      current = current.parentElement;
    }
    return `body > ${parts.join(" > ")}`;
  };
  const isActionLikeLink = (element: Element) => {
    if (!(element instanceof HTMLAnchorElement)) return false;
    const label = elementLabel(element).toLowerCase();
    return /\b(get started|start|try|book|demo|contact|join|sign up|signup|learn more|discover|buy|shop|download|request)\b/.test(label);
  };
  const classificationReason = (element: Element) => {
    if (element instanceof HTMLButtonElement) return "native-button" as const;
    if (element instanceof HTMLInputElement) return "button-input" as const;
    if (element.getAttribute("role") === "button") return "role-button" as const;
    return "action-link-keyword" as const;
  };
  const actionElements = Array.from(document.querySelectorAll("button, input[type=submit], input[type=button], [role=button], a[href]"))
    .filter(isVisible)
    .filter((element) => !(element instanceof HTMLAnchorElement) || isActionLikeLink(element))
    .slice(0, 40);
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 1;
  const rawCtas = actionElements.map((element, index) => {
    const box = element.getBoundingClientRect();
    const label = elementLabel(element).slice(0, 160);
    const labelLower = label.toLowerCase();
    const actionVerb = /\b(get started|start|try|book|demo|contact|join|sign up|signup|buy|shop|download|request)\b/.test(labelLower) ? 16 : 0;
    const topViewportBonus = Math.max(0, 24 - Math.max(box.top, 0) / Math.max(viewportHeight, 1) * 24);
    const sizeBonus = Math.min(24, Math.sqrt(Math.max(box.width * box.height, 0)) / 10);
    const heroBonus = box.top >= 0 && box.top < viewportHeight * 0.6 ? 14 : 0;
    const previewState = element.getAttribute("data-humanize-preview");
    const previewAdjustment = previewState === "primary" ? 22 : previewState === "competing" ? -18 : 0;
    const roundedBounds = { x: Math.round(box.left), y: Math.round(box.top), width: Math.round(box.width), height: Math.round(box.height) };
    const structuralPath = locator(element);
    return {
      id: `cta-${index + 1}`,
      label,
      locator: structuralPath,
      bounds: roundedBounds,
      viewportVisible: box.bottom > 0 && box.top < viewportHeight && box.right > 0 && box.left < window.innerWidth,
      prominence: Math.max(0, Math.min(100, Math.round(28 + actionVerb + topViewportBonus + sizeBonus + heroBonus + previewAdjustment))),
      fingerprint: hash(["cta", labelLower, structuralPath, roundedBounds.x, roundedBounds.y, roundedBounds.width, roundedBounds.height].join("|")),
      classificationReason: classificationReason(element),
      scoreComponents: { base: 28, actionVerb, position: Math.round(topViewportBonus), area: Math.round(sizeBonus), firstViewport: heroBonus, previewState: previewAdjustment },
      inHero: box.top >= 0 && box.top < viewportHeight * 0.6,
    };
  });
  const rankedCtas = [...rawCtas].sort((a, b) => b.prominence - a.prominence || a.bounds.y - b.bounds.y);
  const primaryId = rankedCtas[0]?.id || "";
  const [firstRanked, secondRanked] = rankedCtas;
  const primaryDifference = firstRanked && secondRanked ? firstRanked.prominence - secondRanked.prominence : Infinity;
  const ambiguousPrimary = primaryDifference < 5;
  const elements = rawCtas.map(({ inHero: _inHero, ...cta }) => ({ ...cta, role: cta.id === primaryId ? "primary-cta" as const : "competing-cta" as const }));
  const primary = elements.find((element) => element.id === primaryId);
  const root = document.querySelector("main") || document.body;
  const snapshot = root.cloneNode(true) as HTMLElement;
  snapshot.querySelectorAll("script, style, noscript, template, svg").forEach((element) => element.remove());
  const headingEvidence = Array.from(document.querySelectorAll("h1, h2, h3"))
    .filter(isVisible)
    .map((element, index) => {
      const box = element.getBoundingClientRect();
      return {
        id: `heading-${index + 1}`,
        level: element.tagName.toLowerCase(),
        label: text(element).slice(0, 500),
        bounds: { x: Math.round(box.left), y: Math.round(box.top), width: Math.round(box.width), height: Math.round(box.height) },
        viewportVisible: box.bottom > 0 && box.top < viewportHeight && box.right > 0 && box.left < window.innerWidth,
      };
    })
    .filter((item) => item.label)
    .slice(0, 100);
  const headings = headingEvidence.map(({ level, label }) => ({ level, text: label }));
  const images = Array.from(document.images)
    .filter(isVisible)
    .map((image) => ({ src: image.currentSrc || image.src, alt: image.alt, width: image.naturalWidth || Math.round(image.getBoundingClientRect().width), height: image.naturalHeight || Math.round(image.getBoundingClientRect().height) }))
    .filter((image) => image.src)
    .slice(0, 100);
  const forms = Array.from(document.forms).filter(isVisible).slice(0, 30).map((form) => ({
    action: form.action,
    fields: Array.from(form.elements).map((field) => (field as HTMLInputElement).name || (field as HTMLInputElement).type).filter(Boolean).slice(0, 30),
  }));
  const links = Array.from(document.querySelectorAll("a[href]"))
    .filter(isVisible)
    .map((link) => ({ text: text(link), href: (link as HTMLAnchorElement).href }))
    .filter((link) => link.text)
    .slice(0, 160);
  const unlabeledFormFieldCount = Array.from(document.querySelectorAll("input:not([type=hidden]), textarea, select"))
    .filter(isVisible)
    .filter((field) => {
      const input = field as HTMLInputElement;
      return !input.labels?.length && !input.getAttribute("aria-label") && !input.getAttribute("aria-labelledby");
    }).length;

  return {
    context: {
      url: location.href,
      title: document.title,
      description: document.querySelector('meta[name="description"]')?.getAttribute("content") || "",
      language: document.documentElement.lang || "",
      headings,
      calls_to_action: rawCtas.map((cta) => cta.label),
      forms,
      images,
      links,
      visible_text: (root.innerText || "").replace(/\s+/g, " ").trim().slice(0, 50_000),
      html_snapshot: snapshot.outerHTML.slice(0, 80_000),
    },
    evidence: {
      engineVersion: "deterministic-evidence-v1",
      elements,
      headings: headingEvidence,
      metrics: {
        visibleCtaCount: elements.length,
        heroCtaCount: rawCtas.filter((cta) => cta.inHero).length,
        missingAltCount: images.filter((image) => !image.alt.trim()).length,
        unlabeledFormFieldCount,
        primaryActionProminence: primary?.prominence || 0,
        primaryCtaLabel: primary?.label || "No primary action detected",
        method: "browser-structural-v1",
      },
      ranking: { primaryCtaId: primaryId || null, competingCtaIds: elements.filter((element) => element.id !== primaryId).map((element) => element.id), ambiguousPrimary, method: "cta-prominence-v1" },
      diagnostics: ambiguousPrimary && firstRanked && secondRanked ? [{ code: "ambiguous-primary-cta", message: "The top two CTA candidates are within five prominence points. Inspect them before choosing a preview target.", evidenceIds: [firstRanked.id, secondRanked.id] }] : [],
    },
  };
}
