---
object_id: PAT_treat_optional_modules_as_removable_dependency_sets
object_type: pattern
name: Treat Optional Modules as Removable Dependency Sets
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- modules
- optionality
- dependencies
- scope
cross_links:
- rel: related_to
  target_object_id: PAT_curate_modular_rules_for_safe_onboarding
- rel: related_to
  target_object_id: PAT_keep_common_path_procedures_inside_the_declared_playable_core
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Treat Optional Modules as Removable Dependency Sets

## Pattern Rule
**IF** a subsystem, module, or rules layer is labeled optional
**THEN** verify that removing it leaves the defined base game complete and executable, including any dependencies, balance assumptions, content promises, and procedures that would otherwise rely on it
**ELSE** classify the material as part of the base game or redefine the base experience honestly.

## Do
- Remove the proposed module in a test configuration rather than deciding optionality from labels or table-of-contents placement.
- Trace rules, character options, content, adversaries, rewards, assumptions, and procedures that reference or depend on the module.
- Verify that the base game still delivers its promised experience without hidden calls into the removed material.
- Rebalance or gate content that is only valid when the module is present instead of leaving dormant dependencies in the base configuration.
- State the expansion trigger or use case that makes adding the module worthwhile when it is genuinely optional.
- Distinguish optional **presentation or convenience** from optional **capability**: a rule can be easy to omit physically while still being structurally required.

## Don't
- Call a module optional merely because it is in a separate chapter or book.
- Leave base-game character options or procedures that require the supposedly optional subsystem to function.
- Assume the base game remains balanced after removal without checking resources, opposition, rewards, and role coverage that depended on the module.
- Use "optional" to avoid admitting that the design has multiple required configurations with different completeness conditions.

## Checklist
- The module can be removed while the defined base game still executes its promised experience.
- No base-game option or procedure depends on missing module rules after removal.
- Balance and resource assumptions remain coherent without the module.
- Content that requires the module is clearly gated or packaged with it.
- The reason to add the module and the conditions under which it becomes useful are explicit.
- Optionality has been demonstrated as a dependency property rather than inferred from labeling.

## Notes
Optionality is an architectural claim. A chapter can be physically separable while the game still quietly depends on it through character options, economy, adversary assumptions, or required procedures. The reliable test is removal: if the defined base experience still works, the module is optional; if removing it breaks the promised game, the module belongs to the base configuration or the base promise needs to change.
