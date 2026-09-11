# Shared Priors and Writing Diversity

Independent reanalysis of public co-writing corpora.

**Paper:** `paper/main.pdf`  
**Author:** Babandeep Singh (`babandeep193@gmail.com`)  
**Preprint prep:** `paper/ARXIV.md`

## Claim

Shared feedback-tuned language-model priors can compress co-written diversity. Assistance in general does not. Unified cognitive convergence with transfer debt is not established on public microdata.

## Reproduce paper numbers

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# After placing upstream corpora under data/real/ (see docs below):
python scripts/study1_stats.py
python scripts/make_paper_figures.py
cd paper && tectonic -X compile main.tex
```

Paper tables shipped in-repo: `results/tables/paper_*.csv`

## Upstream data (not redistributed here)

| Corpus | Link |
|--------|------|
| Padmakumar & He | https://github.com/vishakhpk/hai-diversity |
| CoAuthor | https://coauthor.stanford.edu |
| Moon et al. | https://doi.org/10.17605/OSF.IO/YD94Z |
| Simsek et al. | https://doi.org/10.17605/OSF.IO/SWYTK |

Local layout notes: `data/literature/READ_LIST.md`

## Repo map

| Path | Purpose |
|------|---------|
| `paper/` | LaTeX + PDF + figures |
| `scripts/study1_stats.py` | Study 1 bootstrap / permutation |
| `scripts/make_paper_figures.py` | Paper figures |
| `results/tables/paper_*.csv` | Numbers used in the paper |
| `results/honest_claim_audit/` | Keep / drop / leave-open verdicts |

## License

Code and analysis artifacts: MIT (`LICENSE`).  
Upstream corpora retain their original licenses and must be obtained from the sources above.
