---
object_id: writing_adventure_modules_ap_write_introductory_adventure_module_as_runnable_apprenticeship
object_type: ap
name: Write an Introductory Adventure Module as a Runnable Apprenticeship
library_path:
  - writing
  - adventure-modules
  - instruction
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: none
tags:
  - adventure_modules
  - introductory_modules
  - onboarding
  - novice_operator
  - apprenticeship
cross_links:
  - rel: supports
    target_object_id: writing_adventure_modules_reduce_novice_decision_load_with_safe_defaults_and_explicit_optionality
  - rel: supports
    target_object_id: writing_adventure_modules_partition_information_by_reader_role_and_reveal_state
  - rel: supports
    target_object_id: writing_adventure_modules_place_novice_coaching_at_first_relevant_decision
  - rel: supports
    target_object_id: writing_adventure_modules_fade_worked_example_into_bounded_independent_extension
reference:
  source_title: "The Keep on the Borderlands"
  author: "Gary Gygax"
confidence: high
references: []
variants: []
---

# Write an Introductory Adventure Module as a Runnable Apprenticeship

## Objective
Produce an adventure module that a novice operator can prepare and run with limited prior craft knowledge while the act of using the module teaches enough judgment for the operator to personalize, extend, and eventually author adjacent material independently.

## Steps / Flow
1. **Define the novice entry state and the exit capability.** State what rules or basic procedures the module may assume, what adventure-operating judgments it must teach, and what the operator should be able to do independently by the time the supplied material is exhausted. Do not make prior scenario-writing experience an unstated prerequisite.
2. **Build a runnable baseline before opening the design space.** Activate `writing_adventure_modules_reduce_novice_decision_load_with_safe_defaults_and_explicit_optionality`. Supply the minimum preparation order, a complete starting setup, and safe defaults for decisions that would otherwise block first use. Mark enrichment and personalization as optional until the first session can already be run. **Advance gate:** a novice can identify what to read, prepare, and begin without inventing missing core material.
3. **Partition the mediated information.** Activate `writing_adventure_modules_partition_information_by_reader_role_and_reveal_state`. Keep operator truth, player-facing orientation, later reveals, and optional background distinct, and route any novice-only explanation outside player-facing prose. **Advance gate:** the operator can understand the scenario while players receive only the information their characters are entitled to use.
4. **Teach judgment where it first becomes necessary.** Activate `writing_adventure_modules_place_novice_coaching_at_first_relevant_decision`. Identify the first occurrences of the hardest recurring judgments and place concise principle-plus-example coaching beside those moments. Let later occurrences shed explanation as the operator gains familiarity. **Recovery:** if the same question still requires a special note every time, strengthen the general lesson instead of multiplying case-by-case instructions.
5. **Use the prepared scenario as a worked microcosm.** Let its locations, actors, rumors, reactions, and consequences demonstrate the kinds of relationships the operator will later need to create. Keep enough details unresolved that the operator can make ordinary decisions, but not so many that first use depends on invention. **Advance gate:** the module demonstrates at least one reusable form by operation, not merely by explanation.
6. **Fade from operation into authorship.** Activate `writing_adventure_modules_fade_worked_example_into_bounded_independent_extension`. Expose the reasoning behind one contained construction task, hand over a closely related constrained completion, then point toward broader customization or adjacent creation. Preserve the module's runnable core if the novice postpones this optional practice.
7. **Open continuation without withdrawing support all at once.** Show where the supplied scenario ends, which elements can serve as a continuing base, and what kinds of additions naturally connect to what the novice has already operated. Give a few extension vectors rather than a blank command to invent an entire world.
8. **Run the apprenticeship completion check.** A novice should be able to answer five questions from the document itself: What must I prepare? What information may I give now? What principle governs the next unfamiliar judgment? What may I safely change? What is the next bounded thing I could create myself? If any answer requires veteran intuition, return to the owning step rather than adding more general exposition at the front.

## Notes
An introductory module succeeds twice: first as an adventure that works before the operator is skilled, and second as a teaching artifact that reduces dependence on itself. Those goals conflict if instruction is front-loaded as a manual or if flexibility is expressed by leaving gaps. The flow therefore begins with a complete default, embeds coaching at use, and fades support only after the operator has a concrete example to reason from.

The AP supports `writing_adventure_modules_reduce_novice_decision_load_with_safe_defaults_and_explicit_optionality` by making the runnable baseline the first gate; supports `writing_adventure_modules_partition_information_by_reader_role_and_reveal_state` because novice-facing explanation cannot blur operator truth with player knowledge; supports `writing_adventure_modules_place_novice_coaching_at_first_relevant_decision` by scheduling instruction at live judgment points; and supports `writing_adventure_modules_fade_worked_example_into_bounded_independent_extension` by making authorship transfer the closing phase rather than an unsupported demand at the beginning.
