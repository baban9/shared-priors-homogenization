#!/usr/bin/env python3
"""Study 1 bootstrap CIs, permutation tests, and vectorizer robustness."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/real/padmakumar_hai_diversity/repo/processed_data"
OUT = ROOT / "results" / "tables"
FIG = ROOT / "paper" / "figures"
RNG = np.random.default_rng(42)
B = 5000
NPERM = 999


def load_jsonl(name: str) -> list[dict]:
    rows = []
    for line in (BASE / name).read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if len((obj.get("essay") or "").split()) < 40:
            continue
        rows.append(obj)
    return rows


def fit_vec(all_texts: list[str], **kw) -> TfidfVectorizer:
    defaults = dict(stop_words="english", max_features=8000, ngram_range=(1, 2), min_df=2)
    defaults.update(kw)
    return TfidfVectorizer(**defaults).fit(all_texts)


def mean_pair_sim(mat) -> float:
    sim = cosine_similarity(mat)
    n = sim.shape[0]
    if n < 2:
        return float("nan")
    iu = np.triu_indices(n, 1)
    return float(sim[iu].mean())


def by_title(rows: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        out[row["title"]].append(row["essay"])
    return out


def topic_ds(by: dict[str, list[str]], vec: TfidfVectorizer) -> dict[str, float]:
    out = {}
    for title, texts in by.items():
        if len(texts) < 2:
            continue
        out[title] = 1.0 - mean_pair_sim(vec.transform(texts))
    return out


def boot_mean(vals, n: int = B) -> np.ndarray:
    vals = np.asarray(list(vals), dtype=float)
    return np.array([vals[RNG.integers(0, len(vals), len(vals))].mean() for _ in range(n)])


def summarize(arr: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(arr.mean()),
        "lo": float(np.quantile(arr, 0.025)),
        "hi": float(np.quantile(arr, 0.975)),
        "frac_pos": float((arr > 0).mean()),
    }


def perm_topic_gap(by_a, by_b, vec, n_perm: int = NPERM):
    titles = [t for t in set(by_a) & set(by_b) if len(by_a[t]) >= 2 and len(by_b[t]) >= 2]
    caches = {}
    for title in titles:
        pool = by_a[title] + by_b[title]
        caches[title] = (vec.transform(pool), len(by_a[title]), len(pool))

    def gap(X, na, idx_a):
        mask = np.zeros(X.shape[0], dtype=bool)
        mask[list(idx_a)] = True
        xa, xb = X[mask], X[~mask]
        if xa.shape[0] < 2 or xb.shape[0] < 2:
            return np.nan
        return (1 - mean_pair_sim(xa)) - (1 - mean_pair_sim(xb))

    obs = []
    for title in titles:
        X, na, _ = caches[title]
        obs.append(gap(X, na, range(na)))
    obs_mean = float(np.mean(obs))
    null = []
    for _ in range(n_perm):
        gaps = []
        for title in titles:
            X, na, n = caches[title]
            idx = RNG.choice(n, size=na, replace=False)
            gaps.append(gap(X, na, idx.tolist()))
        null.append(np.nanmean(gaps))
    p = float((np.asarray(null) >= obs_mean).mean())
    return obs_mean, p, len(titles)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    solo, gpt3, igpt = map(load_jsonl, ["essays_solo.jsonl", "essays_gpt3.jsonl", "essays_instructgpt.jsonl"])
    all_texts = [r["essay"] for r in solo + gpt3 + igpt]
    vec = fit_vec(all_texts)
    maps = {"solo": by_title(solo), "gpt3": by_title(gpt3), "instructgpt": by_title(igpt)}
    tds = {k: topic_ds(m, vec) for k, m in maps.items()}
    mean_d = {k: float(np.mean(list(v.values()))) for k, v in tds.items()}
    boots = {k: boot_mean(tds[k].values()) for k in tds}
    gaps = {
        "solo_minus_igpt": boots["solo"] - boots["instructgpt"],
        "gpt3_minus_igpt": boots["gpt3"] - boots["instructgpt"],
        "solo_minus_gpt3": boots["solo"] - boots["gpt3"],
    }
    obs_is, p_is, n_is = perm_topic_gap(maps["solo"], maps["instructgpt"], vec)
    obs_ig, p_ig, n_ig = perm_topic_gap(maps["gpt3"], maps["instructgpt"], vec)
    obs_gs, p_gs, n_gs = perm_topic_gap(maps["solo"], maps["gpt3"], vec)

    rob = []
    for spec, v in [
        ("main_tfidf_12", vec),
        ("unigram", fit_vec(all_texts, ngram_range=(1, 1), max_features=5000)),
        ("nostop", fit_vec(all_texts, stop_words=None)),
    ]:
        for name, rows in [("solo", solo), ("gpt3", gpt3), ("instructgpt", igpt)]:
            d = topic_ds(by_title(rows), v)
            rob.append({"spec": spec, "condition": name, "D": float(np.mean(list(d.values())))})

    summary = {
        "mean_D": mean_d,
        "H_igpt": (mean_d["solo"] - mean_d["instructgpt"]) / mean_d["solo"],
        "bootstrap_gaps": {k: summarize(v) for k, v in gaps.items()},
        "permutation": {
            "solo_minus_igpt": {"obs": obs_is, "p": p_is, "n_topics": n_is},
            "gpt3_minus_igpt": {"obs": obs_ig, "p": p_ig, "n_topics": n_ig},
            "solo_minus_gpt3": {"obs": obs_gs, "p": p_gs, "n_topics": n_gs},
        },
    }
    (OUT / "paper_study1_stats.json").write_text(json.dumps(summary, indent=2))
    pd.DataFrame(rob).to_csv(OUT / "paper_padmakumar_robustness.csv", index=False)
    stats = pd.DataFrame(
        [
            {
                "contrast": "solo - InstructGPT",
                **summary["bootstrap_gaps"]["solo_minus_igpt"],
                "perm_p": p_is,
            },
            {
                "contrast": "GPT-3 - InstructGPT",
                **summary["bootstrap_gaps"]["gpt3_minus_igpt"],
                "perm_p": p_ig,
            },
            {
                "contrast": "solo - GPT-3",
                **summary["bootstrap_gaps"]["solo_minus_gpt3"],
                "perm_p": p_gs,
            },
        ]
    )
    stats.to_csv(OUT / "paper_study1_contrasts.csv", index=False)

    # Prefer the shared paper figure script for final art.
    try:
        from make_paper_figures import forest_contrasts, style as fig_style

        fig_style()
        forest_contrasts()
    except Exception:
        pass
    print(stats.to_string(index=False))


if __name__ == "__main__":
    main()
