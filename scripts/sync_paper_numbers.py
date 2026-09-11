#!/usr/bin/env python3
"""Deprecated: simulation snapshot helper.

Use scripts/reproduce_paper.py and scripts/verify_paper_numbers.py instead.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    print(
        "sync_paper_numbers.py is deprecated.\n"
        "Simulated results/summary.json is NOT used in the paper.\n"
        "Run: .venv/bin/python scripts/reproduce_paper.py\n"
        "Then: .venv/bin/python scripts/verify_paper_numbers.py"
    )
    banner = ROOT / "results" / "SIMULATED_NOT_USED_IN_PAPER.md"
    if not banner.exists():
        banner.write_text(
            "results/summary.json and study1-10 simulation tables are legacy simulations.\n"
            "They are NOT used in paper/main.tex.\n"
            "Use results/tables/paper_*.csv from scripts/reproduce_paper.py.\n"
        )


if __name__ == "__main__":
    main()
