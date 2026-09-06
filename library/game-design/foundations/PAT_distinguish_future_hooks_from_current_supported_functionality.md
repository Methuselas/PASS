---
object_id: PAT_distinguish_future_hooks_from_current_supported_functionality
object_type: pattern
name: Distinguish Future Hooks from Current Supported Functionality
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
- scope
- roadmap
- capabilities
- completeness
cross_links:
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Distinguish Future Hooks from Current Supported Functionality

## Pattern Rule
**IF** the current product mentions, previews, or exposes a capability whose complete procedure belongs to future work
**THEN** either provide enough rules now to make the capability executable or label and gate it as a future hook that current characters and procedures cannot depend on
**ELSE** do not present unsupported future scope as completed current functionality.

## Do
- Identify every player-facing option, content promise, or interface that points toward a subsystem not included in the current version.
- Provide an executable current procedure when players can select, purchase, build around, or otherwise depend on that capability now.
- Gate genuinely future material so current characters and scenarios do not require unpublished rules to function.
- Label previews, roadmap hooks, setting implications, and future expansion seeds as future-facing rather than current supported capabilities.
- Check examples, character options, adversaries, equipment, and campaign procedures for hidden dependencies on deferred rules.
- When later expansion arrives, treat it as added scope rather than as retroactive proof that the earlier game was incomplete if the earlier version already delivered its promised experience.

## Don't
- Let players select a capability whose required procedure does not exist in the current product.
- Present a roadmap promise or setting mention as if it were an executable subsystem.
- Hide a deferred dependency in examples or content while claiming the base rules are complete.
- Treat all future expansion seeds as defects; a hook is safe when the current game does not depend on it.

## Checklist
- Every current player-facing capability has enough procedure to be used now.
- Deferred capabilities are clearly identifiable as future hooks.
- Current characters, content, and scenarios do not require unpublished procedures.
- Setting or roadmap references to future scope cannot be mistaken for supported current mechanics.
- Later expansion can add capability without rewriting the truth of what the earlier version already supported.

## Notes
A product can point beyond itself without pretending the future is already present. The dangerous state is not an absent subsystem; it is a current option that depends on rules the user cannot execute. Clear future hooks preserve roadmap flexibility while keeping the present version operable and honest about its scope.
