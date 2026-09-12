import { useState } from "react";

type Finding = {
  title: string;
  severity: "high" | "medium" | "low";
  evidence: string;
  recommendation: string;
};

type AuditResult = {
  score: number;
  score_label: string;
  summary: string;
  findings: Finding[];
  quick_wins: string[];
  research_sources?: { title: string; url: string }[];
};

type PageContext = {
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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function collectPageContext(): PageContext {
  const visible = (element: Element) => {
    const style = window.getComputedStyle(element);
    const box = element.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && box.width > 0 && box.height > 0;
  };
  const text = (element: Element) => (element.textContent || "").replace(/\s+/g, " ").trim();
  const root = document.querySelector("main") || document.body;
  const snapshot = root.cloneNode(true) as HTMLElement;
  snapshot.querySelectorAll("script, style, noscript, template, svg").forEach((element) => element.remove());
  const headings = Array.from(document.querySelectorAll("h1, h2, h3"))
    .filter(visible)
    .map((element) => ({ level: element.tagName.toLowerCase(), text: text(element) }))
    .filter((item) => item.text)
    .slice(0, 100);
  const callsToAction = Array.from(document.querySelectorAll("button, a, input[type=submit], [role=button]"))
    .filter(visible)
    .map(text)
    .filter(Boolean)
    .slice(0, 120);
  const images = Array.from(document.images)
    .filter(visible)
    .map((image) => ({
      src: image.currentSrc || image.src,
      alt: image.alt,
      width: image.naturalWidth || Math.round(image.getBoundingClientRect().width),
      height: image.naturalHeight || Math.round(image.getBoundingClientRect().height),
    }))
    .filter((image) => image.src)
    .slice(0, 100);
  const forms = Array.from(document.forms).filter(visible).slice(0, 30).map((form) => ({
    action: form.action,
    fields: Array.from(form.elements).map((field) => (field as HTMLInputElement).name || (field as HTMLInputElement).type).filter(Boolean).slice(0, 30),
  }));
  const links = Array.from(document.querySelectorAll("a[href]"))
    .filter(visible)
    .map((link) => ({ text: text(link), href: (link as HTMLAnchorElement).href }))
    .filter((link) => link.text)
    .slice(0, 160);

  return {
    url: location.href,
    title: document.title,
    description: document.querySelector('meta[name="description"]')?.getAttribute("content") || "",
    language: document.documentElement.lang || "",
    headings,
    calls_to_action: callsToAction,
    forms,
    images,
    links,
    visible_text: (root.innerText || "").replace(/\s+/g, " ").trim().slice(0, 50000),
    html_snapshot: snapshot.outerHTML.slice(0, 80000),
  };
}

async function captureCurrentPage() {
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (tab.id == null || tab.windowId == null || !tab.url || !/^https?:/i.test(tab.url)) {
    throw new Error("Open a regular HTTP(S) webpage before auditing it.");
  }
  const [{ result }] = await browser.scripting.executeScript({ target: { tabId: tab.id }, func: collectPageContext });
  const screenshot = await browser.tabs.captureVisibleTab(tab.windowId, { format: "jpeg", quality: 72 });
  return { context: result as PageContext, screenshot };
}

function ResultView({ result, onReset }: { result: AuditResult; onReset: () => void }) {
  return (
    <main className="result-shell">
      <header className="brand-row"><span className="mark">✦</span><span>HUMANIZE AI</span><button className="text-button" onClick={onReset}>New audit</button></header>
      <section className="score-card">
        <div><p className="eyebrow">Humanity score</p><strong>{result.score}</strong><span>/100</span></div>
        <div className="score-copy"><span className="pill">{result.score_label}</span><p>{result.summary}</p></div>
      </section>
      <section className="section"><div className="section-heading"><span className="eyebrow">01 / Findings</span><span className="muted">{result.findings.length} signals</span></div>
        {result.findings.map((finding, index) => <article className="finding" key={`${finding.title}-${index}`}><div className={`severity ${finding.severity}`}>{finding.severity}</div><h3>{finding.title}</h3><p className="evidence">“{finding.evidence}”</p><p>{finding.recommendation}</p></article>)}
      </section>
      <section className="section"><div className="section-heading"><span className="eyebrow">02 / Quick wins</span></div><ul className="quick-wins">{result.quick_wins.map((win, index) => <li key={index}>{win}</li>)}</ul></section>
      {!!result.research_sources?.length && <section className="section sources"><div className="section-heading"><span className="eyebrow">03 / Context</span><span className="muted">Powered by Exa</span></div>{result.research_sources.map((source) => <a href={source.url} target="_blank" rel="noreferrer" key={source.url}>{source.title}<span>↗</span></a>)}</section>}
    </main>
  );
}

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AuditResult | null>(null);

  async function audit() {
    setLoading(true); setError("");
    try {
      const captured = await captureCurrentPage();
      const response = await fetch(`${API_BASE_URL}/api/audits`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(captured) });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "The audit service could not review this page.");
      setResult(payload);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong.");
    } finally { setLoading(false); }
  }

  if (result) return <ResultView result={result} onReset={() => setResult(null)} />;
  return <main className="empty-shell"><div className="brand-row"><span className="mark">✦</span><span>HUMANIZE AI</span></div><div className="hero"><div className="orb">✦</div><p className="eyebrow">A second set of eyes for the web</p><h1>Make your page feel more human.</h1><p className="lede">Audit the page you’re looking at and get clear, evidence-based ways to make it warmer, sharper, and easier to trust.</p><button className="audit-button" onClick={audit} disabled={loading}>{loading ? <><span className="spinner" />Reading your page…</> : <>Humanize this page <span>→</span></>}</button>{error && <p className="error">{error}</p>}</div><footer>Private by design · Review only what you choose</footer></main>;
}
