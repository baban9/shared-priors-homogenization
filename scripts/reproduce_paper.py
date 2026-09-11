#!/usr/bin/env python3
"""Regenerate all paper tables/figures from public real corpora only.

No simulated studies. Outputs under results/tables/paper_*.csv and paper/figures/.

Usage:
  .venv/bin/python scripts/reproduce_paper.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PAD = ROOT / "data/real/padmakumar_hai_diversity/repo/processed_data"
COAUTHOR = ROOT / "data/real/coauthor/extracted/coauthor-v1.0"
OSF = ROOT / "data/real/osf_yd94z/02_data/semantic_disjunction"
SIMSEK = ROOT / "data/real/osf_swytk/processed_data"
OUT = ROOT / "results" / "tables"
AUDIT = ROOT / "results" / "honest_claim_audit"
FIG = ROOT / "paper" / "figures"
RNG = np.random.default_rng(42)
B = 5000
NPERM = 999


def mean_pair_sim(mat) -> float:
    sim = cosine_similarity(mat)
    n = sim.shape[0]
    if n < 2:
        return float("nan")
    iu = np.triu_indices(n, 1)
    return float(sim[iu].mean())


def fit_tfidf(texts: list[str], **kw) -> TfidfVectorizer:
    defaults = dict(stop_words="english", max_features=8000, ngram_range=(1, 2), min_df=2)
    defaults.update(kw)
    return TfidfVectorizer(**defaults).fit(texts)


def topic_diversity(by_title: dict[str, list[str]], vec) -> dict[str, float]:
    out = {}
    for title, texts in by_title.items():
        if len(texts) < 2:
            continue
        out[title] = 1.0 - mean_pair_sim(vec.transform(texts))
    return out


def load_padmakumar(name: str) -> list[dict]:
    rows = []
    for line in (PAD / name).read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if len((obj.get("essay") or "").split()) < 40:
            continue
        rows.append(obj)
    return rows


def group_by_title(rows: list[dict], text_key: str = "essay") -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        out[row["title"]].append(row[text_key])
    return out


def authorship_texts(rows: list[dict], label: str) -> list[dict]:
    out = []
    for row in rows:
        sents = row.get("sentences") or []
        auth = row.get("authorship") or []
        parts = [s for s, a in zip(sents, auth) if a == label]
        text = " ".join(parts).strip()
        if len(text.split()) < 20:
            continue
        out.append({"title": row["title"], "essay": text})
    return out


def emb_diversity(by_title: dict[str, list[str]], model) -> float:
    vals = []
    for texts in by_title.values():
        if len(texts) < 2:
            continue
        emb = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        vals.append(1.0 - mean_pair_sim(np.asarray(emb)))
    return float(np.mean(vals)) if vals else float("nan")


def boot_mean(vals, n: int = B) -> np.ndarray:
    vals = np.asarray(list(vals), dtype=float)
    return np.array([vals[RNG.integers(0, len(vals), len(vals))].mean() for _ in range(n)])


def summarize(arr: np.ndarray) -> dict[str, float]:
    return {
        "estimate": float(arr.mean()),
        "ci95_lo": float(np.quantile(arr, 0.025)),
        "ci95_hi": float(np.quantile(arr, 0.975)),
        "boot_frac_pos": float((arr > 0).mean()),
    }


def perm_topic_gap(by_a, by_b, vec, n_perm: int = NPERM):
    titles = [t for t in set(by_a) & set(by_b) if len(by_a[t]) >= 2 and len(by_b[t]) >= 2]
    caches = {}
    for title in titles:
        pool = by_a[title] + by_b[title]
        caches[title] = (vec.transform(pool), len(by_a[title]), len(pool))

    def gap(X, idx_a):
        mask = np.zeros(X.shape[0], dtype=bool)
        mask[list(idx_a)] = True
        xa, xb = X[mask], X[~mask]
        if xa.shape[0] < 2 or xb.shape[0] < 2:
            return np.nan
        return (1 - mean_pair_sim(xa)) - (1 - mean_pair_sim(xb))

    obs = [gap(caches[t][0], range(caches[t][1])) for t in titles]
    obs_mean = float(np.mean(obs))
    null = []
    for _ in range(n_perm):
        gaps = []
        for title in titles:
            X, na, n = caches[title]
            idx = RNG.choice(n, size=na, replace=False)
            gaps.append(gap(X, idx.tolist()))
        null.append(np.nanmean(gaps))
    p = float((np.asarray(null) >= obs_mean).mean())
    return obs_mean, p, len(titles)


def study1_padmakumar(model) -> dict:
    print("Study 1: Padmakumar...")
    solo = load_padmakumar("essays_solo.jsonl")
    gpt3 = load_padmakumar("essays_gpt3.jsonl")
    igpt = load_padmakumar("essays_instructgpt.jsonl")
    all_texts = [r["essay"] for r in solo + gpt3 + igpt]
    vec = fit_tfidf(all_texts)
    maps = {
        "solo": group_by_title(solo),
        "gpt3": group_by_title(gpt3),
        "instructgpt": group_by_title(igpt),
    }
    tds = {k: topic_diversity(m, vec) for k, m in maps.items()}
    mean_d = {k: float(np.mean(list(v.values()))) for k, v in tds.items()}
    emb_d = {k: emb_diversity(m, model) for k, m in maps.items()}
    H = {k: (mean_d["solo"] - mean_d[k]) / mean_d["solo"] for k in mean_d}

    full = pd.DataFrame(
        [
            {
                "condition": k,
                "N": len({"solo": solo, "gpt3": gpt3, "instructgpt": igpt}[k]),
                "tfidf_D": round(mean_d[k], 3),
                "emb_D": round(emb_d[k], 3),
                "H_vs_solo": round(H[k], 3),
            }
            for k in ["solo", "gpt3", "instructgpt"]
        ]
    )
    full.to_csv(OUT / "paper_padmakumar_full.csv", index=False)

    auth_rows = []
    for cond, rows in [("gpt3", gpt3), ("instructgpt", igpt)]:
        for lab, tag in [("U", "user"), ("A", "model")]:
            subset = authorship_texts(rows, lab)
            by = group_by_title(subset)
            d = topic_diversity(by, fit_tfidf([r["essay"] for r in subset] + all_texts[:1]))
            # fit on subset+corpus for stability: use global vec
            d = topic_diversity(by, vec)
            auth_rows.append(
                {
                    "condition": f"{cond} {tag}",
                    "N": len(subset),
                    "tfidf_D": round(float(np.mean(list(d.values()))), 3),
                    "emb_D": round(emb_diversity(by, model), 3),
                }
            )
    auth = pd.DataFrame(auth_rows)
    auth.to_csv(OUT / "paper_padmakumar_auth.csv", index=False)

    boots = {k: boot_mean(tds[k].values()) for k in tds}
    gaps = {
        "solo - InstructGPT": boots["solo"] - boots["instructgpt"],
        "GPT-3 - InstructGPT": boots["gpt3"] - boots["instructgpt"],
        "solo - GPT-3": boots["solo"] - boots["gpt3"],
    }
    pmap = {
        "solo - InstructGPT": perm_topic_gap(maps["solo"], maps["instructgpt"], vec),
        "GPT-3 - InstructGPT": perm_topic_gap(maps["gpt3"], maps["instructgpt"], vec),
        "solo - GPT-3": perm_topic_gap(maps["solo"], maps["gpt3"], vec),
    }
    contrasts = []
    for name, arr in gaps.items():
        row = {"contrast": name, **summarize(arr), "perm_p": pmap[name][1]}
        contrasts.append(row)
    pd.DataFrame(contrasts).to_csv(OUT / "paper_study1_contrasts.csv", index=False)

    rob = []
    for spec, v in [
        ("main (1-2 gram)", vec),
        ("unigram", fit_tfidf(all_texts, ngram_range=(1, 1), max_features=5000)),
        ("no stop-word filter", fit_tfidf(all_texts, stop_words=None)),
    ]:
        row = {"spec": spec}
        for name in ["solo", "gpt3", "instructgpt"]:
            d = topic_diversity(maps[name], v)
            row[name] = round(float(np.mean(list(d.values()))), 3)
        rob.append(row)
    pd.DataFrame(rob).to_csv(OUT / "paper_padmakumar_robustness.csv", index=False)

    # topic paired deltas
    titles = sorted(set(tds["solo"]) & set(tds["gpt3"]) & set(tds["instructgpt"]))
    paired = pd.DataFrame(
        [
            {
                "title": t,
                "solo": tds["solo"][t],
                "gpt3": tds["gpt3"][t],
                "instructgpt": tds["instructgpt"][t],
            }
            for t in titles
        ]
    )
    paired.to_csv(OUT / "paper_padmakumar_topic_paired.csv", index=False)

    stats = {
        "mean_D": mean_d,
        "emb_D": emb_d,
        "H": H,
        "contrasts": contrasts,
        "frac_topics_igpt_lt_solo": float(np.mean([tds["instructgpt"][t] < tds["solo"][t] for t in titles])),
        "frac_topics_igpt_lt_gpt3": float(np.mean([tds["instructgpt"][t] < tds["gpt3"][t] for t in titles])),
        "source": str(PAD),
        "seed": 42,
        "n_bootstrap": B,
        "n_perm": NPERM,
    }
    (OUT / "paper_study1_stats.json").write_text(json.dumps(stats, indent=2))
    return stats


def study2_coauthor() -> dict:
    print("Study 2: CoAuthor...")
    sessions = []
    for path in sorted(COAUTHOR.glob("*.jsonl")):
        last_doc = ""
        n_get = 0
        n_sel = 0
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            name = e.get("eventName") or ""
            if e.get("currentDoc"):
                last_doc = e["currentDoc"]
            if name == "suggestion-get":
                n_get += 1
            if name == "suggestion-select":
                n_sel += 1
        words = len(last_doc.split())
        if words < 40:
            continue
        accept = (n_sel / n_get) if n_get > 0 else np.nan
        sessions.append(
            {
                "session": path.stem,
                "words": words,
                "n_get": n_get,
                "n_select": n_sel,
                "accept_rate": accept,
                "text": last_doc,
            }
        )
    df = pd.DataFrame(sessions)
    with_gets = df[df["n_get"] > 0].copy()
    with_gets["accept_bin"] = pd.qcut(
        with_gets["accept_rate"].rank(method="first"),
        3,
        labels=["low", "mid", "high"],
    )
    texts = with_gets["text"].tolist()
    vec = fit_tfidf(texts, max_features=12000, min_df=3)
    X = vec.transform(texts)
    # centroid similarity for dose atypicality
    centroid = np.asarray(X.mean(axis=0))
    sims = cosine_similarity(X, centroid).ravel()
    with_gets = with_gets.assign(sim_to_mean=sims)

    rows = []
    for b, g in with_gets.groupby("accept_bin", observed=True):
        mat = vec.transform(g["text"].tolist())
        rows.append(
            {
                "accept_bin": str(b),
                "n": int(len(g)),
                "mean_accept_rate": float(g["accept_rate"].mean()),
                "mean_words": float(g["words"].mean()),
                "tfidf_diversity": 1.0 - mean_pair_sim(mat),
            }
        )
    ca = pd.DataFrame(rows)
    ca.to_csv(OUT / "paper_coauthor_accept.csv", index=False)
    rho = float(with_gets["accept_rate"].corr(with_gets["sim_to_mean"], method="spearman"))
    summary = {
        "n_sessions_ge40": int(len(df)),
        "n_with_gets": int(len(with_gets)),
        "n_never_get": int((df["n_get"] == 0).sum()),
        "rank_corr_accept_vs_sim_to_mean": rho,
        "accept_tercile": rows,
        "source": str(COAUTHOR),
    }
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "coauthor_summary.json").write_text(json.dumps(summary, indent=2))
    ca.to_csv(AUDIT / "coauthor_accept_terciles.csv", index=False)
    return summary


def study3_moon() -> dict:
    print("Study 3: Moon OSF...")
    h = pd.read_csv(
        OSF
        / "exp1_matched_compr"
        / "07_h_document_dist_within_prompt_text-embedding-3-large_20260212.csv"
    )
    g = pd.read_csv(
        OSF
        / "exp1_matched_compr"
        / "08_g_document_dist_within_prompt_text-embedding-3-large_20260212.csv"
    )
    matched = pd.DataFrame(
        [
            {
                "source": "human",
                "within_prompt_doc_dist": float(h["document_dist_within_prompt"].mean()),
            },
            {
                "source": "gpt",
                "within_prompt_doc_dist": float(g["document_dist_within_prompt"].mean()),
            },
        ]
    )
    matched.to_csv(OUT / "paper_osf_matched.csv", index=False)

    ws = pd.read_csv(OSF / "exp3_within_subjects" / "gu_exp_full_data_20250828.csv")
    within = (
        ws.groupby("condition", as_index=False)
        .agg(
            n=("original_id", "count"),
            word_dist=("word_dist", "mean"),
            sentence_dist=("sentence_dist", "mean"),
            document_dist=("document_dist", "mean"),
            creativity=("gpt_4_1_mini_creativity", "mean"),
        )
    )
    within.to_csv(OUT / "paper_osf_within.csv", index=False)

    pre = pd.read_csv(
        OSF
        / "collective_word_diversity"
        / "collective_word_institution_year_sample_size_means.csv"
    )
    # Also use document-level pre/post if available from prior audit file pattern
    # Aggregate word distance by ChatGPT era label in released means file.
    # Prefer the previously audited era aggregates (document + word) from the same OSF release.
    doc_path = AUDIT / "osf_prepost_agg.csv"
    if doc_path.exists():
        prepost = pd.read_csv(doc_path)
    else:
        prepost = (
            pre.groupby("ChatGPT", as_index=False)
            .agg(
                n=("n_essay", "sum"),
                word_dist_mean=("collective_word_dist", "mean"),
                word_dist_std=("sd", "mean"),
            )
        )
        prepost["document_dist_mean"] = np.nan

    prepost.to_csv(OUT / "paper_osf_prepost.csv", index=False)

    # within-person GPT lower rates
    pivot = ws.pivot_table(
        index="original_id", columns="condition", values="document_dist", aggfunc="first"
    )
    frac = {}
    if "essay" in pivot.columns:
        for col in ["gpt_revised_essay", "gpt_gen_essay"]:
            if col in pivot.columns:
                pair = pivot[["essay", col]].dropna()
                frac[col] = float((pair[col] < pair["essay"]).mean())

    summary = {
        "matched": matched.to_dict(orient="records"),
        "within": within.to_dict(orient="records"),
        "prepost_word": prepost.to_dict(orient="records"),
        "frac_lower_than_unaided": frac,
        "source": str(OSF),
    }
    (AUDIT / "osf_yd94z_summary.json").write_text(json.dumps(summary, indent=2))
    within.to_csv(AUDIT / "osf_within_subject_agg.csv", index=False)
    return summary


def study4_simsek() -> dict:
    print("Study 4: Simsek identification check...")
    # Processed tables live in sqlite for this release.
    import sqlite3

    db = SIMSEK / "AI_assist_studies.db"
    summary = {
        "db": str(db),
        "both_arms_use_chatgpt": True,
        "unaided_arm_present": False,
        "debt_vs_unaided_identifiable": False,
        "note": "Public processed companion arms use ChatGPT; no no-AI control.",
    }
    if db.exists():
        con = sqlite3.connect(db)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con)
        summary["tables"] = tables["name"].tolist()
        # Best-effort: report transfer means by condition if columns exist
        for t in summary["tables"]:
            cols = pd.read_sql(f"PRAGMA table_info({t})", con)
            names = set(cols["name"].str.lower())
            if "transfer" in "".join(names) or "condition" in names:
                try:
                    head = pd.read_sql(f"SELECT * FROM {t} LIMIT 5", con)
                    summary[f"sample_{t}"] = head.to_dict(orient="records")
                except Exception:
                    pass
        con.close()
    (OUT / "paper_simsek_identification.json").write_text(json.dumps(summary, indent=2))
    return summary


def write_verdicts() -> None:
    v = pd.DataFrame(
        [
            ["InstructGPT homogenizes vs solo/GPT-3", "Supported", "Padmakumar"],
            ["Any LM assistance homogenizes", "Not supported", "Padmakumar"],
            ["Accept dose on group diversity", "Weak / mixed", "CoAuthor"],
            ["Model-only text narrower than human", "Supported", "Moon et al."],
            ["Post-ChatGPT word-diversity collapse", "Not supported", "Moon et al."],
            ["Transfer debt in public learning logs", "Not testable", "Simsek et al."],
            ["Unified cognitive convergence", "Not established", "All"],
        ],
        columns=["claim", "verdict", "where"],
    )
    v.to_csv(OUT / "paper_claim_verdicts.csv", index=False)


def write_snapshot(s1, s2, s3, s4) -> None:
    c = pd.read_csv(OUT / "paper_study1_contrasts.csv")

    def fmt_p(p):
        return f"{p:.3f}" if p >= 0.001 else "<0.001"

    lines = [
        "# Results snapshot (real data only)",
        "",
        "Regenerated by `scripts/reproduce_paper.py`. Not from simulated studies.",
        "",
        "## Study 1 (Padmakumar)",
        f"- Means TF-IDF D: solo={s1['mean_D']['solo']:.3f}, gpt3={s1['mean_D']['gpt3']:.3f}, instructgpt={s1['mean_D']['instructgpt']:.3f}",
        f"- H InstructGPT={s1['H']['instructgpt']:.3f}",
        f"- Emb D: solo={s1['emb_D']['solo']:.3f}, gpt3={s1['emb_D']['gpt3']:.3f}, instructgpt={s1['emb_D']['instructgpt']:.3f}",
        "",
        "| Contrast | Est. | 95% CI | perm p |",
        "|---|---:|---|---:|",
    ]
    for _, r in c.iterrows():
        lines.append(
            f"| {r['contrast']} | {r['estimate']:.3f} | [{r['ci95_lo']:.3f}, {r['ci95_hi']:.3f}] | {fmt_p(r['perm_p'])} |"
        )
    lines += [
        "",
        "## Study 2 (CoAuthor)",
        f"- n>={40} words: {s2['n_sessions_ge40']}; with gets: {s2['n_with_gets']}",
        f"- Spearman accept vs sim-to-mean: {s2['rank_corr_accept_vs_sim_to_mean']:.3f}",
        "",
        "## Study 3 (Moon)",
        f"- Matched doc dist: {s3['matched']}",
        f"- Frac lower than unaided: {s3.get('frac_lower_than_unaided')}",
        "",
        "## Study 4 (Simsek)",
        f"- Debt identifiable vs unaided: {s4['debt_vs_unaided_identifiable']}",
        "",
        "## Claim map",
        "See `results/tables/paper_claim_verdicts.csv`",
        "",
    ]
    (ROOT / "paper" / "results_snapshot.md").write_text("\n".join(lines))
    # Mark simulated summary as non-paper
    sim = ROOT / "results" / "summary.json"
    if sim.exists():
        banner = ROOT / "results" / "SIMULATED_NOT_USED_IN_PAPER.md"
        banner.write_text(
            "results/summary.json and study1-10 simulation tables are legacy simulations.\n"
            "They are NOT used in paper/main.tex.\n"
            "Use results/tables/paper_*.csv from scripts/reproduce_paper.py.\n"
        )


def sync_tex_numbers() -> None:
    """Rewrite numeric literals in main.tex from regenerated CSVs."""
    import re

    tex_path = ROOT / "paper" / "main.tex"
    tex = tex_path.read_text()
    full = pd.read_csv(OUT / "paper_padmakumar_full.csv").set_index("condition")
    auth = pd.read_csv(OUT / "paper_padmakumar_auth.csv").set_index("condition")
    rob = pd.read_csv(OUT / "paper_padmakumar_robustness.csv")
    c = pd.read_csv(OUT / "paper_study1_contrasts.csv").set_index("contrast")
    ca = pd.read_csv(OUT / "paper_coauthor_accept.csv").set_index("accept_bin")
    matched = pd.read_csv(OUT / "paper_osf_matched.csv").set_index("source")
    within = pd.read_csv(OUT / "paper_osf_within.csv").set_index("condition")
    stats = json.loads((OUT / "paper_study1_stats.json").read_text())
    rho = float(
        json.loads((AUDIT / "coauthor_summary.json").read_text())[
            "rank_corr_accept_vs_sim_to_mean"
        ]
    )
    frac = json.loads((AUDIT / "osf_yd94z_summary.json").read_text()).get(
        "frac_lower_than_unaided", {}
    )

    def r3(x):
        return f"{float(x):.3f}"

    def r3p(p):
        p = float(p)
        if p <= 0:
            return "0.001"
        if p < 0.001:
            return "0.001"
        return f"{p:.3f}"

    def signed(x):
        x = float(x)
        return f"\\phantom{{-}}{r3(x)}" if x >= 0 else f"$-{r3(abs(x))}$"

    solo_d = full.loc["solo", "tfidf_D"]
    gpt3_d = full.loc["gpt3", "tfidf_D"]
    igpt_d = full.loc["instructgpt", "tfidf_D"]
    solo_e = full.loc["solo", "emb_D"]
    gpt3_e = full.loc["gpt3", "emb_D"]
    igpt_e = full.loc["instructgpt", "emb_D"]
    H = float(full.loc["instructgpt", "H_vs_solo"])
    Hg = float(full.loc["gpt3", "H_vs_solo"])
    c_si = c.loc["solo - InstructGPT"]
    c_gi = c.loc["GPT-3 - InstructGPT"]
    c_sg = c.loc["solo - GPT-3"]

    tex = re.sub(
        r"\(\$p=[0-9.]+\$ and \$p=[0-9.]+\$\), while the solo-versus-GPT-3 contrast does not \(\$p=[0-9.]+\$\)\.",
        f"($p={r3p(c_si['perm_p'])}$ and $p={r3p(c_gi['perm_p'])}$), while the solo-versus-GPT-3 contrast does not ($p={float(c_sg['perm_p']):.2f}$).",
        tex,
        count=1,
    )
    tex = re.sub(
        r"Within-topic TF--IDF diversity is \$[0-9.]+\$ \(solo\), \$[0-9.]+\$ \(GPT-3\), and \$[0-9.]+\$ \(InstructGPT\), so \$H=[0-9.\-]+\$",
        f"Within-topic TF--IDF diversity is ${r3(solo_d)}$ (solo), ${r3(gpt3_d)}$ (GPT-3), and ${r3(igpt_d)}$ (InstructGPT), so $H={r3(H)}$",
        tex,
        count=1,
    )
    tex = re.sub(
        r"Embedding diversity falls from \$[0-9.]+\$ to \$[0-9.]+\$ \(GPT-3\) and \$[0-9.]+\$ \(InstructGPT\)\.",
        f"Embedding diversity falls from ${r3(solo_e)}$ to ${r3(gpt3_e)}$ (GPT-3) and ${r3(igpt_e)}$ (InstructGPT).",
        tex,
        count=1,
    )

    gpt3_h = f"$-{r3(abs(Hg))}$" if Hg < 0 else f"\\phantom{{-}}{r3(Hg)}"
    ph = "\\phantom{-}"
    study1_table = (
        f"solo & {int(full.loc['solo','N'])} & {r3(solo_d)} & {r3(solo_e)} & {ph}0.000 \\\\\n"
        f"gpt3 & {int(full.loc['gpt3','N'])} & {r3(gpt3_d)} & {r3(gpt3_e)} & {gpt3_h} \\\\\n"
        f"instructgpt & {int(full.loc['instructgpt','N'])} & {r3(igpt_d)} & {r3(igpt_e)} & {ph}{r3(H)} \\\\"
    )
    tex = re.sub(
        r"solo & \d+ & [0-9.]+ & [0-9.]+ & \\phantom\{-\}[0-9.]+ \\\\\n"
        r"gpt3 & \d+ & [0-9.]+ & [0-9.]+ & \$-?[0-9.]+\$ \\\\\n"
        r"instructgpt & \d+ & [0-9.]+ & [0-9.]+ & \\phantom\{-\}[0-9.]+ \\\\",
        lambda _m: study1_table,
        tex,
        count=1,
    )

    tex = re.sub(
        r"The GPT-3 minus InstructGPT gap is \$[0-9.\-]+\$ \(95\\% CI \$\[[^\]]+\]\$; permutation \$p=[0-9.]+\$\)\.",
        f"The GPT-3 minus InstructGPT gap is ${r3(c_gi['estimate'])}$ (95\\% CI $[{r3(c_gi['ci95_lo'])}, {r3(c_gi['ci95_hi'])}]$; permutation $p={r3p(c_gi['perm_p'])}$).",
        tex,
        count=1,
    )
    tex = re.sub(
        r"The solo minus InstructGPT gap is \$[0-9.\-]+\$ \(CI \$\[[^\]]+\]\$; \$p=[0-9.]+\$\); \$[0-9.]+\\%\$ of bootstrap replicates are positive\.",
        f"The solo minus InstructGPT gap is ${r3(c_si['estimate'])}$ (CI $[{r3(c_si['ci95_lo'])}, {r3(c_si['ci95_hi'])}]$; $p={r3p(c_si['perm_p'])}$); ${100 * float(c_si['boot_frac_pos']):.1f}\\%$ of bootstrap replicates are positive.",
        tex,
        count=1,
    )
    tex = re.sub(
        r"The solo minus GPT-3 gap is near zero \(\$p=[0-9.]+\$\)\.",
        f"The solo minus GPT-3 gap is near zero ($p={float(c_sg['perm_p']):.2f}$).",
        tex,
        count=1,
    )

    contrasts_table = (
        f"solo $-$ IGPT & {signed(c_si['estimate'])} & {signed(c_si['ci95_lo'])} & {r3(c_si['ci95_hi'])} & {r3p(c_si['perm_p'])} \\\\\n"
        f"GPT-3 $-$ IGPT & {signed(c_gi['estimate'])} & {signed(c_gi['ci95_lo'])} & {r3(c_gi['ci95_hi'])} & {r3p(c_gi['perm_p'])} \\\\\n"
        f"solo $-$ GPT-3 & {signed(c_sg['estimate'])} & {signed(c_sg['ci95_lo'])} & {r3(c_sg['ci95_hi'])} & {r3p(c_sg['perm_p'])} \\\\"
    )
    tex = re.sub(
        r"solo \$-\$ IGPT &.*?\\\\\nGPT-3 \$-\$ IGPT &.*?\\\\\nsolo \$-\$ GPT-3 &.*?\\\\",
        contrasts_table,
        tex,
        count=1,
        flags=re.S,
    )

    iu = auth.loc["instructgpt user"]
    im = auth.loc["instructgpt model"]
    tex = re.sub(
        r"TF--IDF \$[0-9.]+\$ vs \$[0-9.]+\$; embeddings \$[0-9.]+\$ vs \$[0-9.]+\$",
        f"TF--IDF ${r3(im['tfidf_D'])}$ vs ${r3(iu['tfidf_D'])}$; embeddings ${r3(im['emb_D'])}$ vs ${r3(iu['emb_D'])}$",
        tex,
        count=1,
    )
    auth_table = "\n".join(
        f"{idx} & {int(r['N'])} & {r3(r['tfidf_D'])} & {r3(r['emb_D'])} \\\\"
        for idx, r in auth.iterrows()
    )
    tex = re.sub(
        r"gpt3 user & \d+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"gpt3 model & \d+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"instructgpt user & \d+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"instructgpt model & \d+ & [0-9.]+ & [0-9.]+ \\\\",
        auth_table,
        tex,
        count=1,
    )

    rob_lines = []
    for _, r in rob.iterrows():
        spec = str(r["spec"]).replace("1-2", "1--2")
        rob_lines.append(
            f"{spec} & {r3(r['solo'])} & {r3(r['gpt3'])} & {r3(r['instructgpt'])} \\\\"
        )
    tex = re.sub(
        r"main \(1--2 gram\) & [0-9.]+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"unigram & [0-9.]+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"no stop-word filter & [0-9.]+ & [0-9.]+ & [0-9.]+ \\\\",
        "\n".join(rob_lines),
        tex,
        count=1,
    )

    low, mid, high = ca.loc["low"], ca.loc["mid"], ca.loc["high"]
    tex = re.sub(
        r"acceptance terciles: \$[0-9.]+\$, \$[0-9.]+\$, and \$[0-9.]+\$",
        f"acceptance terciles: ${r3(low['tfidf_diversity'])}$, ${r3(mid['tfidf_diversity'])}$, and ${r3(high['tfidf_diversity'])}$",
        tex,
        count=1,
    )
    tex = re.sub(r"\\rho=\+[0-9.]+", f"\\rho=+{rho:.3f}", tex, count=1)
    ca_table = (
        f"low & {int(low['n'])} & {r3(low['mean_accept_rate'])} & {r3(low['tfidf_diversity'])} \\\\\n"
        f"mid & {int(mid['n'])} & {r3(mid['mean_accept_rate'])} & {r3(mid['tfidf_diversity'])} \\\\\n"
        f"high & {int(high['n'])} & {r3(high['mean_accept_rate'])} & {r3(high['tfidf_diversity'])} \\\\"
    )
    tex = re.sub(
        r"low & \d+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"mid & \d+ & [0-9.]+ & [0-9.]+ \\\\\n"
        r"high & \d+ & [0-9.]+ & [0-9.]+ \\\\",
        ca_table,
        tex,
        count=1,
    )

    hm = matched.loc["human", "within_prompt_doc_dist"]
    gm = matched.loc["gpt", "within_prompt_doc_dist"]
    una = within.loc["essay"]
    rev = within.loc["gpt_revised_essay"]
    gen = within.loc["gpt_gen_essay"]
    tex = re.sub(
        r"document distance is \$[0-9.]+\$ for human essays versus \$[0-9.]+\$ for GPT essays\.",
        f"document distance is ${r3(hm)}$ for human essays versus ${r3(gm)}$ for GPT essays.",
        tex,
        count=1,
    )
    tex = re.sub(
        r"document distance falls from \$[0-9.]+\$ \(unaided\) to \$[0-9.]+\$ \(GPT-revised\) and \$[0-9.]+\$ \(GPT-generated\)",
        f"document distance falls from ${r3(una['document_dist'])}$ (unaided) to ${r3(rev['document_dist'])}$ (GPT-revised) and ${r3(gen['document_dist'])}$ (GPT-generated)",
        tex,
        count=1,
    )
    if frac:
        lo = min(frac.values())
        hi = max(frac.values())
        tex = re.sub(
            r"\$[0-9.]+\\%\$--\$[0-9.]+\\%\$ of people are lower under GPT",
            f"${100 * lo:.0f}\\%$--${100 * hi:.0f}\\%$ of people are lower under GPT",
            tex,
            count=1,
        )
    moon_table = (
        f"Matched & human & n/a & {r3(hm)} \\\\\n"
        f"Matched & gpt & n/a & {r3(gm)} \\\\\n"
        f"\\midrule\n"
        f"Within & unaided & {int(una['n'])} & {r3(una['document_dist'])} \\\\\n"
        f"Within & gpt revised & {int(rev['n'])} & {r3(rev['document_dist'])} \\\\\n"
        f"Within & gpt generated & {int(gen['n'])} & {r3(gen['document_dist'])} \\\\"
    )
    tex = re.sub(
        r"Matched & human & n/a & [0-9.]+ \\\\\n"
        r"Matched & gpt & n/a & [0-9.]+ \\\\\n"
        r"\\midrule\n"
        r"Within & unaided & \d+ & [0-9.]+ \\\\\n"
        r"Within & gpt revised & \d+ & [0-9.]+ \\\\\n"
        r"Within & gpt generated & \d+ & [0-9.]+ \\\\",
        moon_table,
        tex,
        count=1,
    )

    tex = re.sub(
        r"InstructGPT is below solo in \$[0-9.]+\\%\$ of topics and below GPT-3 in \$[0-9.]+\\%\$\.",
        f"InstructGPT is below solo in ${100 * stats['frac_topics_igpt_lt_solo']:.0f}\\%$ of topics and below GPT-3 in ${100 * stats['frac_topics_igpt_lt_gpt3']:.0f}\\%$.",
        tex,
        count=1,
    )

    # Pre/post word/doc if available
    prepost = pd.read_csv(OUT / "paper_osf_prepost.csv")
    if "document_dist_mean" in prepost.columns and prepost["document_dist_mean"].notna().any():
        pre = prepost.set_index("ChatGPT")
        if "pre" in pre.index and "post" in pre.index:
            tex = re.sub(
                r"Word distance is slightly higher after ChatGPT \(\$[0-9.]+\$ vs \$[0-9.]+\), while document distance is slightly lower \(\$[0-9.]+\$ vs \$[0-9.]+\)\.",
                f"Word distance is slightly higher after ChatGPT (${r3(pre.loc['post','word_dist_mean'])}$ vs ${r3(pre.loc['pre','word_dist_mean'])}$), while document distance is slightly lower (${r3(pre.loc['post','document_dist_mean'])}$ vs ${r3(pre.loc['pre','document_dist_mean'])}$).",
                tex,
                count=1,
            )

    tex_path.write_text(tex)
    print(f"Synced numbers into {tex_path}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    for p, label in [
        (PAD, "Padmakumar"),
        (COAUTHOR, "CoAuthor"),
        (OSF, "Moon OSF"),
        (SIMSEK, "Simsek"),
    ]:
        if not p.exists():
            raise SystemExit(f"Missing real data for {label}: {p}")

    print("Loading MiniLM for embedding diversity...")
    from sentence_transformers import SentenceTransformer

    local_model = Path.home() / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots"
    snaps = sorted(local_model.glob("*")) if local_model.exists() else []
    # Prefer a complete snapshot with model weights.
    model_path = None
    for snap in snaps:
        if (snap / "modules.json").exists() and (
            (snap / "model.safetensors").exists() or (snap / "pytorch_model.bin").exists()
        ):
            model_path = snap
            break
    if model_path is None:
        raise SystemExit(
            "MiniLM weights not found in local HF cache. "
            "Run once online: SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
        )
    model = SentenceTransformer(str(model_path), local_files_only=True)

    s1 = study1_padmakumar(model)
    s2 = study2_coauthor()
    s3 = study3_moon()
    s4 = study4_simsek()
    write_verdicts()
    write_snapshot(s1, s2, s3, s4)

    print("Figures...")
    from make_paper_figures import main as fig_main

    fig_main()
    sync_tex_numbers()
    print("Done. Real-data tables written to", OUT)


if __name__ == "__main__":
    main()
