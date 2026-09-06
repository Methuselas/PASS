---
object_id: AP_run_an_evidence_driven_playtest_revision_cycle
object_type: ap
name: Run an Evidence-Driven Playtest Revision Cycle
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
- revision
- feedback
cross_links:
- rel: supports
  target_object_id: PAT_define_the_intended_player_before_designing_for_them
- rel: supports
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: supports
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: supports
  target_object_id: PAT_classify_playtest_evidence_before_revising
- rel: supports
  target_object_id: PAT_repair_the_smallest_correct_owner_of_a_confirmed_defect
- rel: supports
  target_object_id: PAT_retest_revisions_before_treating_them_as_validated
- rel: supports
  target_object_id: PAT_keep_game_design_specification_living_and_dependency_aware
- rel: supports
  target_object_id: PAT_trace_foundational_design_changes_through_dependent_work
- rel: supports
  target_object_id: PAT_define_completion_against_a_living_game_design_document
- rel: related_to
  target_object_id: DRILL_stress_test_the_core_resolution_grammar
- rel: related_to
  target_object_id: DRILL_stress_test_mechanical_constraints_under_composition
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Run an Evidence-Driven Playtest Revision Cycle

## Objective
Run completed-game playtesting as an evidence-producing revision cycle: begin with a specific question, preserve the test conditions long enough to observe the game honestly, distinguish symptoms from diagnoses and proposed fixes, decompose mixed evidence when a test build changed several things at once, revise or revert only as strongly as the evidence supports, retest every changed behavior, and stop the current cycle when its defined completion criteria are satisfied.

## Steps / Flow
1. **Enter with a testable build and an intended behavior.** Use **Keep the Current Game Design Specification Living** to preserve the matching game version and the recoverable design specification or game design document (GDD) state that says what the tested version is supposed to do.
2. **Name the test question.** State what this session is primarily trying to learn. Avoid using “is the game fun?” as the only question when a more diagnostic question can be asked.
3. **Choose appropriate testers.** Use **Define the Intended Player Before Designing for Them** to include people representative of the intended audience, and when useful vary experience, play style, or familiarity within that audience so one regular group is not mistaken for the whole market of intended players.
4. **State the test conditions.** Tell participants what kind of play or content is being tested, what the session is focusing on, and what table or safety procedures apply.
5. **Preserve the test environment.** Use **Make the Game Operable Without Hidden Designer Knowledge** as the handoff standard: do not silently repair, reinterpret, or explain the game while it is being tested. Intervene when continuing would otherwise be impossible or inappropriate, but record the intervention as part of the evidence.
6. **Observe behavior, not only opinions.** Use **Evaluate Mechanics by the Decisions and Agency They Create** when the test question concerns a mechanic's decision points or distribution of outcome control, and record the directly observable table effects relevant to the test question: confusion, lookup time, repeated questions, skipped options, dominant strategies, stalls, unexpected solutions, pacing changes, facilitator improvisations, emotional reactions, and other concrete effects.
7. **Collect independent feedback before open discussion when practical.** Written or private responses reduce the chance that the first or loudest opinion rewrites everyone else's memory of the session.
8. **Classify the evidence before revising.** Use **Classify Playtest Evidence Before Revising** to preserve each observed symptom separately from proposed causes and fixes, then mark its evidence strength as ambiguous or plausibly group-specific, recurring, severe but uncertain, or conclusive and reproducible.
9. **Branch on evidence strength.** Continue with **Classify Playtest Evidence Before Revising**: repeat ambiguity when resolution matters, run a targeted reproduction for recurring or severe uncertainty, and allow a conclusive reproducible defect to advance without ceremonial repetition. Leave unsupported conclusions explicitly unresolved.
10. **Decompose mixed-result bundles.** Use **Classify Playtest Evidence Before Revising** when the tested build changed several things. Preserve evidence per component so rejection of the package does not automatically condemn every included change.
11. **Make an unvalidated repair or revert.** Use **Repair the Smallest Correct Owner of a Confirmed Defect** to change the smallest rule, dependency, or assumption that actually owns the failure, escalating to redesign or removal when the regulating architecture itself is wrong. Returning to a known-working prior state remains a legitimate result when the replacement has not earned its migration or regression cost. If that repair changes a foundational assumption or contract, use **Trace Foundational Design Changes Through Dependent Work** to identify the systems, content, interfaces, assumptions, and production requirements that must be reviewed before more work assumes the new foundation.
12. **Regression test the change.** Use **Retest Revisions Before Treating Them as Validated** to rerun the changed behavior and nearby dependencies, including retained components or partial reversions. A change does not become trusted merely because the diagnosis was correct or the new text sounds cleaner.
13. **Preserve history.** Keep the version and test history required by **Retest Revisions Before Treating Them as Validated**, and keep the matching specification states required by **Keep the Current Game Design Specification Living**, long enough to compare outcomes, reverse a bad repair, distinguish newly introduced regressions from older defects, and identify what each tested build was supposed to implement.
14. **Apply the completion gate.** Use **Define Design Completion Against Current-Version Fundamentals** to continue the cycle while required fundamentals remain unsupported, material unresolved defects remain, or an implemented repair has not survived retesting. When the current version's design-completion gate is satisfied and no material unresolved defect remains for this cycle, stop this revision cycle. Apply any separate release-readiness gates afterward; further ideas become later revisions, enhancements, expansions, optional modules, or next-version work rather than proof that the current design never finished.

## Notes
Completed-game playtesting is not an approval ritual. It is an empirical revision loop. Different groups can expose different truths about the same design, so uncertain findings often need reproduction; recurrence is an evidence tool rather than a ceremonial threshold. Testers are excellent sensors for what happened to them, but their repair suggestions remain design proposals. Preserve observations, diagnose causes, and version revisions so the design can learn without being whipsawed by noise.

The durable rule is: **repeat uncertainty, decompose mixed evidence, repair or revert proof, retest change.** A rejected test build can contain a useful component; package-level failure is not evidence that every bundled change failed. When a GDD or equivalent specification exists, preserve the specification state with the tested build and use its completion gates to decide when testing has done enough for the current version.
