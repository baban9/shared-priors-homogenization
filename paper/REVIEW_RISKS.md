# Reviewer / arXiv risk checklist

## Fixed in repo packaging
- README now points to `reproduce_paper.py` as canonical
- `requirements.txt` includes `sentence-transformers`
- Simulated pipeline clearly marked unused
- Ethics statement added for secondary data
- arXiv comments page count set to 10

## Remaining rejection risks (content, not packaging)

### High (venue / reviewer)
1. **No new experiment.** This is a reanalysis note. Top venues (CHI/ICLR full papers) often want a new controlled study.
2. **H1 CI crosses 0.** Solo vs InstructGPT bootstrap 95% CI includes 0; support rests on permutation p and the GPT-3 contrast. Reviewers may call H1 weak.
3. **Only 10 topics.** Topic-level inference is underpowered; intervals stay wide.
4. **Claim map mixes statistical tests with identification arguments.** Study 4 is non-identification, not a null. Keep wording careful.

### Medium
5. **CoAuthor has no solo arm.** Dose analysis cannot prove/refute homogenization vs unaided writing.
6. **Moon era contrast is observational.** Year labels are not individual AI-use labels.
7. **Embedding diversity needs MiniLM.** Reproducers without HF cache will fail unless they download once.
8. **Dual scripts.** Prefer `reproduce_paper.py`; `study1_stats.py` alone is incomplete.

### Low (arXiv admin)
9. Endorsement may be required for new `cs.HC` submitters.
10. Upload LaTeX source, not PDF-only; real author names required (done).
11. Independent Researcher affiliation is allowed; some readers discount it.

## What would most improve acceptance odds
- One new human study with solo / base-model / instruction-tuned arms + unaided transfer
- Or shrink to a short workshop note / technical report framing
- Pre-register the three Keep/Drop/Open claims and stick to them
