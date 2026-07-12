# NCypher vs AlphaGenome: per-variant chromatin call

AlphaGenome = neural accessibility (ATAC+DNASE, 14 CNS tracks); impactful = neural max|log2FC| >= p95 of a 200-variant class-matched background (0.556). NCypher = fetal-OPC ChromBPNet log2FC; impactful at |log2FC| >= 0.162. 'p' = background percentile.

| Gene | Source | NCypher (OPC) | AlphaGenome (neural) | phyloP | Dir | Class |
|---|---|---|---|---|---|---|
| SYN3 | hero | IMPACT log2FC=-1.24 (loss) | IMPACT max=3.21 (loss, p100) | 8.58 | agree | both impactful |
| FARP1 | hero | IMPACT log2FC=-1.16 (loss) | IMPACT max=0.67 (loss, p96) | 8.64 | agree | both impactful |
| IGFBP7 | hero | IMPACT log2FC=-1.10 (loss) | moderate max=0.42 (loss, p92) | n/a | agree | NCypher only |
| GDPD5 | hero | IMPACT log2FC=-0.91 (loss) | IMPACT max=0.72 (loss, p96) | 2.8 | agree | both impactful |
| SOX2-OT | hero | IMPACT log2FC=+0.26 (gain) | weak max=0.26 (gain, p78) | 3.54 | agree | NCypher only |
| TERT | hero | weak log2FC=+0.10 (gain) | IMPACT max=1.06 (gain, p99) | 0.13 | agree | AlphaGenome only |
| TLE4 | hero | weak log2FC=+0.00 (gain) | weak max=0.31 (gain, p84) | 8.9 | agree | both not |
| NPAS3 | se-hit | IMPACT log2FC=-0.71 (loss) | weak max=0.20 (gain, p70) | 4.68 | DISAGREE | NCypher only |
| POLR2F | se-hit | IMPACT log2FC=-0.70 (loss) | IMPACT max=1.05 (loss, p99) | 8.7 | agree | both impactful |
| ENSR00000672906 | se-hit | IMPACT log2FC=+0.37 (gain) | weak max=0.15 (gain, p54) | 2.55 | agree | NCypher only |
| SNX29 | se-hit | IMPACT log2FC=+0.33 (gain) | IMPACT max=0.98 (gain, p99) | 3.07 | agree | both impactful |
| ELMO1 | se-hit | IMPACT log2FC=-0.32 (loss) | moderate max=0.43 (loss, p92) | 5.98 | agree | NCypher only |
| PDE2A | se-hit | IMPACT log2FC=-0.31 (loss) | IMPACT max=0.70 (loss, p96) | 5.91 | agree | both impactful |
| LOC105378374 | se-hit | IMPACT log2FC=-0.31 (loss) | IMPACT max=0.95 (loss, p98) | 4.93 | agree | both impactful |
| LOC101929727 | se-hit | IMPACT log2FC=+0.31 (gain) | moderate max=0.53 (gain, p94) | 3.38 | agree | NCypher only |
| ATP9B | se-hit | IMPACT log2FC=-0.28 (loss) | moderate max=0.40 (loss, p90) | 4.31 | agree | NCypher only |
| LOC105378102 | se-hit | IMPACT log2FC=+0.28 (gain) | moderate max=0.42 (gain, p91) | 2.28 | agree | NCypher only |
| LINC01117 | se-hit | IMPACT log2FC=-0.26 (loss) | IMPACT max=0.90 (loss, p98) | 8.82 | agree | both impactful |
| FNDC3B | se-hit | IMPACT log2FC=-0.26 (loss) | IMPACT max=1.15 (loss, p99) | 5.79 | agree | both impactful |
| LDLRAD3 | se-hit | IMPACT log2FC=-0.26 (loss) | IMPACT max=0.83 (loss, p97) | 5.68 | agree | both impactful |
| NFIC | se-hit | IMPACT log2FC=-0.26 (loss) | weak max=0.26 (loss, p78) | 3.66 | agree | NCypher only |
| LOC105378005 | se-hit | IMPACT log2FC=+0.25 (gain) | weak max=0.38 (gain, p88) | 2.96 | agree | NCypher only |
| SAMD4A | se-hit | IMPACT log2FC=+0.23 (gain) | weak max=0.35 (gain, p88) | 4.77 | agree | NCypher only |
| POLR2F | se-hit | IMPACT log2FC=-0.23 (loss) | weak max=0.27 (loss, p80) | 4.14 | agree | NCypher only |
| SAMD4A | se-hit | IMPACT log2FC=+0.23 (gain) | weak max=0.22 (gain, p74) | 2.37 | agree | NCypher only |
| SIPA1L2 | se-hit | IMPACT log2FC=-0.22 (loss) | moderate max=0.45 (loss, p92) | 5.02 | agree | NCypher only |
| PKNOX2 | se-hit | IMPACT log2FC=+0.22 (gain) | weak max=0.13 (loss, p51) | 4.02 | DISAGREE | NCypher only |
| ZFP36L1 | se-hit | IMPACT log2FC=-0.22 (loss) | weak max=0.12 (loss, p50) | 4.01 | agree | NCypher only |
| LINC01905 | se-hit | IMPACT log2FC=+0.21 (gain) | moderate max=0.55 (loss, p95) | 5.9 | DISAGREE | NCypher only |
| COL1A1 | se-hit | IMPACT log2FC=-0.21 (loss) | IMPACT max=0.82 (loss, p96) | 3.88 | agree | both impactful |
| RXRA | se-hit | IMPACT log2FC=-0.20 (loss) | none max=0.05 (gain, p21) | 4.25 | DISAGREE | NCypher only |
| SNX1 | se-hit | IMPACT log2FC=-0.20 (loss) | weak max=0.17 (gain, p58) | 3.28 | DISAGREE | NCypher only |
| NOL4L | se-hit | IMPACT log2FC=-0.19 (loss) | weak max=0.23 (loss, p76) | 7.02 | agree | NCypher only |
| PTPRJ | se-hit | IMPACT log2FC=+0.19 (gain) | IMPACT max=1.36 (loss, p99) | 4.6 | DISAGREE | both impactful |
| ANKRD44 | se-hit | IMPACT log2FC=-0.19 (loss) | weak max=0.24 (loss, p76) | 2.33 | agree | NCypher only |
| IER2 | se-hit | IMPACT log2FC=-0.18 (loss) | IMPACT max=0.56 (loss, p95) | 6.95 | agree | both impactful |
| ENST00000652518 | se-hit | IMPACT log2FC=+0.18 (gain) | moderate max=0.46 (loss, p92) | 4.17 | DISAGREE | NCypher only |
| XYLT1 | se-hit | IMPACT log2FC=-0.17 (loss) | moderate max=0.41 (loss, p90) | 4.72 | agree | NCypher only |