import type { SweepRow } from "../types";
import { fmtSigned, fmtNum } from "../lib/format";
import data from "../data/ncypher.json";

/** The three orthogonal axes, as the MCP score_variant returns them. */
export function AxisTriPanel({ row }: { row: SweepRow }) {
  const HI = data.thresholds.chromatin_hi;
  const CON = data.thresholds.constraint;

  const chromImpact = row.high_impact;
  const conImpact = row.constrained;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <AxisTile
        n="Axis 2"
        title="Chromatin accessibility"
        model="ChromBPNet fetal-OPC"
        available
        impactful={chromImpact}
        metric={fmtSigned(row.logfc, 3)}
        metricLabel="log2FC"
        note={
          row.direction === "gain"
            ? "accessibility gain (opening)"
            : row.direction === "loss"
            ? "accessibility loss (closing)"
            : "no change"
        }
        threshold={`high-impact at |log2FC| >= ${HI}`}
      />
      <AxisTile
        n="Axis 3"
        title="Evolutionary constraint"
        model="Zoonomia phyloP (241 mammals)"
        available={row.phylop !== null}
        impactful={conImpact}
        metric={fmtNum(row.phylop, 2)}
        metricLabel="phyloP"
        note={conImpact ? "constrained (purifying selection)" : "not constrained"}
        threshold={`constrained at phyloP >= ${CON}`}
      />
      <AxisTile
        n="Axis 1"
        title="Measured function"
        model="lentiMPRA (Pollard)"
        available={false}
        impactful={null}
        metric="n/a"
        metricLabel="allelic effect"
        note="not in the MPRA / DAV set for this somatic variant"
        threshold="orthogonal: accessibility is not reporter activity"
      />
    </div>
  );
}

function AxisTile({
  n,
  title,
  model,
  available,
  impactful,
  metric,
  metricLabel,
  note,
  threshold,
}: {
  n: string;
  title: string;
  model: string;
  available: boolean;
  impactful: boolean | null;
  metric: string;
  metricLabel: string;
  note: string;
  threshold: string;
}) {
  const status = !available
    ? { label: "not available", c: "#64748b", bg: "#f1f5f9", dot: "#94a3b8", bd: "rgba(14,15,35,0.12)" }
    : impactful
    ? { label: "impactful", c: "#0600f9", bg: "#ecebfe", dot: "#0600f9", bd: "#bab4fd" }
    : { label: "below threshold", c: "#3d4152", bg: "#f1f5f9", dot: "#64748b", bd: "rgba(14,15,35,0.12)" };

  return (
    <div
      className={`flex flex-col rounded-xl border p-3.5 ${
        available && impactful ? "border-brand-200 bg-brand-50/40" : "border-line bg-page/60"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-[10.5px] font-semibold uppercase tracking-[0.12em] text-faint">
          {n}
        </span>
        <span
          className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10.5px] font-semibold"
          style={{ color: status.c, backgroundColor: status.bg, borderColor: status.bd }}
        >
          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: status.dot }} />
          {status.label}
        </span>
      </div>
      <div className="mt-1.5 text-[13.5px] font-semibold text-ink">{title}</div>
      <div className="text-[11px] text-muted">{model}</div>

      <div className="mt-3 flex items-baseline gap-2">
        <span
          className={`font-mono text-[22px] font-bold tnum ${
            available ? "text-ink" : "text-faint"
          }`}
        >
          {metric}
        </span>
        <span className="text-[11px] font-medium text-muted">{metricLabel}</span>
      </div>
      <div className="mt-0.5 text-[12px] leading-snug text-ink/80">{note}</div>
      <div className="mt-auto pt-2.5 text-[10.5px] leading-snug text-faint">{threshold}</div>
    </div>
  );
}
