# arXiv submission prep

## Metadata (paste into arXiv form)

**Title**
```
Shared Priors, Not Assistance in General: What Public Co-Writing Data Support about Homogenization
```

**Authors** (arXiv metadata format)
```
Babandeep Singh (Independent Researcher)
```

**Corresponding email**
```
babandeep193@gmail.com
```

**Primary category (suggested)**
```
cs.HC
```

**Cross-lists (optional)**
```
cs.CL
cs.AI
```

**Comments**
```
9 pages. Code and analysis tables: https://github.com/baban9/shared-priors-homogenization
```

**Abstract**
Use the abstract from `paper/main.tex` (ASCII only in the form if prompted).

**License (suggested)**
```
arXiv.org perpetual, non-exclusive license
```
or CC-BY-4.0 if preferred. Code in the GitHub repo is MIT.

## Source package for arXiv

Upload LaTeX source (preferred), not only PDF:

```
paper/main.tex
paper/references.bib
paper/figures/fig_multicorpus.png
paper/figures/fig_study1_contrasts.png   # optional if unused in tex
```

Compile locally first:

```bash
cd paper && tectonic -X compile main.tex
```

Or with pdflatex + bibtex. Prefer `pdflatex` on arXiv because figures are PNG.

## Do not upload to arXiv

- `.venv/`
- raw `data/real/` dumps (2GB+; cite upstream URLs)
- literature PDF archive under `papers/pdfs/`
- social/ marketing assets

## GitHub repo (analysis + tables)

https://github.com/baban9/shared-priors-homogenization
