# Source provenance

This file records where claims and data in the project come from.
Canonical reading order: `data/literature/READ_LIST.md`.
Canonical paper claim: shared feedback-tuned priors can compress co-written diversity; unified cognitive convergence is not established.

## Real human data used in the paper

| Source | Local path | Role in paper |
|---|---|---|
| Padmakumar & He ICLR 2024 essays | `data/real/padmakumar_hai_diversity/repo/processed_data/` | Study 1: InstructGPT vs GPT-3 vs solo; authorship split |
| CoAuthor CHI 2022 sessions | `data/real/coauthor/extracted/coauthor-v1.0/` | Study 2: acceptance dose vs diversity |
| Moon et al. OSF yd94z | `data/real/osf_yd94z/02_data/semantic_disjunction/` | Study 3: model prior; pre/post; within-subject |
| Simsek et al. OSF swytk/jmz85 | `data/real/osf_swytk/` | Study 4: debt not identifiable (ChatGPT vs ChatGPT arms) |

Padmakumar clone: https://github.com/vishakhpk/hai-diversity  
CoAuthor: https://coauthor.stanford.edu  
Moon data: https://doi.org/10.17605/OSF.IO/YD94Z  
Study companion: https://doi.org/10.17605/OSF.IO/SWYTK

## Primary literature (local PDFs + new cited sources)

| Citation key | Local PDF / link | Role in paper |
|---|---|---|
| `padmakumar2024diversity` | `papers/pdfs/padmakumar2024diversity_2309.05196.pdf` | Keep: InstructGPT homogenization |
| `lee2022coauthor` | `papers/pdfs/lee2022coauthor_2201.06796.pdf` | Limit: co-writing dose, no solo arm |
| `moon2026disjunction` | `papers/pdfs/moon2026disjunction_jsz58_v6.pdf` | Keep model-narrowness; drop word-collapse overclaim |
| `osfyd94z2026` | https://doi.org/10.17605/OSF.IO/YD94Z | Data citation for Moon materials |
| `simsek2025companion` | `papers/pdfs/simsek2025companion_h2se3.pdf` | Leave open: debt not identified in public logs |
| `osfswytk2025` | https://doi.org/10.17605/OSF.IO/SWYTK | Data citation for study companion |
| `anderson2024homogenization` | `anderson2024homogenization_cc2024.pdf` | External ideation homogenization |
| `kosmyna2025eeg` | `kosmyna2025eeg_2506.08872.pdf` | External debt estimates |
| `barcaui2025crutch` | `barcaui2025crutch_ssho.pdf` | External retention RCT |
| `lee2025critical` | `lee2025critical_chi2025.pdf` | Context: effort / confidence |
| `acemoglu2026collapse` | `acemoglu2026collapse_nber34910.pdf` | Population framing |
| `dellacqua2025frontier` | `dellacqua2025frontier_jagged.pdf` | Performance vs competence context |
| `parasuraman1997automation` | `parasuraman1997automation_hf.pdf` | Automation bias classic |
| `risko2016offloading` | `risko2016offloading_tics.pdf` | Offloading review |

## Study order (enough for deep understanding)

1. Risko & Gilbert, then Parasuraman & Riley (foundations)
2. Padmakumar & He (the keep claim)
3. Moon et al. (model prior vs mixed observational era effects)
4. Lee et al. CoAuthor (why assistance-as-such does not travel)
5. Anderson (external ideation; closed microdata)
6. Kosmyna, Barcaui, then Simsek (debt left open / not identified here)
7. Optional: Lee CHI 2025, Dell'Acqua, Acemoglu

Fast path and skip list: `READ_LIST.md`.

## Older / unrelated local PDFs

Not needed for the current paper:
`dokumaci2024offloading_2401.12187.pdf`, `wu2025calibration_2308.05374.pdf`,
`anderson2024homogenization_2402.01536.pdf` (older copy),
`padmakumar2023homogenization_2309.05196.pdf` (duplicate older name),
`dellacqua2023ai_2403.11316.pdf` (older/wrong-keyed copy).

## Simulation data lineage

| Artifact | Generator | Notes |
|---|---|---|
| `data/processed/study1_*.csv` ... `study8_*.csv` | `scripts/run_all.py` | Seeded agent simulations; **not used in current paper** |
| `results/honest_claim_audit/` | multi-corpus audit scripts | Public-data claim verdicts |
| `results/tables/paper_*.csv` | paper table export | Numbers used in `paper/main.tex` |

Do not present simulation CSVs as human-subject data.
The current paper is real-data only.
