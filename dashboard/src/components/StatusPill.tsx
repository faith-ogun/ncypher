import { VERDICT_META } from "../lib/format";
import type { Verdict } from "../types";

export function StatusPill({
  verdict,
  size = "md",
}: {
  verdict: Verdict;
  size?: "sm" | "md" | "lg";
}) {
  const m = VERDICT_META[verdict];
  const sizes = {
    sm: "px-3 py-1 text-[13px]",
    md: "px-4 py-1.5 text-[15px]",
    lg: "px-5 py-2 text-[18px]",
  } as const;
  const dot = { sm: 7, md: 8, lg: 10 }[size];
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full font-bold tracking-wide shadow-pill ${sizes[size]}`}
      style={{ backgroundColor: m.bg, color: m.colour, boxShadow: `inset 0 0 0 1.5px ${m.ring}33` }}
    >
      <span
        className="inline-block rounded-full"
        style={{ width: dot, height: dot, backgroundColor: m.ring }}
      />
      {m.label}
    </span>
  );
}

export function ConfidenceBadge({ tier }: { tier: string }) {
  const t = tier.toUpperCase();
  const map: Record<string, { c: string; bg: string; bd: string }> = {
    HIGH: { c: "#0600f9", bg: "#ecebfe", bd: "#bab4fd" },
    MEDIUM: { c: "#a16207", bg: "#fef9c3", bd: "#fde68a" },
    LOW: { c: "#3d4152", bg: "#f1f5f9", bd: "rgba(14,15,35,0.12)" },
  };
  const s = map[t] ?? map.LOW;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[11.5px] font-semibold uppercase tracking-wide"
      style={{ color: s.c, backgroundColor: s.bg, borderColor: s.bd }}
    >
      {t} confidence
    </span>
  );
}
