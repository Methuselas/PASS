---
object_id: PAT_classify_playtest_evidence_before_revising
object_type: pattern
name: Classify Playtest Evidence Before Revising
library_path:
- game-design
- foundations
stage_binding: 3 rough
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- playtesting
- evidence
- diagnosis
- feedback
cross_links:
- rel: related_to
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: related_to
  target_object_id: PAT_retest_revisions_before_treating_them_as_validated
- rel: related_to
  target_object_id: PAT_repair_the_smallest_correct_owner_of_a_confirmed_defect
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Classify Playtest Evidence Before Revising

## Pattern Rule
**IF** playtest observation or feedback suggests that the game may need a change
**THEN** preserve what was observed separately from proposed causes and fixes, classify the evidence by recurrence, severity, uncertainty, and reproducibility, and gather only the additional evidence needed to justify the next design decision
**ELSE** do not convert a reaction, diagnosis, or suggested repair directly into a canonical revision.

## Do
- Preserve the observed symptom in concrete terms before interpreting it: confusion, delay, skipped options, dominance, lack of choice, repeated lookup, a stalled procedure, an exploit, or another actual effect.
- Record proposed causes and fixes as hypotheses rather than as part of the observation itself, including suggestions made by the designer.
- Classify important findings as ambiguous or plausibly group-specific, recurring, severe but uncertain, or conclusive and reproducible.
- Repeat ambiguous findings with another group, scenario, or controlled condition when the question matters enough to resolve.
- Run a targeted reproduction for recurring or severe findings when the cause remains uncertain, changing as few unrelated conditions as practical.
- Allow conclusive reproducible defects to advance to repair without ceremonial repetition merely to satisfy a test-count ritual.
- When a build changed several things at once, decompose mixed evidence by component so package-level rejection does not automatically condemn every included change.
- Preserve unresolved findings explicitly when the available evidence does not support a stronger conclusion.
- Treat tester suggestions, speculative alternatives, and improvised content ideas as **design candidates**, not observations; a promising proposal can be adopted for fit without becoming evidence that the tested design already contained or communicated it.

## Don't
- Implement a tester's proposed fix merely because the reported symptom is real; accurate observation does not guarantee accurate diagnosis.
- Treat one regular group as the whole intended audience when a result may depend on group habits, experience, scenario, or table culture.
- Require arbitrary repetition for a defect already demonstrated conclusively and reproducibly.
- Treat a rejected multi-change build as proof that every individual change in the bundle failed.
- Rewrite an observation into a preferred diagnosis after discussion has begun; preserve the original evidence separately.
- Count a clever tester prediction, proposed fix, or speculative addition as proof that the original design supported that result merely because the idea is worth using.

## Checklist
- Each material finding states what was actually observed separately from any proposed cause or repair.
- Evidence strength is recorded rather than implied by confidence or volume of discussion.
- Ambiguous or severe-but-uncertain findings have a reproduction plan when resolution matters.
- Conclusive reproducible defects can be identified without requiring redundant ceremony.
- Mixed-result change bundles are decomposed before individual components are accepted or rejected.
- Unresolved evidence remains explicitly unresolved instead of being promoted into a design conclusion.
- Tester-generated ideas retained for later design work remain distinguishable from observations and diagnoses produced by the playtest.

## Notes
Playtesters are strong sensors for what happened to them and weaker authorities on why it happened or what the system should become. The designer has the same limitation when diagnosing immediately after a session. Separating observation, diagnosis, and repair preserves information that later evidence can reinterpret. Evidence strength should control the next test: repeat uncertainty, target recurring or severe ambiguity, and repair proof. That keeps the game from being whipsawed by noise without turning repetition into a ritual that delays correction of defects already demonstrated clearly.

A playtest can also generate useful authorship material. Players may speculate about an unresolved situation, propose a more interesting possibility, or improvise an interaction the draft has not defined. Those contributions can enter the designer's option pool when the underlying content is genuinely open, but adoption is an authorship decision rather than validation of the original build. Keep that creative use separate from claims about what the tested design already caused, communicated, or supported.
