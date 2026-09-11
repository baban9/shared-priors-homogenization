# Shared Priors and Writing Diversity

Independent reanalysis of public co-writing corpora.

**Format:** workshop-style technical report (not a full conference paper)  
**Paper:** `paper/main.pdf`  
**Author:** Babandeep Singh (`babandeep193@gmail.com`)  
**Code:** https://github.com/baban9/shared-priors-homogenization  
**arXiv prep:** `paper/ARXIV.md`

## Claim

Shared feedback-tuned language-model priors can compress co-written diversity. Assistance in general does not. Unified cognitive convergence with transfer debt is not established on public microdata.

## Reproduce (real data only)

1. Place upstream corpora under the paths in **Data layout** below (not shipped in git; ~2GB).
2. Install deps (needs `sentence-transformers` / a local MiniLM cache):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# First run online once to cache MiniLM, or reuse an existing HF cache:
#   python -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/all-MiniLM-L6-v2')"
.venv/bin/python scripts/reproduce_paper.py
.venv/bin/python scripts/verify_paper_numbers.py
cd paper && tectonic -X compile main.tex   # or pdflatex + bibtex
```

`scripts/reproduce_paper.py` rebuilds `results/tables/paper_*.csv`, figures, and syncs numbers into `paper/main.tex`.  
`scripts/verify_paper_numbers.py` checks that the TeX numbers match those tables.

**Do not use** `results/summary.json` or `scripts/run_all.py` for the paper. Those are legacy simulations. See `results/SIMULATED_NOT_USED_IN_PAPER.md`.

## Data layout (required for reproduction)

| Corpus | Expected local path | Upstream |
|--------|---------------------|----------|
| Padmakumar & He | `data/real/padmakumar_hai_diversity/repo/processed_data/*.jsonl` | https://github.com/vishakhpk/hai-diversity |
| CoAuthor | `data/real/coauthor/extracted/coauthor-v1.0/*.jsonl` | https://coauthor.stanford.edu |
| Moon et al. | `data/real/osf_yd94z/02_data/semantic_disjunction/` | https://doi.org/10.17605/OSF.IO/YD94Z |
| Simsek et al. | `data/real/osf_swytk/processed_data/` | https://doi.org/10.17605/OSF.IO/SWYTK |

Notes: `data/literature/READ_LIST.md`, `data/literature/SOURCE_PROVENANCE.md`

## Repo map

| Path | Purpose |
|------|---------|
| `paper/` | LaTeX, PDF, figures, `ARXIV.md` |
| `scripts/reproduce_paper.py` | **Canonical** end-to-end real-data rebuild |
| `scripts/verify_paper_numbers.py` | TeX vs CSV check |
| `scripts/make_paper_figures.py` | Figures only |
| `scripts/study1_stats.py` | Study 1 subset (prefer `reproduce_paper.py`) |
| `results/tables/paper_*.csv` | Numbers used in the paper |
| `results/honest_claim_audit/` | Claim map / audit JSON |

## License

Code and analysis artifacts: MIT (`LICENSE`).  
Upstream corpora keep their original licenses; obtain them from the sources above.
