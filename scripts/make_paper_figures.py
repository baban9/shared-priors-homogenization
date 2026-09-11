#!/usr/bin/env python3
"""Regenerate paper figures with consistent academic alignment."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "results" / "tables"
FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

COLORS = {
    "solo": "#4C72B0",
    "gpt3": "#55A868",
    "igpt": "#C44E52",
    "user": "#4C72B0",
    "model": "#8172B3",
    "accept": "#DD8452",
    "unaided": "#4C72B0",
    "rev": "#C44E52",
    "gen": "#8172B3",
}


def style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def forest_contrasts():
    stats = pd.read_csv(TAB / "paper_study1_contrasts.csv")
    # Support both column naming schemes from study1_stats.
    est_col = "estimate" if "estimate" in stats.columns else "mean"
    lo_col = "ci95_lo" if "ci95_lo" in stats.columns else "lo"
    hi_col = "ci95_hi" if "ci95_hi" in stats.columns else "hi"

    labels = ["solo - IGPT", "GPT-3 - IGPT", "solo - GPT-3"]
    # Map short labels to CSV contrast names.
    key = {
        "solo - IGPT": "solo - InstructGPT",
        "GPT-3 - IGPT": "GPT-3 - InstructGPT",
        "solo - GPT-3": "solo - GPT-3",
    }
    row = {r["contrast"]: r for _, r in stats.iterrows()}
    est = np.array([row[key[l]][est_col] for l in labels])
    lo = np.array([row[key[l]][lo_col] for l in labels])
    hi = np.array([row[key[l]][hi_col] for l in labels])
    y = np.arange(len(labels))[::-1]

    fig, ax = plt.subplots(figsize=(3.6, 2.2))
    ax.axvline(0, color="#666666", lw=0.9, zorder=0)
    ax.errorbar(
        est,
        y,
        xerr=[est - lo, hi - est],
        fmt="o",
        color="#222222",
        ecolor="#222222",
        elinewidth=1.2,
        capsize=3.0,
        markersize=5.0,
        zorder=2,
    )
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Diversity gap")
    ax.set_xlim(-0.08, 0.11)
    ax.set_ylim(-0.55, len(labels) - 0.45)
    ax.tick_params(axis="y", pad=6)
    ax.grid(axis="x", color="#E6E6E6", lw=0.7, zorder=0)
    fig.tight_layout(pad=0.15)
    fig.savefig(FIG / "fig_study1_contrasts.png", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(FIG / "fig_study1_contrasts.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def multicorpus():
    full = pd.read_csv(TAB / "paper_padmakumar_full.csv")
    auth = pd.read_csv(TAB / "paper_padmakumar_auth.csv")
    co = pd.read_csv(TAB / "paper_coauthor_accept.csv")
    within = pd.read_csv(TAB / "paper_osf_within.csv")

    d_full = {r.condition: r.tfidf_D for _, r in full.iterrows()}
    d_auth = {r.condition: r.tfidf_D for _, r in auth.iterrows()}
    d_co = {r.accept_bin: r.tfidf_diversity for _, r in co.iterrows()}
    d_w = {r.condition: r.document_dist for _, r in within.iterrows()}

    fig = plt.figure(figsize=(7.0, 5.0))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1, 1],
        height_ratios=[1, 1],
        wspace=0.32,
        hspace=0.42,
        left=0.10,
        right=0.98,
        top=0.94,
        bottom=0.10,
    )
    axes = np.array([[fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])],
                     [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]])

    # A
    ax = axes[0, 0]
    labs = ["Solo", "GPT-3", "InstructGPT"]
    vals = [d_full["solo"], d_full["gpt3"], d_full["instructgpt"]]
    cols = [COLORS["solo"], COLORS["gpt3"], COLORS["igpt"]]
    ax.bar(labs, vals, color=cols, width=0.68, edgecolor="none")
    ax.set_ylim(0.70, 0.82)
    ax.set_ylabel("Diversity D")
    ax.set_title("A. Padmakumar conditions", loc="left", fontweight="bold", pad=4)

    # B
    ax = axes[0, 1]
    labs = ["GPT-3\nuser", "GPT-3\nmodel", "IGPT\nuser", "IGPT\nmodel"]
    vals = [
        d_auth["gpt3 user"],
        d_auth["gpt3 model"],
        d_auth["instructgpt user"],
        d_auth["instructgpt model"],
    ]
    cols = [COLORS["user"], COLORS["model"], COLORS["user"], COLORS["model"]]
    ax.bar(np.arange(4), vals, color=cols, width=0.68, edgecolor="none")
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labs)
    ax.set_ylim(0.78, 0.92)
    ax.set_ylabel("Diversity D")
    ax.set_title("B. Authorship split", loc="left", fontweight="bold", pad=4)

    # C
    ax = axes[1, 0]
    labs = ["Low", "Mid", "High"]
    vals = [d_co["low"], d_co["mid"], d_co["high"]]
    ax.bar(labs, vals, color=COLORS["accept"], width=0.68, edgecolor="none")
    ax.set_ylim(0.915, 0.935)
    ax.set_yticks([0.915, 0.920, 0.925, 0.930, 0.935])
    ax.set_ylabel("Diversity D")
    ax.set_xlabel("Acceptance tercile")
    ax.set_title("C. CoAuthor acceptance", loc="left", fontweight="bold", pad=4)

    # D
    ax = axes[1, 1]
    labs = ["Unaided", "GPT revised", "GPT generated"]
    vals = [d_w["essay"], d_w["gpt_revised_essay"], d_w["gpt_gen_essay"]]
    cols = [COLORS["unaided"], COLORS["rev"], COLORS["gen"]]
    ax.bar(labs, vals, color=cols, width=0.68, edgecolor="none")
    ax.set_ylim(0.0, 0.35)
    ax.set_ylabel("Doc. distance")
    ax.set_title("D. Within-subject essays", loc="left", fontweight="bold", pad=4)

    for ax in axes.ravel():
        ax.yaxis.grid(True, color="#E8E8E8", lw=0.7, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(length=3, width=0.7)

    fig.savefig(FIG / "fig_multicorpus.png", dpi=300, bbox_inches="tight", pad_inches=0.06)
    fig.savefig(FIG / "fig_multicorpus.pdf", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def main():
    style()
    forest_contrasts()
    multicorpus()
    print(f"Wrote figures to {FIG}")


if __name__ == "__main__":
    main()
