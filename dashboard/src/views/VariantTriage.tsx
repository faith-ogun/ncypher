import { useState } from "react";
import data from "../data/ncypher.json";
import { HEROES, HERO_ORDER } from "../data/content";
import type { HeroContent, NCypherData, SweepRow, Verdict } from "../types";
import { Card, SectionLabel, Tag } from "../components/ui";
import { StatusPill, ConfidenceBadge } from "../components/StatusPill";
import { AxisTriPanel } from "../components/AxisTriPanel";
import { SaliencyView, VariantBases } from "../components/Mechanism";
import { VERDICT_META, normaliseVariantId } from "../lib/format";

const D = data as unknown as NCypherData;

type Context = "opc" | "breast";

function initialSelected(): string {
  const m = window.location.hash.match(/[?&]v=([^&]+)/);
  if (m) {
    const norm = normaliseVariantId(decodeURIComponent(m[1]));
    if (norm && D.sweep[norm]) return norm;
  }
  return HERO_ORDER[0];
}

function initialContext(): Context {
  return /[?&]ctx=breast/.test(window.location.hash) ? "breast" : "opc";
}

export function VariantTriage() {
  const [selected, setSelected] = useState<string>(initialSelected());
  const [query, setQuery] = useState("");
  const [context, setContext] = useState<Context>(initialContext());
  const [notFound, setNotFound] = useState<string | null>(null);

  const row: SweepRow | undefined = D.sweep[selected];

  function submitQuery() {
    const norm = normaliseVariantId(query);
    if (!norm) {
      setNotFound(query.trim() || "(empty)");
      return;
    }
    if (D.sweep[norm]) {
      setSelected(norm);
      setNotFound(null);
    } else {
      setSelected(norm);
      setNotFound(norm);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-8 py-8">
      <ViewHeader
        eyebrow="Variant triage"
        title="Score one non-coding variant"
        blurb="The rich, honest card the score_variant tool returns: three orthogonal axes, a convergence verdict with a calibrated confidence tier, the model-native mechanism, a skeptic check, and a go/no-go memo. Never a bare number."
      />

      {/* Picker */}
      <div className="mt-6 flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <SectionLabel>Featured variants</SectionLabel>
        </div>
        <div className="flex flex-wrap gap-2">
          {HERO_ORDER.map((k) => {
            const h = HEROES[k];
            const r = D.sweep[k];
            const active = k === selected;
            const v = r?.verdict ?? "NO-GO";
            const m = VERDICT_META[v];
            return (
              <button
                key={k}
                onClick={() => {
                  setSelected(k);
                  setNotFound(null);
                }}
                className={`group flex items-center gap-2 rounded-full border px-3 py-1.5 text-[13px] transition-all ${
                  active
                    ? "border-brand-300 bg-brand-50 shadow-pill"
                    : "border-line bg-card hover:border-lineStrong hover:bg-page"
                }`}
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: m.ring }}
                  title={v}
                />
                <span className={`font-semibold ${active ? "text-brand-700" : "text-ink"}`}>
                  {h.label}
                </span>
                <span className="hidden text-[11px] text-muted sm:inline">{kindLabel(h.kind)}</span>
              </button>
            );
          })}
        </div>

        {/* Free-form + context */}
        <div className="mt-1 flex flex-wrap items-center gap-3">
          <div className="flex flex-1 items-center gap-2 rounded-xl border border-line bg-card px-3 py-2 shadow-card sm:max-w-md">
            <svg viewBox="0 0 24 24" className="h-4 w-4 text-faint" fill="none">
              <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
              <path d="m20 20-3.2-3.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submitQuery()}
              placeholder="Type chr-pos-ref-alt, e.g. chr22-33000876-C-T"
              className="min-w-0 flex-1 bg-transparent font-mono text-[13px] text-ink outline-none placeholder:text-faint"
            />
            <button
              onClick={submitQuery}
              className="rounded-lg bg-brand-500 px-3 py-1 text-[12.5px] font-semibold text-white transition-colors hover:bg-brand-600"
            >
              Score
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11.5px] font-medium text-muted">Model context</span>
            <div className="flex rounded-xl border border-line bg-card p-0.5 shadow-card">
              <ContextTab
                active={context === "opc"}
                onClick={() => setContext("opc")}
                label="Fetal-OPC (in domain)"
              />
              <ContextTab
                active={context === "breast"}
                onClick={() => setContext("breast")}
                label="Breast (out of domain)"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Card */}
      <div className="mt-6">
        {notFound && !D.sweep[selected] ? (
          <NotInCacheCard vkey={notFound} />
        ) : row ? (
          <TriageCard row={row} context={context} />
        ) : null}
      </div>
    </div>
  );
}

