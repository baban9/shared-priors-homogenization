# Holistic claim audit (no advocacy)

Scope: public microdata only (Padmakumar, CoAuthor, OSF yd94z, OSF jmz85).
Stance: confirm, qualify, or refute. Do not protect the original claim.

## Bottom line

Mechanism claim should be narrowed to: shared feedback-tuned priors can compress co-written output diversity. Broader cognitive-convergence / debt framing is a hypothesis, not a result we can defend with current public data.

### Keep
- InstructGPT co-writing homogenizes relative to solo and GPT-3 in Padmakumar (H1-H3 hold there)
- Model-only and GPT-revised text is narrower than unaided human essays (OSF yd94z)

### Drop or soften
- Do not claim any assistance homogenizes; GPT-3 counterexample matters
- Do not claim population lexical diversity collapsed post-ChatGPT; word_dist rose slightly
- Do not claim transfer debt from our public learning data; design cannot identify it
- Do not claim CoAuthor confirms homogenization; no solo arm and weak dose-response on group D

## Claim-by-claim

### C1_shared_feedback_tuned_prior_homogenizes_cowriting
- Statement: Feedback-tuned LLM co-writing reduces cross-author diversity more than solo and more than base LM assistance
- Verdict: **SUPPORTED in that corpus**
- Caveat: Single dataset, N~100/arm, 10 topics
- Caveat: InstructGPT lower than solo in 60% of topics only (not unanimous)
- Caveat: Does not prove cognitive offloading or debt; only output homogenization

### C2_any_LLM_assistance_homogenizes
- Statement: Any LLM assistance reduces diversity
- Verdict: **REFUTED / NOT SUPPORTED**
- Evidence: Padmakumar: GPT-3 diversity >= solo
- Evidence: CoAuthor: requesting suggestions associated with higher (not lower) cross-session diversity vs never-get (small never-get n)
- Evidence: CoAuthor: accept terciles nearly identical on group diversity
- Caveat: CoAuthor has no true solo control

### C3_dose_response_more_acceptance_more_homogenization
- Statement: More suggestion acceptance causes more homogenization
- Verdict: **WEAK / MIXED**
- Evidence: CoAuthor: rank corr accept_rate vs sim_to_mean = +0.178 (mild support for individual atypicality loss)
- Evidence: CoAuthor: group diversity low vs high accept almost flat (0.929 vs 0.922)

### C4_population_essays_became_less_diverse_after_ChatGPT
- Statement: College essays became lexically/semantically less diverse after ChatGPT
- Verdict: **MIXED / PARTIAL**
- Evidence: OSF GU: post ChatGPT word_dist slightly HIGHER (refutes lexical homogenization at word level)
- Evidence: OSF GU: post document_dist slightly LOWER (weak support for embedding-level homogenization)
- Evidence: Observational year confound; ChatGPT label is pre/post era not individual AI use

### C5_model_only_text_is_more_homogeneous_than_human
- Statement: Pure model generations are more homogeneous than human essays on same prompts
- Verdict: **STRONGLY SUPPORTED**
- Evidence: Matched within-prompt doc distance GPT 0.116 vs human 0.302
- Evidence: Within-subject: gpt_gen and gpt_revised lower document_dist than unaided essay
- Caveat: Shows model prior is narrow; does not by itself prove human co-writing converges cognitively

### C6_cognitive_debt_transfer_loss_after_assistance
- Statement: LLM assistance causes worse later unaided / transfer performance
- Verdict: **NOT TESTABLE with current public microdata we hold**
- Evidence: Learning companion OSF: no unaided control arm
- Evidence: Kosmyna/Barcaui cited externally only; microdata closed

### C7_cognitive_convergence_as_unified_mechanism
- Statement: Offloading onto a shared prior jointly explains homogenization AND debt
- Verdict: **NOT ESTABLISHED**
- Reason: Homogenization evidence (Padmakumar InstructGPT; pure GPT narrowness) does not identify offloading or debt. Debt not re-measured. CoAuthor and population word diversity do not cleanly confirm a general convergence story.

## Dataset notes

### Padmakumar
- solo D=0.780, gpt3 D=0.788, instructgpt D=0.740
- InstructGPT < solo in 60% of topics

### CoAuthor
- No unaided control.
- Accept vs centroid similarity rho=0.178
- Group D by accept tercile nearly flat; never-get n=33 is too small for strong claims

### OSF yd94z (admissions essays)
- Word diversity slightly up post-ChatGPT; document embedding distance slightly down.
- Pure GPT and GPT-revised texts clearly less diverse than unaided human essays.

### OSF jmz85 (ChatGPT study companion)
- Both arms are ChatGPT conditions. Cannot test debt vs solo learning.
