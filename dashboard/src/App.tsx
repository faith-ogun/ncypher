import { useEffect, useState } from "react";
import { Sidebar, type ViewId } from "./components/Sidebar";
import { VariantTriage } from "./views/VariantTriage";
import { TheFinding } from "./views/TheFinding";
import { Validation } from "./views/Validation";
import { GUARDRAILS } from "./data/content";

const VALID: ViewId[] = ["triage", "finding", "validation"];

function viewFromHash(): ViewId {
  const h = window.location.hash.replace("#", "") as ViewId;
  return VALID.includes(h) ? h : "triage";
}

export default function App() {
  const [view, setView] = useState<ViewId>(viewFromHash());

  useEffect(() => {
    const onHash = () => setView(viewFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  function navigate(v: ViewId) {
    setView(v);
    if (window.location.hash !== `#${v}`) window.location.hash = v;
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-page text-ink">
      <Sidebar view={view} setView={navigate} />
      <main className="flex-1 overflow-y-auto">
        {view === "triage" && <VariantTriage />}
        {view === "finding" && <TheFinding />}
        {view === "validation" && <Validation />}
        <GuardrailFooter />
      </main>
    </div>
  );
}

function GuardrailFooter() {
  return (
    <footer className="mx-auto max-w-6xl px-8 pb-10">
      <div className="rounded-xl2 border border-line bg-card p-5 shadow-card">
        <div className="flex items-center gap-2">
          <svg viewBox="0 0 24 24" className="h-4 w-4 text-brand-600" fill="none">
            <path
              d="M12 3 4 6v5c0 4.5 3.2 7.9 8 9 4.8-1.1 8-4.5 8-9V6l-8-3Z"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinejoin="round"
            />
          </svg>
          <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-faint">
            Honesty guardrails · the bright-line "do not say" list
          </span>
        </div>
        <div className="mt-3 grid grid-cols-1 gap-x-8 gap-y-2 md:grid-cols-2">
          {GUARDRAILS.map((g, i) => (
            <div key={i} className="flex gap-2.5 text-[12px] leading-snug text-muted">
              <span className="mt-[3px] font-mono text-[11px] font-bold text-nogo">x</span>
              <span>{g}</span>
            </div>
          ))}
        </div>
        <div className="mt-4 border-t border-line pt-3 text-[11px] leading-snug text-faint">
          NCypher couples a chromatin score, evolutionary constraint and (where available) measured
          function into one agent-callable verdict with a mechanism and an honesty flag. It is the
          convergence layer, not a better general variant-effect predictor. Confidently wrong is
          worse than missing data.
        </div>
      </div>
    </footer>
  );
}
