#!/usr/bin/env python3
"""Verify paper/main.tex numeric claims match results/tables/paper_*.csv."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEX = (ROOT / "paper" / "main.tex").read_text()
OUT = ROOT / "results" / "tables"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> None:
    full = pd.read_csv(OUT / "paper_padmakumar_full.csv").set_index("condition")
    auth = pd.read_csv(OUT / "paper_padmakumar_auth.csv").set_index("condition")
    c = pd.read_csv(OUT / "paper_study1_contrasts.csv").set_index("contrast")
    ca = pd.read_csv(OUT / "paper_coauthor_accept.csv").set_index("accept_bin")
    matched = pd.read_csv(OUT / "paper_osf_matched.csv").set_index("source")
    within = pd.read_csv(OUT / "paper_osf_within.csv").set_index("condition")

    checks = [
        (f"{full.loc['solo','tfidf_D']:.3f}", "solo TF-IDF"),
        (f"{full.loc['gpt3','tfidf_D']:.3f}", "gpt3 TF-IDF"),
        (f"{full.loc['instructgpt','tfidf_D']:.3f}", "instructgpt TF-IDF"),
        (f"{full.loc['instructgpt','H_vs_solo']:.3f}", "H"),
        (f"{auth.loc['instructgpt model','tfidf_D']:.3f}", "igpt model TF-IDF"),
        (f"{auth.loc['instructgpt user','tfidf_D']:.3f}", "igpt user TF-IDF"),
        (f"{ca.loc['low','tfidf_diversity']:.3f}", "coauthor low D"),
        (f"{ca.loc['high','tfidf_diversity']:.3f}", "coauthor high D"),
        (f"{matched.loc['human','within_prompt_doc_dist']:.3f}", "matched human"),
        (f"{matched.loc['gpt','within_prompt_doc_dist']:.3f}", "matched gpt"),
        (f"{within.loc['essay','document_dist']:.3f}", "unaided doc"),
        (f"{within.loc['gpt_gen_essay','document_dist']:.3f}", "gpt gen doc"),
    ]
    for val, name in checks:
        if val not in TEX:
            fail(f"{name} value {val} missing from main.tex")

    # contrasts rounded
    for key, short in [
        ("solo - InstructGPT", "solo $-$ IGPT"),
        ("GPT-3 - InstructGPT", "GPT-3 $-$ IGPT"),
        ("solo - GPT-3", "solo $-$ GPT-3"),
    ]:
        est = f"{c.loc[key,'estimate']:.3f}".lstrip("0") if False else f"{abs(c.loc[key,'estimate']):.3f}"
        if est not in TEX:
            fail(f"contrast estimate {key} ~ {est} missing")

    # simulation contamination guard
    if "diversity_at_zero_influence" in TEX or "n_agents" in TEX:
        fail("simulated study language leaked into tex")
    sim_summary = ROOT / "results" / "summary.json"
    if sim_summary.exists() and not (ROOT / "results" / "SIMULATED_NOT_USED_IN_PAPER.md").exists():
        fail("simulated summary.json present without warning file")

    print("OK: paper numbers match regenerated real-data tables")


if __name__ == "__main__":
    main()
