import { BASE_COLOURS, fmtNum } from "../lib/format";
import type { HeroContent, SweepRow } from "../types";

/** ref -> alt substitution rendered in the fixed DNA base colours. */
export function VariantBases({ vkey, size = 20 }: { vkey: string; size?: number }) {
  const parts = vkey.split("-");
  const ref = parts[2] ?? "";
  const alt = parts[3] ?? "";
  return (
    <span className="inline-flex items-center gap-1.5 font-mono font-bold" style={{ fontSize: size }}>
      <span style={{ color: BASE_COLOURS[ref] ?? "#0F1E24" }}>{ref}</span>
      <svg width="16" height="12" viewBox="0 0 16 12" className="text-faint">
        <path d="M1 6h12m0 0-4-4m4 4-4 4" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span style={{ color: BASE_COLOURS[alt] ?? "#0F1E24" }}>{alt}</span>
    </span>
  );
}

/** The DeepSHAP "contribution collapse" as before/after bars (real magnitudes). */
export function ContributionCollapse({
  collapse,
  refVal,
  altVal,
}: {
  collapse: number; // 0..1
  refVal?: number;
  altVal?: number;
}) {
  const pct = Math.round(collapse * 100);
  const altFrac = Math.max(0, 1 - collapse);
  return (
    <div className="rounded-xl border border-line bg-page/60 p-4">
      <div className="flex items-baseline justify-between">
        <div className="text-[13px] font-semibold text-ink">Model-native contribution at the variant base</div>
        <div className="font-mono text-[22px] font-bold tnum text-nogo">{pct}%</div>
      </div>
      <div className="mt-0.5 text-[11.5px] text-muted">
        DeepSHAP local importance, reference vs alternate allele (collapse)
      </div>

      <div className="mt-4 space-y-3">
        <CollapseBar label="reference" frac={1} value={refVal} colour="#0E9E8A" />
        <CollapseBar label="alternate" frac={altFrac} value={altVal} colour="#DA4A42" />
      </div>
      <div className="mt-3 text-[11.5px] leading-snug text-muted">
        A {pct}% collapse means the base the model relied on in the reference sequence stops
        contributing under the alt allele. The motif is broken at the exact variant base.
      </div>
    </div>
  );
}

function CollapseBar({
  label,
  frac,
  value,
  colour,
}: {
  label: string;
  frac: number;
  value?: number;
  colour: string;
}) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11.5px]">
        <span className="font-medium text-ink">{label} allele</span>
        {value !== undefined && (
          <span className="font-mono tnum text-muted">{fmtNum(value, 3)}</span>
        )}
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-line">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${Math.max(2, frac * 100)}%`, backgroundColor: colour }}
        />
      </div>
    </div>
  );
}

/** For a GAIN variant: a calibrated meter showing log2FC past the p99 threshold. */
export function GainMeter({ logfc, threshold }: { logfc: number; threshold: number }) {
  const max = 0.45; // display ceiling for the cohort dynamic range
  const clamp = (x: number) => Math.max(0, Math.min(1, x / max));
  const thr = clamp(threshold) * 100;
  const val = clamp(Math.abs(logfc)) * 100;
  return (
    <div className="rounded-xl border border-line bg-page/60 p-4">
      <div className="flex items-baseline justify-between">
        <div className="text-[13px] font-semibold text-ink">Calibrated accessibility gain</div>
        <div className="font-mono text-[22px] font-bold tnum text-teal-600">
          +{fmtNum(logfc, 3)}
        </div>
      </div>
      <div className="mt-0.5 text-[11.5px] text-muted">
        log2FC on the cohort dynamic range, against the p99 high-impact threshold
      </div>

      <div className="relative mt-6 h-3 w-full rounded-full bg-gradient-to-r from-teal-100 to-teal-300">
        {/* threshold marker */}
        <div
          className="absolute top-1/2 -translate-y-1/2"
          style={{ left: `${thr}%` }}
        >
          <div className="h-6 w-[2px] -translate-x-1/2 bg-ink/50" />
        </div>
        {/* value marker */}
        <div className="absolute top-1/2 -translate-y-1/2" style={{ left: `${val}%` }}>
          <div className="h-5 w-5 -translate-x-1/2 rounded-full border-[3px] border-white bg-teal-500 shadow-pill" />
        </div>
      </div>
      <div className="relative mt-1 h-4 text-[10.5px] text-muted">
        <span className="absolute left-0">0</span>
        <span className="absolute -translate-x-1/2" style={{ left: `${thr}%` }}>
          p99 = {threshold}
        </span>
        <span className="absolute right-0">{max}</span>
      </div>
      <div className="mt-3 text-[11.5px] leading-snug text-muted">
        A rare gain (33 of 164 converged hits). The direction fits an enhancer that reinforces the
        circuit, a created or strengthened motif rather than a broken one.
      </div>
    </div>
  );
}

/** Dispatch: real DeepSHAP PNG, or a mechanism visual, based on the hero kind. */
export function SaliencyView({ hero, row }: { hero: HeroContent; row: SweepRow }) {
  if (hero.saliencyKind === "deepshap" && hero.saliencyImage) {
    return (
      <figure className="overflow-hidden rounded-xl border border-line bg-white">
        <img
          src={hero.saliencyImage}
          alt={`Ref vs alt DeepSHAP saliency logo for ${hero.gene} ${hero.key}`}
          className="w-full"
        />
        <figcaption className="border-t border-line bg-page/60 px-4 py-2 text-[11.5px] text-muted">
          Model-native DeepSHAP contribution logo, Corces c15 (fetal-OPC) ChromBPNet. The variant
          base is highlighted; the reference motif visibly collapses under the alternate allele.
        </figcaption>
      </figure>
    );
  }
  if (hero.saliencyKind === "collapse" && row.deepshap_collapse != null) {
    return (
      <ContributionCollapse
        collapse={row.deepshap_collapse}
        refVal={hero.key === "chr14-33788719-A-G" ? 0.299 : undefined}
        altVal={hero.key === "chr14-33788719-A-G" ? 0.059 : undefined}
      />
    );
  }
  if (hero.saliencyKind === "gain" && row.logfc != null) {
    return <GainMeter logfc={row.logfc} threshold={0.162} />;
  }
  return null;
}
