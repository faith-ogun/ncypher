import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl2 border border-line bg-card shadow-card ${className}`}
    >
      {children}
    </div>
  );
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-faint">
      {children}
    </div>
  );
}

export function Kbd({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-md border border-line bg-page px-1.5 py-0.5 font-mono text-[12px] text-muted">
      {children}
    </span>
  );
}

export function Tag({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "teal" | "amber" | "red" | "green" | "blue";
}) {
  const tones: Record<string, string> = {
    neutral: "bg-page text-muted border-line",
    teal: "bg-teal-50 text-teal-700 border-teal-200",
    amber: "bg-[#FBF0DE] text-[#8A560B] border-[#EBD3A6]",
    red: "bg-[#FBE9E8] text-[#A32E28] border-[#F0C8C5]",
    green: "bg-[#E9F6EC] text-[#256E33] border-[#C3E4CB]",
    blue: "bg-[#E8F0FD] text-[#23509E] border-[#C6D8F6]",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[12px] font-medium ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export function Stat({
  value,
  label,
  sub,
  tone = "ink",
}: {
  value: ReactNode;
  label: ReactNode;
  sub?: ReactNode;
  tone?: "ink" | "teal" | "red" | "amber";
}) {
  const tones: Record<string, string> = {
    ink: "text-ink",
    teal: "text-teal-600",
    red: "text-nogo",
    amber: "text-hold",
  };
  return (
    <div>
      <div className={`font-mono text-[26px] font-semibold leading-none tnum ${tones[tone]}`}>
        {value}
      </div>
      <div className="mt-1.5 text-[12.5px] font-medium text-ink">{label}</div>
      {sub && <div className="mt-0.5 text-[12px] leading-snug text-muted">{sub}</div>}
    </div>
  );
}

export function Divider() {
  return <div className="h-px w-full bg-line" />;
}
