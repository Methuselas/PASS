---
object_id: PAT_factor_repeated_resolution_structures_into_shared_procedures_and_data
object_type: pattern
name: Factor Repeated Resolution Structures into Shared Procedures and Data
library_path:
- game-design
- mechanics
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- mechanics
- refactoring
- tables
- data
cross_links:
- rel: related_to
  target_object_id: PAT_build_complete_resolution_procedures_incrementally
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Factor Repeated Resolution Structures into Shared Procedures and Data

## Pattern Rule
**IF** runtime procedures repeatedly reconstruct the same stable property, deterministic translation, dimensions, or resolution structure
**THEN** move the invariant work into a shared procedure, precomputed value, matrix, or explicit data field and leave only genuine case-specific decisions or state changes for runtime
**ELSE** keep separate live procedures when their decision structure or outputs differ enough that factoring would hide meaningful behavior.

## Do
- Compare the repeated structures side by side and identify the dimensions, branches, and outputs that are actually common.
- Extract the common matrix, sequence, or lookup family into one learned procedure when users would otherwise repeat the same logic in several places.
- Store item-specific differences as compact data, tags, categories, modifiers, parameters, or outputs when those distinctions do not require a different procedure.
- When several executions repeatedly derive the same stable property of an attack, item, actor, or effect, test whether that property should become explicit inspectable entity data consumed by the shared procedure.
- Precompute invariant arithmetic or deterministic translation into target values, tables, entity data, or another static representation when every execution would otherwise repeat the same work and doing it live creates no meaningful choice or useful feedback.
- Preserve differences that change tactics, consequences, state, timing, access, or other meaningful play rather than normalizing them away for cosmetic neatness.
- Compare representative outputs before and after consolidation to verify that the refactor did not silently erase useful distinctions.
- Permit a deep character, equipment, spell, vehicle, or adversary vocabulary to feed one shallow resolver when the distinctions live in inputs, access, state, or consequences rather than in separate resolution logic.
- Measure whether the shared structure actually reduces retrieval, interpretation, and maintenance burden instead of merely relocating it into a denser master table.

## Don't
- Keep several near-duplicate tables solely because they were authored in different subsystems.
- Collapse procedures that only look similar on the page but differ in sequencing, decisions, or consequential outputs.
- Remove weapon, armor, spell, vehicle, or other distinctions that were doing useful work merely to reduce the number of tables.
- Replace several small readable procedures with one opaque universal matrix whose translation cost exceeds what it saves.
- Treat data consolidation as proof that the surrounding complete procedures now integrate correctly.
- Recalculate the same stable property or universal constant at runtime merely because the formula is simple when the design can publish the result once.
- Promote descriptive facts into first-class statistics unless actual procedures repeatedly consume them.

## Checklist
- The repeated structures share an identifiable procedure or dimension set rather than only superficial formatting.
- Case-specific differences are represented as data or parameters only when they do not require different decision logic.
- Representative pre- and post-refactor outputs preserve distinctions that matter in play.
- The consolidated structure reduces duplicate procedure or lookup work in actual use.
- Users can still identify the local differences that affect tactics, consequences, or state.
- Complete procedures that consume the shared structure remain separately validated.
- Stable properties repeatedly consumed by real procedures have been considered for explicit entity data rather than repeated derivation.
- Universal deterministic arithmetic and translations have been checked for precomputation so users are not repeatedly performing work the design can do once.

## Notes
Many mature rulesets accumulate parallel tables that rediscover the same dimensions for weapons, armor, spells, vehicles, or other content. They also ask users to reconstruct stable properties or repeat deterministic translations that could have been resolved during design or content construction. Factoring can reduce duplication without flattening the game when the common logic is genuinely common and meaningful differences can live as data. If several actions continually rediscover the same penetration class, size category, resistance value, or other durable property, record it once when real procedures repeatedly consume it. Likewise, if every execution adds the same constant or performs the same fixed conversion, precompute that work unless doing it live creates a decision or useful feedback. The purpose is not fewer tables or more statistics as an aesthetic target. It is less repeated procedure per useful distinction.
