export interface HBarRow {
  label: string;
  sublabel?: string;
  value: number; // numeric for bar length
  display: string; // e.g. "2.62x" or "0.689"
  tone: "teal" | "amber" | "grey" | "red" | "blue";
  annotation?: string; // e.g. "p = 4.8e-13"
  annotationTone?: "strong" | "nominal" | "ns";
  emphasise?: boolean;
}

const BAR_TONES: Record<string, string> = {
  teal: "#0600f9",
  amber: "#eab308",
  grey: "#94a3b8",
  red: "#DA4A42",
  blue: "#0600f9",
};

const ANN_TONES: Record<string, { c: string; bg: string; bd: string }> = {
  strong: { c: "#0600f9", bg: "#ecebfe", bd: "#bab4fd" },
  nominal: { c: "#a16207", bg: "#fef9c3", bd: "#fde68a" },
  ns: { c: "#3d4152", bg: "#f1f5f9", bd: "rgba(14,15,35,0.12)" },
};

export function HBarChart({
  rows,
  max,
  baseline,
  baselineLabel,
  unit,
}: {
  rows: HBarRow[];
  max: number;
  baseline?: number; // draw a reference line (e.g. base rate, or chance)
  baselineLabel?: string;
  unit?: string;
}) {
  const pct = (v: number) => `${Math.max(0, Math.min(100, (v / max) * 100))}%`;
  return (
    <div>
      <div className="relative flex flex-col gap-3.5">
        {rows.map((r) => {
          const ann = r.annotationTone ? ANN_TONES[r.annotationTone] : null;
          return (
            <div key={r.label} className="grid grid-cols-[190px_1fr] items-center gap-4">
              <div className="min-w-0 text-right">
                <div
                  className={`truncate text-[13px] ${
                    r.emphasise ? "font-bold text-ink" : "font-semibold text-ink"
                  }`}
                >
                  {r.label}
                </div>
                {r.sublabel && (
                  <div className="truncate text-[11px] text-muted">{r.sublabel}</div>
                )}
              </div>
              <div className="relative">
                <div className="flex items-center gap-2.5">
                  <div className="relative h-7 flex-1 overflow-visible rounded-md bg-page">
                    <div
                      className="flex h-7 items-center rounded-md pl-2 transition-all"
                      style={{
                        width: pct(r.value),
                        backgroundColor: BAR_TONES[r.tone],
                        minWidth: 34,
                        boxShadow: r.emphasise ? "0 2px 8px rgba(6,0,249,0.22)" : undefined,
                      }}
                    >
                      <span className="font-mono text-[12.5px] font-bold text-white tnum">
                        {r.display}
                      </span>
                    </div>
                  </div>
                  {r.annotation && ann && (
                    <span
                      className="shrink-0 rounded-md border px-1.5 py-0.5 font-mono text-[11px] font-semibold"
                      style={{ color: ann.c, backgroundColor: ann.bg, borderColor: ann.bd }}
                    >
                      {r.annotation}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* baseline / axis */}
      {baseline !== undefined && (
        <div className="mt-3 grid grid-cols-[190px_1fr] items-center gap-4">
          <div />
          <div className="relative">
            <div
              className="absolute top-0 flex flex-col items-center"
              style={{ left: pct(baseline) }}
            >
              <div className="h-2 w-px bg-faint" />
              <span className="mt-0.5 whitespace-nowrap text-[10.5px] text-muted">
                {baselineLabel}
              </span>
            </div>
          </div>
        </div>
      )}
      {unit && (
        <div className="mt-4 grid grid-cols-[190px_1fr] gap-4">
          <div />
          <div className="text-right text-[10.5px] uppercase tracking-wide text-faint">{unit}</div>
        </div>
      )}
    </div>
  );
}
