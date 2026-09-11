# Reading list and sequence

Aligned to the paper claim:

- **Keep:** shared feedback-tuned priors can compress co-written diversity
- **Drop:** any LM assistance homogenizes
- **Leave open:** transfer debt / unified cognitive convergence

Local PDFs live under `papers/pdfs/` unless noted.
Your paper: `paper/main.pdf`.

---

## Read in this order

### 1. Foundations (why offloading and over-reliance matter)
| # | Paper | Local file | Why now |
|---|---|---|---|
| 1 | Risko & Gilbert 2016, Cognitive Offloading | `risko2016offloading_tics.pdf` | Names offloading before LLMs |
| 2 | Parasuraman & Riley 1997, Use/Misuse/Disuse/Abuse | `parasuraman1997automation_hf.pdf` | Automation bias vocabulary |

### 2. The claim we keep (read carefully)
| # | Paper | Local file / link | Why now |
|---|---|---|---|
| 3 | Padmakumar & He 2024, Does Writing with LMs Reduce Content Diversity? | `padmakumar2024diversity_2309.05196.pdf` | Primary reanalysis: InstructGPT vs GPT-3 vs solo |
| 4 | Moon et al. 2026, Diverse Words / Original Ideas (semantic disjunction) | `moon2026disjunction_jsz58_v6.pdf` ; data https://doi.org/10.17605/OSF.IO/YD94Z | Model prior is narrow; observational word vs document split is mixed |

### 3. Where the broader claim weakens
| # | Paper | Local file / link | Why now |
|---|---|---|---|
| 5 | Lee, Liang, Yang 2022, CoAuthor | `lee2022coauthor_2201.06796.pdf` ; data https://coauthor.stanford.edu | Large co-writing log; no solo arm; weak accept dose on group diversity |
| 6 | Anderson, Shah, Kreminski 2024, Homogenization Effects... | `anderson2024homogenization_cc2024.pdf` | Ideation homogenization (external; microdata closed) |

### 4. Debt / transfer (leave open; do not overclaim)
| # | Paper | Local file / link | Why now |
|---|---|---|---|
| 7 | Kosmyna et al. 2025, Your Brain on ChatGPT | `kosmyna2025eeg_2506.08872.pdf` | Debt / EEG (cite published estimates only) |
| 8 | Barcaui 2025, ChatGPT as a cognitive crutch | `barcaui2025crutch_ssho.pdf` | Retention RCT (microdata closed) |
| 9 | Simsek et al. 2025, Is ChatGPT a good study companion? | `simsek2025companion_h2se3.pdf` ; data https://doi.org/10.17605/OSF.IO/SWYTK | Public logs; both arms use ChatGPT so debt vs unaided is not identified |

### 5. Context (optional but useful)
| # | Paper | Local file | Why now |
|---|---|---|---|
| 10 | Lee et al. 2025, GenAI and critical thinking survey | `lee2025critical_chi2025.pdf` | Effort / confidence; not diversity |
| 11 | Dell'Acqua et al. 2025, Jagged Technological Frontier | `dellacqua2025frontier_jagged.pdf` | When AI helps vs hurts performance |
| 12 | Acemoglu, Kong, Ozdaglar 2026, AI and Knowledge Collapse | `acemoglu2026collapse_nber34910.pdf` | Population framing; theory, not our microdata |

### 6. Skip for this paper (local only / older copies)
- `dokumaci2024offloading_2401.12187.pdf`
- `wu2025calibration_2308.05374.pdf`
- `anderson2024homogenization_2402.01536.pdf` (prefer `_cc2024`)
- `padmakumar2023homogenization_2309.05196.pdf` (duplicate of 2024 file)
- `dellacqua2023ai_2403.11316.pdf` (older/wrong-keyed copy)

---

## Fast path (if short on time)

1. Padmakumar & He (full)
2. Moon et al. abstract + Exp1/Exp3 tables (model vs human; within-subject)
3. CoAuthor paper skim + our CoAuthor accept tercile result
4. Kosmyna abstract + Barcaui results table (external debt only)
5. Your paper: `paper/main.pdf`

## After reading: check against our verdicts

| Claim | Our verdict |
|---|---|
| InstructGPT homogenizes vs solo/GPT-3 | Supported |
| Any LM assistance homogenizes | Not supported |
| Accept dose on group diversity | Weak / mixed |
| Model-only text narrower than human | Supported |
| Post-ChatGPT word-diversity collapse | Not supported |
| Transfer debt in public learning logs | Not testable |
| Unified cognitive convergence | Not established |

Full audit: `results/honest_claim_audit/HOLISTIC_CLAIM_VERDICT.md`