function TriageCard({ row, context }: { row: SweepRow; context: Context }) {
  const hero = HEROES[row.key];
  const ood = context === "breast";
  const verdict: Verdict = ood ? "NO-GO" : row.verdict;
  const m = VERDICT_META[verdict];

  const nAvail = row.phylop !== null ? 2 : 1;
  const nImpact = (row.high_impact ? 1 : 0) + (row.constrained ? 1 : 0);
  const agreement = nAvail > 0 ? nImpact / nAvail : 0;

  const gene = row.gene ?? hero?.gene ?? "intergenic";
  const tier = row.confidence ? row.confidence : "low";

  return (
    <Card>
      {/* Header */}
      <div
        className="flex flex-col gap-4 rounded-t-xl2 border-b border-line px-6 py-5 sm:flex-row sm:items-center sm:justify-between"
        style={{ background: `linear-gradient(180deg, ${m.bg}55, transparent)` }}
      >
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-[22px] font-bold text-ink">{gene}</h2>
            {hero && <Tag tone={kindTone(hero.kind)}>{kindLabel(hero.kind)}</Tag>}
            {row.cls && <Tag>{row.cls}</Tag>}
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-3">
            <span className="font-mono text-[13.5px] font-semibold text-muted">{row.key}</span>
            <VariantBases vkey={row.key} size={15} />
            <span className="text-[12px] text-faint">
              {row.n_patients} patient{row.n_patients === 1 ? "" : "s"}
            </span>
          </div>
          {hero?.tagline && (
            <p className="mt-1.5 max-w-2xl text-[13px] text-muted">{hero.tagline}</p>
          )}
        </div>
        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          <StatusPill verdict={verdict} size="lg" />
          <div className="flex items-center gap-2">
            {ood ? (
              <span className="rounded-md border border-[#0e0f231f] bg-[#f1f5f9] px-2 py-1 text-[11.5px] font-semibold uppercase tracking-wide text-[#3d4152]">
                out of domain
              </span>
            ) : (
              <ConfidenceBadge tier={tier} />
            )}
          </div>
          <span className="text-[12px] text-muted">{m.blurb}</span>
        </div>
      </div>

      {/* OOD banner */}
      {ood && (
        <div className="border-b border-line bg-[#FBE9E8]/50 px-6 py-3 text-[13px] text-[#8a2f2a]">
          <span className="font-semibold">Out-of-domain guard.</span> This variant is being scored
          in a breast context, outside the developing-brain set the model was trained on. NCypher
          returns NO-GO by default and does not trust the score here. Re-score in a matched
          fetal-OPC model to get a real verdict. This is the honesty demo: the same variant that is
          a GO in domain is correctly refused out of domain.
        </div>
      )}

      {/* Convergence strip */}
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-b border-line bg-page/50 px-6 py-3">
        <Metric k="Axes available" v={`${nAvail} of 3`} />
        <Metric k="Axes impactful" v={`${nImpact} of ${nAvail}`} />
        <Metric
          k="Agreement"
          v={`${Math.round(agreement * 100)}%`}
          tone={agreement >= 0.66 ? "teal" : agreement >= 0.5 ? "amber" : "grey"}
        />
        <Metric k="In domain" v={ood ? "no" : "yes"} tone={ood ? "red" : "teal"} />
        <Metric k="Converged (2-axis)" v={row.converged ? "yes" : "no"} tone={row.converged ? "teal" : "grey"} />
      </div>

      {/* Axes */}
      <div className="px-6 py-5">
        <SectionLabel>The three orthogonal axes</SectionLabel>
        <div className="mt-3">
          <AxisTriPanel row={row} />
        </div>
      </div>

      {/* Mechanism + saliency */}
      {hero && (hero.saliencyKind !== "none" || hero.mechanism) && (
        <div className="grid grid-cols-1 gap-6 border-t border-line px-6 py-5 lg:grid-cols-2">
          <div>
            <SectionLabel>Mechanism</SectionLabel>
            <p className="mt-2 text-[14px] leading-relaxed text-ink">{hero.mechanism}</p>
            {hero.motifClaim && (
              <div className="mt-3">
                <Tag tone="teal">
                  <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none">
                    <path d="M4 12s3-7 8-7 8 7 8 7-3 7-8 7-8-7-8-7Z" stroke="currentColor" strokeWidth="1.6" />
                    <circle cx="12" cy="12" r="2.5" fill="currentColor" />
                  </svg>
                  {hero.motifClaim}
                </Tag>
              </div>
            )}
            <div className="mt-4 rounded-lg border border-line bg-page/60 px-3.5 py-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-faint">
                What drives the call
              </div>
              <p className="mt-1 text-[12.5px] leading-snug text-muted">{hero.driverAxis}</p>
            </div>
          </div>
          <div>
            <SectionLabel>
              {hero.saliencyKind === "deepshap"
                ? "Ref vs alt saliency logo"
                : hero.saliencyKind === "gain"
                ? "Accessibility gain"
                : "Contribution collapse"}
            </SectionLabel>
            <div className="mt-2">
              <SaliencyView hero={hero} row={row} />
            </div>
          </div>
        </div>
      )}

      {/* Skeptic check */}
      {hero?.skeptic && hero.skeptic.length > 0 && (
        <div className="border-t border-line bg-[#fefce8]/60 px-6 py-5">
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 24 24" className="h-4 w-4 text-[#a16207]" fill="none">
              <path d="M12 3 2 20h20L12 3Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
              <path d="M12 10v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="currentColor" />
            </svg>
            <SectionLabel>Skeptic check (falsification)</SectionLabel>
          </div>
          <ul className="mt-3 space-y-2">
            {hero.skeptic.map((s, i) => (
              <li key={i} className="flex gap-2.5 text-[13px] leading-snug text-ink/90">
                <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-hold" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Memo */}
      <div className="border-t border-line px-6 py-5">
        {ood ? (
          <MemoRefused />
        ) : hero?.memo && verdict === "GO" ? (
          <GoMemo hero={hero} />
        ) : hero?.holdNote ? (
          <HoldMemo verdict={verdict} note={hero.holdNote} />
        ) : (
          <HoldMemo
            verdict={verdict}
            note="No promoted memo: this call does not clear the convergence bar for a GO."
          />
        )}
      </div>

      {/* Provenance footer */}
      <div className="rounded-b-xl2 border-t border-line bg-page/60 px-6 py-3 text-[11px] leading-snug text-muted">
        Model {D.provenance.model}. Constraint: {D.provenance.constraint_track}, constrained at
        phyloP {"≥"} {D.provenance.constraint_threshold}. Chromatin high-impact at |log2FC|{" "}
        {"≥"} {D.provenance.chromatin_hi_threshold} ({D.provenance.chromatin_hi_note}). Genome{" "}
        {D.provenance.genome}.
      </div>
    </Card>
  );
}

function GoMemo({ hero }: { hero: HeroContent }) {
  const memo = hero.memo!;
  return (
    <div>
      <div className="flex items-center gap-2">
        <span className="rounded-md bg-brand-50 px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-brand-700">
          Go / no-go memo
        </span>
        <span className="text-[12px] text-muted">the decision, not just the score</span>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
        <MemoCell n="1" title="Validate first" body={memo.validateFirst} tone="teal" />
        <MemoCell n="2" title="Decisive experiment" body={memo.decisiveExperiment} tone="blue" />
        <MemoCell n="3" title="Kill criterion" body={memo.killCriterion} tone="red" />
        <MemoCell
          n="4"
          title={`Therapy angle · axis ${memo.therapyAxis ?? ""}`}
          body={memo.therapyAngle}
          tone="amber"
          footer={memo.therapyConfidence}
        />
      </div>
    </div>
  );
}

function MemoCell({
  n,
  title,
  body,
  tone,
  footer,
}: {
  n: string;
  title: string;
  body: string;
  tone: "teal" | "blue" | "red" | "amber";
  footer?: string;
}) {
  const tones: Record<string, string> = {
    teal: "border-l-brand-400",
    blue: "border-l-[#0600f9]",
    red: "border-l-nogo",
    amber: "border-l-hold",
  };
  return (
    <div className={`rounded-lg border border-line border-l-[3px] bg-card px-4 py-3 ${tones[tone]}`}>
      <div className="flex items-center gap-2">
        <span className="font-mono text-[12px] font-bold text-faint">{n}</span>
        <span className="text-[12.5px] font-bold uppercase tracking-wide text-ink">{title}</span>
      </div>
      <p className="mt-1.5 text-[13px] leading-snug text-ink/90">{body}</p>
      {footer && (
        <p className="mt-2 border-t border-line pt-2 text-[11.5px] italic text-muted">{footer}</p>
      )}
    </div>
  );
}

function HoldMemo({ verdict, note }: { verdict: Verdict; note: string }) {
  const m = VERDICT_META[verdict];
  return (
    <div className="rounded-lg border border-line px-4 py-3" style={{ backgroundColor: m.bg + "55" }}>
      <div className="flex items-center gap-2">
        <StatusPill verdict={verdict} size="sm" />
        <span className="text-[12.5px] font-semibold text-ink">
          {verdict === "HOLD" ? "Resolve before bench time" : "Not promoted"}
        </span>
      </div>
      <p className="mt-2 text-[13px] leading-relaxed text-ink/90">{note}</p>
    </div>
  );
}

function MemoRefused() {
  return (
    <div className="rounded-lg border border-line bg-[#FBE9E8]/40 px-4 py-3">
      <div className="flex items-center gap-2">
        <StatusPill verdict="NO-GO" size="sm" />
        <span className="text-[12.5px] font-semibold text-ink">No memo issued out of domain</span>
      </div>
      <p className="mt-2 text-[13px] leading-relaxed text-ink/90">
        NCypher does not write a go/no-go memo for an out-of-domain score. Re-score the variant in a
        matched developing-brain context, then a verdict and memo can be issued.
      </p>
    </div>
  );
}

function NotInCacheCard({ vkey }: { vkey: string }) {
  const norm = normaliseVariantId(vkey);
  return (
    <Card>
      <div className="px-6 py-6">
        <div className="flex items-center gap-3">
          <StatusPill verdict="HOLD" size="md" />
          <div>
            <div className="font-mono text-[15px] font-semibold text-ink">{norm ?? vkey}</div>
            <div className="text-[12px] text-muted">not in the DMG discovery cache</div>
          </div>
        </div>
        <p className="mt-4 max-w-2xl text-[13.5px] leading-relaxed text-ink/90">
          {norm
            ? "This variant is not in the pre-computed discovery sweep, so the chromatin axis is not yet scored. NCypher does not issue a convergence verdict without the chromatin axis, and it never promotes on a single axis."
            : "That does not parse as a variant. Use chr-pos-ref-alt, for example chr22-33000876-C-T."}
        </p>
        {norm && (
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <MiniAxis title="Chromatin (axis 2)" body="Needs scoring on the Corces c15 fetal-OPC ChromBPNet before a verdict." tone="grey" />
            <MiniAxis title="Constraint (axis 3)" body="Would be queried live from Zoonomia phyloP." tone="grey" />
            <MiniAxis title="Function (axis 1)" body="Not in the MPRA / DAV set." tone="grey" />
          </div>
        )}
        <p className="mt-4 text-[12px] text-muted">
          Try a featured variant above, or one of the 164 converged hits (for example
          chr13-98333680-C-G).
        </p>
      </div>
    </Card>
  );
}

function MiniAxis({ title, body }: { title: string; body: string; tone: string }) {
  return (
    <div className="rounded-lg border border-line bg-page/60 px-3.5 py-3">
      <div className="text-[12.5px] font-semibold text-ink">{title}</div>
      <p className="mt-1 text-[12px] leading-snug text-muted">{body}</p>
    </div>
  );
}

// ---- small helpers --------------------------------------------------------

function Metric({
  k,
  v,
  tone = "ink",
}: {
  k: string;
  v: string;
  tone?: "ink" | "teal" | "amber" | "grey" | "red";
}) {
  const tones: Record<string, string> = {
    ink: "text-ink",
    teal: "text-brand-600",
    amber: "text-[#a16207]",
    grey: "text-muted",
    red: "text-nogo",
  };
  return (
    <div className="flex items-baseline gap-1.5">
      <span className="text-[11.5px] text-muted">{k}</span>
      <span className={`font-mono text-[13px] font-bold tnum ${tones[tone]}`}>{v}</span>
    </div>
  );
}

function ContextTab({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-3 py-1.5 text-[12px] font-semibold transition-colors ${
        active ? "bg-brand-500 text-white shadow-pill" : "text-muted hover:text-ink"
      }`}
    >
      {label}
    </button>
  );
}

export function ViewHeader({
  eyebrow,
  title,
  blurb,
}: {
  eyebrow: string;
  title: string;
  blurb: string;
}) {
  return (
    <div>
      <div className="text-[12px] font-semibold uppercase tracking-[0.14em] text-brand-600">
        {eyebrow}
      </div>
      <h1 className="mt-1.5 text-[27px] font-bold leading-tight text-ink">{title}</h1>
      <p className="mt-2 max-w-3xl text-[14px] leading-relaxed text-muted">{blurb}</p>
    </div>
  );
}

function kindLabel(kind: string): string {
  return (
    {
      lead: "Lead candidate",
      converged: "Converged GO",
      control: "Positive control",
      hold: "Informative HOLD",
      nogo: "Honest NO-GO",
    } as Record<string, string>
  )[kind] ?? kind;
}

function kindTone(kind: string): "teal" | "amber" | "red" | "blue" | "neutral" {
  return (
    {
      lead: "teal",
      converged: "teal",
      control: "blue",
      hold: "amber",
      nogo: "red",
    } as Record<string, "teal" | "amber" | "red" | "blue" | "neutral">
  )[kind] ?? "neutral";
}
