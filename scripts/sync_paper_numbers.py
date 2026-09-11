#!/usr/bin/env python3
"""Sync numeric claims in paper/PAPER.md from results/summary.json (sanity helper)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    summary = json.loads((ROOT / "results" / "summary.json").read_text())
    out = ROOT / "paper" / "results_snapshot.md"
    lines = [
        "# Results snapshot (auto)",
        "",
        f"Seed: `{summary['seed']}`",
        "",
        "## Study 1",
        f"- diversity w=0: `{summary['study1']['diversity_at_zero_influence']:.4f}`",
        f"- diversity w=1: `{summary['study1']['diversity_at_full_influence']:.4f}`",
        f"- max H: `{summary['study1']['max_homogenization_index']:.4f}`",
        "",
        "## Study 2",
        f"- final diversity: `{summary['study2']['final_diversity_by_weight']}`",
        f"- final competence: `{summary['study2']['final_competence_by_weight']}`",
        "",
        "## Study 3",
        f"- d: `{summary['study3']['cohens_d']:.4f}`",
        f"- p: `{summary['study3']['p_value']:.6g}`",
        f"- CI: `{summary['study3']['bootstrap_ci_95']}`",
        "",
        "## Study 4",
        f"- inflation: `{summary['study4']['mean_inflation']:.4f}`",
        f"- overconfident: `{summary['study4']['fraction_overconfident']:.3f}`",
        "",
        "## Study 5",
        f"- diversity drop: `{summary['study5']['diversity_drop_full_blend']:.4f}`",
        f"- max H: `{summary['study5']['max_homogenization_index']:.4f}`",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
