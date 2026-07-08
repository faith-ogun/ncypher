import data from "../data/ncypher.json";

export type ViewId = "triage" | "finding" | "validation";

const NAV: { id: ViewId; label: string; sub: string; icon: JSX.Element }[] = [
  {
    id: "triage",
    label: "Variant triage",
    sub: "The rich, honest card",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-[18px] w-[18px]">
        <path
          d="M4 7h16M4 12h10M4 17h7"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <circle cx="18" cy="16" r="3" stroke="currentColor" strokeWidth="1.8" />
        <path d="m20.5 18.5 1.5 1.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: "finding",
    label: "The finding",
    sub: "Convergence beats one scorer",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-[18px] w-[18px]">
        <path d="M4 20V4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <rect x="7" y="12" width="3.2" height="6" rx="1" fill="currentColor" opacity="0.55" />
        <rect x="12" y="7" width="3.2" height="11" rx="1" fill="currentColor" />
        <rect x="17" y="14" width="3.2" height="4" rx="1" fill="currentColor" opacity="0.55" />
      </svg>
    ),
  },
  {
    id: "validation",
    label: "Validation",
    sub: "Right cell context, honestly",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-[18px] w-[18px]">
        <path
          d="M12 3 4 6v5c0 4.5 3.2 7.9 8 9 4.8-1.1 8-4.5 8-9V6l-8-3Z"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinejoin="round"
        />
        <path d="m9 12 2 2 4-4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

export function Sidebar({
  view,
  setView,
}: {
  view: ViewId;
  setView: (v: ViewId) => void;
}) {
  const c = data.cohort;
  return (
    <aside className="flex w-[264px] shrink-0 flex-col border-r border-line bg-panel">
      {/* Brand: the NCypher logo lockup on a white card. The logo carries the
          wordmark and tagline, so it replaces the old text wordmark. */}
      <div className="px-5 pb-5 pt-5">
        <div className="rounded-xl border border-line bg-white p-2.5 shadow-card">
          <img
            src="/logo_upscaled.png"
            alt="NCypher, decode the non-coding"
            className="block w-full"
          />
        </div>
      </div>

      <div className="mx-6 mb-4 h-px bg-line" />

      {/* Nav */}
      <nav className="flex flex-col gap-1 px-3">
        {NAV.map((n) => {
          const active = view === n.id;
          return (
            <button
              key={n.id}
              onClick={() => setView(n.id)}
              className={`group flex items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-colors ${
                active ? "bg-brand-50" : "hover:bg-page"
              }`}
            >
              <span
                className={`mt-0.5 ${active ? "text-brand-600" : "text-faint group-hover:text-muted"}`}
              >
                {n.icon}
              </span>
              <span className="min-w-0">
                <span
                  className={`block text-[14px] font-semibold ${
                    active ? "text-brand-700" : "text-ink"
                  }`}
                >
                  {n.label}
                </span>
                <span className="block text-[11.5px] leading-tight text-muted">{n.sub}</span>
              </span>
            </button>
          );
        })}
      </nav>

      <div className="mx-6 my-4 h-px bg-line" />

      {/* Cohort snapshot */}
      <div className="px-6">
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-faint">
          Discovery sweep
        </div>
        <dl className="mt-3 space-y-2 text-[12.5px]">
          <SnapRow k="Variants scored" v={c.n_scored.toLocaleString("en-GB")} />
          <SnapRow k="Chromatin high-impact" v={c.n_high_impact.toLocaleString("en-GB")} />
          <SnapRow k="Constrained" v={c.n_constrained.toLocaleString("en-GB")} />
          <SnapRow k="Converged (both)" v={String(c.n_converged)} strong />
          <SnapRow k="Patients" v={String(c.n_patients)} />
        </dl>
      </div>

      <div className="mt-auto px-6 pb-5 pt-6">
        <div className="rounded-lg border border-line bg-white px-3 py-2.5 text-[11px] leading-snug text-muted">
          Model context{" "}
          <span className="font-mono text-[10.5px] text-ink">trevino_2021.c15</span> · fetal-OPC
          ChromBPNet · GRCh38. Hypothesis-generating triage, not proven drivers.
        </div>
      </div>
    </aside>
  );
}

function SnapRow({ k, v, strong = false }: { k: string; v: string; strong?: boolean }) {
  return (
    <div className="flex items-baseline justify-between gap-2">
      <dt className="text-muted">{k}</dt>
      <dd
        className={`font-mono tnum ${
          strong ? "text-[14px] font-bold text-brand-600" : "text-[13px] font-semibold text-ink"
        }`}
      >
        {v}
      </dd>
    </div>
  );
}
