import data from "../data/ncypher.json";
import type { CaqtlRow, NCypherData } from "../types";
import { Card, SectionLabel, Tag } from "../components/ui";
import { HBarChart, type HBarRow } from "../components/HBarChart";
import { ViewHeader } from "./VariantTriage";
import { fmtP, fmtNum } from "../lib/format";

const D = data as unknown as NCypherData;

function matched(set: string) {
  return set.toLowerCase().includes("progenitor");
}
function mismatched(set: string) {
  return set.toLowerCase().includes("psychencode");
}

export function Validation() {
  const rows = D.validation.caqtl;
  const mpra = D.validation.mpra;
  const mbr = D.validation.motifbreakr;

  const bars: HBarRow[] = rows.map((r: CaqtlRow) => ({
    label: r.set.replace(/\s*\(.*\)/, ""),
    sublabel: `${paren(r.set)} · n = ${r.n_pos} · AUROC ${fmtNum(r.auroc, 3)}`,
    value: r.fold,
    display: `${fmtNum(r.fold, 1)}x`,
    tone: mismatched(r.set) ? "grey" : "teal",
    annotation: `p = ${fmtP(r.mwu_p)}`,
    annotationTone: r.mwu_p < 0.01 ? "strong" : r.mwu_p < 0.1 ? "nominal" : "ns",
    emphasise: matched(r.set),
  }));

  return (
    <div className="mx-auto max-w-6xl px-8 py-8">
      <ViewHeader
        eyebrow="Validation"
        title="The right cell context, proven and stated honestly"
        blurb="The chromatin axis is validated on its native ground truth (allelic chromatin-accessibility QTLs), and it recovers them in a cell-type-specific way that matches its training context. This is the quantitative proof of the context USP, and it comes with an honest note on the axis where the model should not be used."
      />

      {/* caQTL context-specificity */}
      <Card className="mt-6 p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <SectionLabel>caQTL recovery by cell context</SectionLabel>
            <p className="mt-1.5 max-w-2xl text-[13.5px] leading-relaxed text-muted">
              Predicted |log2FC| ranking allelic caQTLs, fold enrichment over the base rate. The c15
              model is a fetal-OPC/progenitor context, so it should recover progenitor caQTLs best
              and fail on a mismatched set. It does exactly that.
            </p>
          </div>
          <div className="rounded-xl bg-teal-50 px-4 py-2.5 text-center">
            <div className="font-mono text-[24px] font-bold text-teal-600 tnum">7.5x</div>
            <div className="text-[11px] font-medium text-teal-700">matched context</div>
          </div>
        </div>

        <div className="mt-6">
          <HBarChart rows={bars} max={8} baseline={1.0} baselineLabel="chance (1.0x)" unit="fold vs base rate" />
        </div>

        {/* metrics table */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full border-collapse text-[12.5px]">
            <thead>
              <tr className="border-b border-line text-left text-[11px] uppercase tracking-wide text-faint">
                <th className="py-2 pr-3 font-semibold">Ground truth</th>
                <th className="py-2 pr-3 text-right font-semibold">n</th>
                <th className="py-2 pr-3 text-right font-semibold">AUPRC</th>
                <th className="py-2 pr-3 text-right font-semibold">fold</th>
                <th className="py-2 pr-3 text-right font-semibold">AUROC</th>
                <th className="py-2 pr-3 text-right font-semibold">MWU p</th>
                <th className="py-2 font-semibold">context</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.set} className={`border-b border-line/70 ${matched(r.set) ? "bg-teal-50/40" : ""}`}>
                  <td className="py-2 pr-3 font-medium text-ink">{r.set.replace(/\s*\(.*\)/, "")}</td>
                  <td className="py-2 pr-3 text-right font-mono tnum text-ink">{r.n_pos}</td>
                  <td className="py-2 pr-3 text-right font-mono tnum text-ink">{fmtNum(r.auprc, 3)}</td>
                  <td className="py-2 pr-3 text-right font-mono tnum font-semibold text-ink">
                    {fmtNum(r.fold, 1)}x
                  </td>
                  <td className="py-2 pr-3 text-right font-mono tnum text-ink">{fmtNum(r.auroc, 3)}</td>
                  <td className="py-2 pr-3 text-right font-mono tnum text-muted">{fmtP(r.mwu_p)}</td>
                  <td className="py-2">
                    {matched(r.set) ? (
                      <Tag tone="teal">matched</Tag>
                    ) : mismatched(r.set) ? (
                      <Tag tone="red">mismatched, n.s.</Tag>
                    ) : (
                      <Tag>brain</Tag>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-4 rounded-lg border border-line bg-teal-50/50 px-4 py-3 text-[12.5px] leading-snug text-ink/90">
          <span className="font-semibold text-teal-700">The USP, quantified.</span> The model is not
          generically good, it is good in its matched context: progenitor caQTLs at AUROC 0.689 and
          7.5x the base rate, weaker for neuron, and null for the mismatched PsychENCODE set (AUROC
          0.449, below chance). That is why context is a first-class part of every verdict.
        </p>
      </Card>

      {/* Two honesty panels */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* MPRA honest negative */}
        <Card className="overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-[#FBF6EE]/70 px-6 py-3.5">
            <svg viewBox="0 0 24 24" className="h-4 w-4 text-hold" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
              <path d="M12 8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="12" cy="16" r="0.6" fill="currentColor" stroke="currentColor" />
            </svg>
            <span className="text-[13px] font-bold text-ink">The honest negative: MPRA activity</span>
          </div>
          <div className="px-6 py-5">
            <p className="text-[13.5px] leading-relaxed text-ink/90">
              The chromatin model does NOT recover the {mpra.n_davs} MPRA differential-activity
              variants, and we say so.
            </p>
            <div className="mt-4 grid grid-cols-3 gap-3">
              <MiniStat value={fmtNum(mpra.auprc, 3)} label="AUPRC" sub={`${mpra.auprc_vs_base}x base = chance`} />
              <MiniStat value={fmtNum(mpra.auroc, 3)} label="AUROC" sub="≈ chance" />
              <MiniStat value={fmtNum(mpra.pearson_r, 3)} label="Pearson r" sub="effect size" />
            </div>
            <p className="mt-4 text-[12.5px] leading-snug text-muted">
              Why, and why it is expected: ChromBPNet predicts chromatin <em>accessibility</em>; MPRA
              measures episomal reporter <em>activity</em>. Different molecular modalities. Pollard
              trained a separate CNN-BiLSTM on the MPRA (r ~ 0.82) precisely because activity is not
              predictable from an accessibility model. So MPRA is the wrong ground truth for this
              axis, and the negative is not a bug.
            </p>
            <div className="mt-4 rounded-lg border border-[#F0C8C5] bg-[#FBE9E8]/50 px-3.5 py-2.5 text-[12px] leading-snug text-ink/90">
              <span className="font-semibold text-nogo">Retired claim.</span> We do not say NCypher
              beats motifbreakR on the {mbr.total} DAVs (motifbreakR caught {mbr.caught}/{mbr.total} ={" "}
              {mbr.pct}%). That headline was wrong for a chromatin model and we dropped it.
            </div>
          </div>
        </Card>

        {/* Orthogonality */}
        <Card className="overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-teal-50/50 px-6 py-3.5">
            <svg viewBox="0 0 24 24" className="h-4 w-4 text-teal-600" fill="none">
              <path d="M5 19V5M5 19h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              <path d="M5 19 19 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeDasharray="2 2.5" />
            </svg>
            <span className="text-[13px] font-bold text-ink">Why three axes, orthogonal by design</span>
          </div>
          <div className="px-6 py-5">
            <p className="text-[13.5px] leading-relaxed text-ink/90">
              Chromatin accessibility (caQTL), reporter activity (MPRA) and evolutionary constraint
              capture different facets. No single axis is a universal functional-variant detector.
            </p>
            <ul className="mt-4 space-y-2.5">
              <OrthoRow head="Convergence is stringent by construction" body="Agreement across orthogonal axes is a high bar, which is why a converged hit is worth bench time." />
              <OrthoRow head="Disagreement is informative, not noise" body="Chromatin says yes, constraint says no, and the mechanism explains why. A responsible tool surfaces that rather than manufacturing one confident number." />
              <OrthoRow head="Honesty is encoded for an agent" body="An agent, not a human reading a methods section, is calling this. Each verdict ships a confidence tier and a guardrail the agent can check." />
            </ul>
            <div className="mt-4 rounded-lg border border-line bg-page/60 px-3.5 py-2.5 text-[12px] leading-snug text-muted">
              The headline that survives: NCypher's chromatin engine recovers progenitor caQTLs at
              7.5x the base rate in its matched fetal context, is honest about the
              accessibility-versus-activity gap, and applies that calibrated engine to the first
              systematic non-coding survey of DMG.
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function paren(set: string): string {
  const m = set.match(/\((.*)\)/);
  return m ? m[1] : "brain";
}

function MiniStat({ value, label, sub }: { value: string; label: string; sub: string }) {
  return (
    <div className="rounded-lg border border-line bg-page/60 px-3 py-2.5 text-center">
      <div className="font-mono text-[19px] font-bold text-ink tnum">{value}</div>
      <div className="text-[11.5px] font-semibold text-ink">{label}</div>
      <div className="text-[10.5px] leading-tight text-muted">{sub}</div>
    </div>
  );
}

function OrthoRow({ head, body }: { head: string; body: string }) {
  return (
    <li className="flex gap-2.5">
      <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
      <span>
        <span className="text-[13px] font-semibold text-ink">{head}. </span>
        <span className="text-[12.5px] leading-snug text-muted">{body}</span>
      </span>
    </li>
  );
}
