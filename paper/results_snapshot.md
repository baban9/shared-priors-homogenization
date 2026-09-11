# Results snapshot (real-data paper)

## Study 1 inference (seed 42)
| Contrast | Est. | 95% CI | perm p |
|---|---:|---|---:|
| solo - InstructGPT | 0.040 | [-0.018, 0.099] | 0.003 |
| GPT-3 - InstructGPT | 0.047 | [0.001, 0.097] | 0.001 |
| solo - GPT-3 | -0.008 | [-0.063, 0.046] | 0.709 |

Robustness: unigram and nostop preserve InstructGPT < solo ≈ GPT-3.
Code: `scripts/study1_stats.py`

## Means
solo 0.780, gpt3 0.788, instructgpt 0.740 (H=0.051)

## Other studies
CoAuthor: accept terciles flat (0.929 / 0.929 / 0.922)
Moon: model prior narrow; word collapse not supported
Simsek: debt not identifiable

## Claim map
See `results/tables/paper_claim_verdicts.csv`
